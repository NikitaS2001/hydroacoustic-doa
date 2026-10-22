#!/usr/bin/env python3
"""Read-only documentation/evidence checks (stdlib, no downloads or model runs).

Default: portable tree/links, registered protocol revisions, protected artifacts,
compact saved ULA summaries and documentation budget; no vault or archive required.
Root .agents/skills/ and skills-lock.json are tooling, not audited scientific inputs.
--snapshot checks local pre-refactor and pre-transfer archives without extracting.
--external-evidence checks optional sibling and Obsidian source/evidence hashes.
--language-snapshot checks the separate historical translation archive/signatures.
--self-test runs bounded positive/negative parser/invariant fixtures in a temp dir.

Markdown support: ATX headings with GitHub-style slugs, explicit HTML anchors,
inline local links, fenced blocks and pipe tables as used here. Not a full renderer.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'notes/refactor_manifest.json'
LOG = 'notes/refactor_verification.log'
POLICY = 'notes/policy.json'
JOURNAL = 'notes/journal.jsonl'
TASKS = 'notes/tasks.json'
SKIP_DIRS = {'.git', '__pycache__', '.venv', '.pytest_cache'}
TOOLING_DIRS = (Path('.agents/skills'),)
TOOLING_FILES = frozenset({Path('skills-lock.json')})
HEADING_NAVIGATION_REVISION = 'heading-navigation-2026-10-13'
LINK = re.compile(r'!?\[[^\]\n]+\]\(([^)\n]+)\)')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def files_under(root):
    paths = []
    for p in root.rglob('*'):
        relative = p.relative_to(root)
        if set(relative.parts) & SKIP_DIRS:
            continue
        if relative in TOOLING_FILES or any(relative.is_relative_to(d) for d in TOOLING_DIRS):
            continue
        if p.is_file():
            paths.append(p)
    return sorted(paths)


def visible_lines(text):
    """Drop fenced code for heading/link/table parsing; return fence errors."""
    result, fence = [], None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence is None:
            result.append((number, line))
    return result, ([] if fence is None else ['unclosed fenced block'])


def heading_ids(text):
    counts, used, ordered = {}, set(), []
    for _, line in visible_lines(text)[0]:
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match:
            continue
        title = re.sub(r'<[^>]+>', '', match.group(1)).lower()
        title = re.sub(r'[^\w\-\s]', '', title)
        base = re.sub(r'\s', '-', title.strip())
        n = counts.get(base, 0)
        candidate = base if n == 0 else f'{base}-{n}'
        while candidate in used:
            n += 1
            candidate = f'{base}-{n}'
        counts[base] = n + 1
        used.add(candidate)
        ordered.append(candidate)
    return ordered


def explicit_ids(text):
    # Ignore example anchors in fenced code, just as for headings/links.
    visible = '\n'.join(line for _, line in visible_lines(text)[0])
    return re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', visible)


def slugs(text):
    return set(heading_ids(text) + explicit_ids(text))


def heading_anchor_map(text):
    """Associate a standalone old HTML id with the next automatic heading slug."""
    visible = visible_lines(text)[0]
    headings = [(n, slug) for (n, _), slug in zip(
        [(n, line) for n, line in visible if re.match(r'^#{1,6}\s+', line)], heading_ids(text))]
    result = {}
    for n, line in visible:
        match = re.fullmatch(r'\s*<a\s+(?:id|name)=["\']([^"\']+)["\']\s*>\s*</a>\s*', line)
        if match:
            following = [slug for number, slug in headings if number > n]
            assert following and match[1] not in result, 'unmapped/duplicate HTML anchor'
            result[match[1]] = following[0]
    assert set(result) == set(explicit_ids(text)), 'non-standalone HTML anchor'
    return result


def navigation_target(root, source, target, maps):
    raw = target.strip().strip('<>')
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc or not parsed.fragment:
        return target
    dest = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source.resolve()
    if not dest.is_relative_to(root.resolve()):
        return target
    rel = dest.relative_to(root.resolve()).as_posix()
    replacement = maps.get(rel, {}).get(unquote(parsed.fragment))
    if replacement is None:
        return target
    rewritten = parsed._replace(fragment=replacement).geturl()
    return '<' + rewritten + '>' if target.strip().startswith('<') else rewritten


def strip_html_navigation(root, source, text, maps):
    """Change only standalone anchor lines and live internal Markdown link targets."""
    visible = {n for n, _ in visible_lines(text)[0]}
    result, skip_blank = [], False
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        if n in visible and re.fullmatch(r'\s*<a\s+(?:id|name)=["\'][^"\']+["\']\s*>\s*</a>\s*', line):
            skip_blank = True
            continue
        if skip_blank and not line.strip():
            skip_blank = False
            continue
        skip_blank = False
        if n in visible:
            def rewrite(match):
                start = match.start(1) - match.start()
                end = match.end(1) - match.start()
                return match[0][:start] + navigation_target(root, source, match[1], maps) + match[0][end:]
            line = LINK.sub(rewrite, line)
        result.append(line)
    return ''.join(result)


def historical_target(m, target):
    """Resolve archived metadata only; current Markdown must contain real targets."""
    return navigation_target(ROOT, ROOT / 'README.md', target, m.get('heading_navigation', {}).get('targets', {}))


def winter_document_sha(m):
    original = m['language_migration']['winter_translated_sha256']
    rel = 'docs/experiments/winter_field_protocol.md'
    change = m.get('heading_navigation', {}).get('documents', {}).get(rel)
    current = original
    if change is not None:
        assert change['before_sha256'] == original, 'winter navigation baseline'
        current = change['after_sha256']
    for revision in m.get('protocol_revisions', []):
        if rel not in revision['files']:
            continue
        entry = revision['files'][rel]
        # This historical revision is already applied by heading_navigation above.
        navigation = m.get('heading_navigation', {})
        if (change is not None
                and revision.get('id') == HEADING_NAVIGATION_REVISION
                and revision.get('decision_ref') == navigation.get('decision_ref')
                and navigation.get('decision_ref')
                and entry.get('before') is not None
                and entry.get('before') == entry.get('after')):
            continue
        before, after = entry.get('before_sha256'), entry.get('after_sha256')
        assert all(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)
                   for value in (before, after)), 'winter revision digest'
        assert before == current, 'winter revision chain'
        current = after
    return current


def formal_signature(text):
    """Translation regression hints, not a scientific/semantic equivalence test."""
    blocks = re.findall(r'^```([^\n]*)\n(.*?)^```\s*$', text, re.M | re.S)
    code = [body for kind, body in blocks if kind.strip() != 'mermaid']
    graphs = [body for kind, body in blocks if kind.strip() == 'mermaid']
    topology = [re.sub(r'\[[^\]]*\]|\{[^}]*\}|\|[^|]*\|',
                       lambda m: m[0][0] + m[0][-1], body) for body in graphs]
    tables = []
    for _, line in visible_lines(text)[0]:
        if line.lstrip().startswith('|'):
            # Lexical hyphens (Stage-1, DECO-50) are not negative quantities.
            line = re.sub(r'(?<=[A-Za-zА-Яа-яЁё])-+(?=\d)', '', line)
            cells = re.split(r'(?<!\\)\|', line.strip())[1:-1]
            tables.append([re.findall(r'[+−-]?\d+(?:\.\d+)*(?:[eE][+−-]?\d+)?', c) for c in cells])
    fields = {
        'display_math': re.findall(r'\\\[.*?\\\]', text, re.S),
        'code_blocks': code,
        'mermaid_topology': topology,
        'table_numbers': tables,
        'external_urls': sorted(re.findall(r'https?://[^\s<>)]*', text)),
    }
    return {key: {'sha256': sha(json.dumps(value, ensure_ascii=False).encode()),
                  'count': len(value)} for key, value in fields.items()}


def local_target_error(root, source, target):
    parsed = urlsplit(target.strip().strip('<>'))
    if parsed.scheme or parsed.netloc:
        return None
    rel = unquote(parsed.path)
    dest = (source.parent / rel).resolve() if rel else source.resolve()
    if not dest.is_relative_to(root.resolve()):
        return 'local link escapes repository (external evidence must be optional)'
    if not dest.exists():
        return f'missing path {rel}'
    anchor = unquote(parsed.fragment)
    if anchor and dest.suffix == '.md' and anchor not in slugs(dest.read_text()):
        return f'missing anchor #{anchor} in {dest.relative_to(root)}'
    return None


def inspect_markdown(root, paths):
    errors, local_count, tables = [], 0, 0
    for p in paths:
        text = p.read_text(encoding='utf-8')
        label = str(p.relative_to(root))
        if not text.endswith('\n'):
            errors.append(f'{label}: missing final newline')
        for n, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f'{label}:{n}: trailing whitespace')
            if re.match(r'^(<<<<<<<|=======|>>>>>>>)', line):
                errors.append(f'{label}:{n}: conflict marker')
        lines, fence_errors = visible_lines(text)
        errors.extend(f'{label}: {e}' for e in fence_errors)
        ids = Counter(heading_ids(text) + explicit_ids(text))
        errors.extend(f'{label}: duplicate anchor #{key}' for key, count in ids.items() if count > 1)
        width = None
        previous_number = -2
        for n, line in lines:
            if line.lstrip().startswith('|'):
                cells = re.split(r'(?<!\\)\|', line.strip())
                this_width = len(cells) - 2
                if width is None or n != previous_number + 1:
                    tables += 1
                    width = this_width
                if not line.rstrip().endswith('|') or this_width != width:
                    errors.append(f'{label}:{n}: uneven table row')
                previous_number = n
            else:
                width = None
            for target in LINK.findall(line):
                parsed = urlsplit(target.strip().strip('<>'))
                if not parsed.scheme and not parsed.netloc:
                    local_count += 1
                err = local_target_error(root, p, target)
                if err:
                    errors.append(f'{label}:{n}: {target}: {err}')
    return errors, local_count, tables


def matches_display_precision(value, displayed):
    number = Decimal(displayed.replace('−', '-'))
    quantum = Decimal(1).scaleb(number.as_tuple().exponent)
    return Decimal(str(value)).quantize(quantum) == number


def self_test():
    cases = [
        ('valid duplicate heading/escaped pipe', '# A\n[ok](b.md#repeat-1)\n| a | b |\n|---|---|\n| x\\|y | z |\n', False),
        ('missing file', '# A\n[bad](missing.md)\n', True),
        ('missing anchor', '# A\n[bad](b.md#absent)\n', True),
        ('uneven table', '# A\n| a | b |\n|---|---|\n| x |\n', True),
        ('unclosed fence', '# A\n```text\nx\n', True),
        ('trailing whitespace', '# A \n', True),
        ('conflict marker', '# A\n<<<<<<< ours\n', True),
        ('ignore fenced fake link', '# A\n```md\n[not-a-link](absent.md)\n```\n', False),
        ('repository escape', '# A\n[x](../external.md)\n', True),
        ('legacy explicit anchor', '# A\n[ok](b.md#legacy)\n', False),
        ('Russian heading', '# A\n[ok](b.md#раздел-с-фазой)\n', False),
        ('duplicate explicit anchor', '# A\n<a id="old"></a>\n<a id="old"></a>\n', True),
        ('heading anchor collision', '# A\n<a id="a"></a>\n', True),
        ('ignore fenced fake anchor', '# A\n```html\n<a id="hidden"></a>\n```\n[bad](#hidden)\n', True),
        ('ignore fenced anchor collision', '# A\n```html\n<a id="a"></a>\n```\n', False),
    ]
    with tempfile.TemporaryDirectory(prefix='hydro-doc-validator-') as d:
        root = Path(d)
        (root / 'b.md').write_text('# Repeat\n## Repeat\n<a id="legacy"></a>\n## Раздел с фазой\n')
        for label, text, should_fail in cases:
            (root / 'a.md').write_text(text)
            errors, _, _ = inspect_markdown(root, sorted(root.glob('*.md')))
            if bool(errors) != should_fail:
                raise AssertionError(f'self-test {label}: {errors}')
    with tempfile.TemporaryDirectory(prefix='hydro-scope-fixtures-') as d:
        root = Path(d)
        included = {
            'docs/science.md', '.agents/research.md', '.agents/skills-extra/probe.md',
            'experiments/skills-lock.json', 'experiments/.agents/skills/probe.md',
        }
        excluded = {
            '.agents/skills/fixture/probe.md', 'skills-lock.json',
            '.venv/probe.md', 'experiments/__pycache__/probe.pyc',
        }
        for rel in included:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture\n')
        assert {p.relative_to(root).as_posix() for p in files_under(root)} == included
        for rel in excluded:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture\n')
        assert {p.relative_to(root).as_posix() for p in files_under(root)} == included
    rounding = [(0.0788097818, '0.079', True), (9.2986e-16, '9.30e−16', True),
                (1.3598958, '1.36', True), (0.0788097818, '0.081', False)]
    for value, displayed, expected in rounding:
        assert matches_display_precision(value, displayed) == expected
    original = '# English\n\\[x=2\\]\n```python\nx = 3\n```\n```mermaid\nA[Input] --> B{Gate}\n```\n| Label | 2.5e−3 |\n|---|---|\nhttps://example.org/paper\n'
    translated = original.replace('English', 'Русский').replace('Input', 'Вход').replace('Gate', 'Допуск').replace('Label', 'Метка')
    assert formal_signature(original) == formal_signature(translated)
    mutations = [('math', translated.replace('x=2', 'x=4')),
                 ('code', translated.replace('x = 3', 'x = 4')),
                 ('topology', translated.replace('-->', '-.->')),
                 ('table', translated.replace('2.5e−3', '2.6e−3')),
                 ('URL', translated.replace('/paper', '/other'))]
    for name, changed in mutations:
        assert formal_signature(original) != formal_signature(changed), name
    wanted, actual = {'old.md', 'new.md'}, {'old.md', 'new.md'}
    assert coverage_delta(wanted, actual) == ([], [])
    assert coverage_delta(wanted, actual | {'unknown.md'}) == ([], ['unknown.md'])
    assert coverage_delta(wanted, actual - {'new.md'}) == (['new.md'], [])
    baseline = formal_signature(original)
    revised = formal_signature(translated.replace('x=2', 'x=4'))
    fixture = {'language_migration': {'formal_signatures_before': {'a.md': baseline}, 'unchanged_paths': []},
               'obsidian_transfer': {'source_notes': [{'id': 'O01'}]},
               'protocol_revisions': [{'id': 'r1', 'date': '2026-10-13', 'decision_ref': 'notes/log.md#decision',
                                      'sources': ['O01'], 'files': {'a.md': {'before': baseline, 'after': revised}}}]}
    assert protocol_signature_state(fixture)['a.md'] == revised
    assert fixture['language_migration']['formal_signatures_before']['a.md'] == baseline
    assert formal_signature(original) != protocol_signature_state(fixture)['a.md']
    for kind in ('unknown', 'protected', 'chain', 'duplicate', 'digest'):
        bad = json.loads(json.dumps(fixture))
        revision = bad['protocol_revisions'][0]
        if kind == 'unknown':
            revision['files']['absent.md'] = revision['files'].pop('a.md')
        elif kind == 'protected':
            bad['language_migration']['unchanged_paths'] = ['a.md']
        elif kind == 'chain':
            revision['files']['a.md']['before'] = revised
        elif kind == 'duplicate':
            bad['protocol_revisions'].append(revision)
        else:
            revision['files']['a.md']['after']['display_math']['sha256'] = 'bad'
        try:
            protocol_signature_state(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('protocol negative fixture ' + kind)
    explicit = json.loads(json.dumps(fixture))
    explicit['protocol_revisions'][0]['source_kind'] = 'obsidian'
    assert protocol_signature_state(explicit)['a.md'] == revised
    project = json.loads(json.dumps(fixture))
    project['protocol_revisions'][0]['source_kind'] = 'project_decision'
    project['protocol_revisions'][0]['decision_ref'] = 'notes/research_log.md#decision'
    project['protocol_revisions'][0]['sources'] = [project['protocol_revisions'][0]['decision_ref']]
    assert protocol_signature_state(project)['a.md'] == revised
    for kind in ('kind', 'missing_decision', 'source_id', 'mismatched_decision', 'other_document', 'external_decision'):
        bad = json.loads(json.dumps(fixture if kind == 'source_id' else project))
        revision = bad['protocol_revisions'][0]
        if kind == 'kind':
            revision['source_kind'] = 'unknown'
        elif kind == 'missing_decision':
            revision['decision_ref'] = ''
        elif kind == 'source_id':
            revision['sources'] = ['O99']
        elif kind == 'mismatched_decision':
            revision['sources'] = ['notes/log.md#other']
        elif kind == 'other_document':
            revision['decision_ref'] = 'README.md#decision'
            revision['sources'] = [revision['decision_ref']]
        else:
            revision['decision_ref'] = 'https://example.org/decision#external'
            revision['sources'] = [revision['decision_ref']]
        try:
            protocol_signature_state(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('provenance negative fixture ' + kind)
    winter = 'docs/experiments/winter_field_protocol.md'
    translated_sha, navigation_sha, first_sha, second_sha = [
        sha(text) for text in (b'translated', b'navigation', b'first revision', b'second revision')
    ]
    winter_fixture = {'language_migration': {'winter_translated_sha256': translated_sha}}
    winter_tests = 0
    assert winter_document_sha(winter_fixture) == translated_sha
    winter_tests += 1
    winter_fixture['heading_navigation'] = {'documents': {
        winter: {'before_sha256': translated_sha, 'after_sha256': navigation_sha}
    }}
    assert winter_document_sha(winter_fixture) == navigation_sha
    winter_tests += 1
    unrelated = {'files': {'other.md': {'before': baseline, 'after': revised}}}
    winter_fixture['protocol_revisions'] = [unrelated]
    assert winter_document_sha(winter_fixture) == navigation_sha
    winter_tests += 1
    first_revision = {'files': {winter: {
        'before': baseline, 'after': baseline,
        'before_sha256': navigation_sha, 'after_sha256': first_sha,
    }}}
    second_revision = {'files': {winter: {
        'before': baseline, 'after': baseline,
        'before_sha256': first_sha, 'after_sha256': second_sha,
    }}}
    winter_fixture['protocol_revisions'] = [first_revision]
    assert winter_document_sha(winter_fixture) == first_sha
    winter_tests += 1
    winter_fixture['protocol_revisions'] = [first_revision, unrelated, second_revision]
    assert winter_document_sha(winter_fixture) == second_sha
    winter_tests += 1
    winter_failures = [
        ('missing before', 'before_sha256', None, 'winter revision digest'),
        ('missing after', 'after_sha256', None, 'winter revision digest'),
        ('malformed before', 'before_sha256', 'bad', 'winter revision digest'),
        ('malformed after', 'after_sha256', 'A' * 64, 'winter revision digest'),
        ('non-string before', 'before_sha256', 42, 'winter revision digest'),
        ('non-string after', 'after_sha256', [], 'winter revision digest'),
        ('chain mismatch', 'before_sha256', translated_sha, 'winter revision chain'),
        ('reordered', None, None, 'winter revision chain'),
    ]
    for label, field, value, message in winter_failures:
        bad = json.loads(json.dumps(winter_fixture))
        if field is None:
            bad['protocol_revisions'].reverse()
        elif value is None:
            del bad['protocol_revisions'][0]['files'][winter][field]
        else:
            bad['protocol_revisions'][0]['files'][winter][field] = value
        try:
            winter_document_sha(bad)
        except AssertionError as error:
            assert str(error) == message, label
            winter_tests += 1
        else:
            raise AssertionError('winter negative fixture ' + label)
    legacy = json.loads(json.dumps(winter_fixture))
    navigation_decision = 'notes/research_log.md#2026-10-13-удаление-явных-html-якорей'
    legacy['heading_navigation'].update(date='2026-10-13', decision_ref=navigation_decision)
    historical_revision = {
        'id': HEADING_NAVIGATION_REVISION, 'date': '2026-10-13',
        'decision_ref': navigation_decision,
        'files': {winter: {'before': baseline, 'after': baseline}},
    }
    legacy['protocol_revisions'].insert(0, historical_revision)
    assert winter_document_sha(legacy) == second_sha
    winter_tests += 1
    with_digests = json.loads(json.dumps(legacy))
    with_digests['protocol_revisions'][0]['files'][winter].update(
        before_sha256=translated_sha, after_sha256=navigation_sha)
    assert winter_document_sha(with_digests) == second_sha
    winter_tests += 1
    for kind in ('decision mismatch', 'changed formal signature', 'no navigation',
                 'other navigation document', 'new revision same decision'):
        bad = json.loads(json.dumps(legacy))
        revision = bad['protocol_revisions'][0]
        if kind == 'decision mismatch':
            revision['decision_ref'] = 'notes/research_log.md#other'
        elif kind == 'changed formal signature':
            revision['files'][winter]['after'] = revised
        elif kind == 'no navigation':
            del bad['heading_navigation']
        elif kind == 'other navigation document':
            del bad['heading_navigation']['documents'][winter]
        else:
            revision['id'] = 'new-same-decision'
        try:
            winter_document_sha(bad)
        except AssertionError as error:
            assert str(error) == 'winter revision digest', kind
            winter_tests += 1
        else:
            raise AssertionError('winter navigation negative fixture ' + kind)
    evidence_tests = 0
    directory = ROOT / 'experiments/ula_evidence'
    if directory.is_dir():
        originals = {name: (directory / name).read_bytes() for name in ('manifest.json', 'summary.csv', 'result_audit.json')}
        with tempfile.TemporaryDirectory(prefix='hydro-evidence-fixtures-') as d:
            temporary = Path(d).resolve()
            for name, data in originals.items():
                (temporary / name).write_bytes(data)
            evidence_consistency(temporary)
            evidence_tests += 1
            for name, old, new in [('manifest.json', b'"completed_cases": 4665', b'"completed_cases": 4664'),
                                   ('result_audit.json', b'"rows": 41985', b'"rows": 41984'),
                                   ('summary.csv', b'B,chirp_32,bartlett_24_32,main,-10.0,220,0.25,', b'B,chirp_32,bartlett_24_32,main,-10.0,220,0.35,')]:
                assert old in originals[name]
                (temporary / name).write_bytes(originals[name].replace(old, new, 1))
                try:
                    evidence_consistency(temporary)
                except AssertionError:
                    evidence_tests += 1
                else:
                    raise AssertionError('evidence negative fixture ' + name)
                (temporary / name).write_bytes(originals[name])
    navigation_fixture = '# Root\n\n<a id="old"></a>\n\n## Раздел\n[go](a.md#old)\n\n<a id="second"></a>\n\n## Раздел\n'
    mapping = heading_anchor_map(navigation_fixture)
    assert mapping == {'old': 'раздел', 'second': 'раздел-1'}
    with tempfile.TemporaryDirectory(prefix='hydro-heading-fixtures-') as d:
        root = Path(d).resolve()
        source = root / 'a.md'
        rewritten = strip_html_navigation(root, source, navigation_fixture, {'a.md': mapping})
        source.write_text(rewritten)
        assert not explicit_ids(rewritten) and heading_ids(rewritten) == heading_ids(navigation_fixture)
        assert '[go](a.md#раздел)' in rewritten
        assert inspect_markdown(root, [source])[0] == []
        assert local_target_error(root, source, 'a.md#old') is not None
        assert local_target_error(root, source, 'a.md#раздел') is None
        assert navigation_target(root, source, 'https://example.org/#old', {'a.md': mapping}) == 'https://example.org/#old'
    assert historical_target({'heading_navigation': {'targets': {'a.md': mapping}}}, 'a.md#old') == 'a.md#раздел'
    journal_tests = 0
    entry = {'schema_version': 1, 'id': 'fixture', 'seq': 1, 'date': '2026-10-22',
             'type': 'decision', 'status': 'accepted', 'title': 't', 'summary': 's',
             'prev': None}
    entry['hash'] = sha(journal_canonical(entry))
    assert sha(journal_canonical(entry)) == entry['hash']
    journal_tests += 1
    changed = dict(entry, title='changed')
    assert sha(journal_canonical(changed)) != entry['hash']
    journal_tests += 1
    second = {'schema_version': 1, 'id': 'fixture-2', 'seq': 2, 'date': '2026-10-22',
              'type': 'check', 'status': 'completed', 'title': 't2', 'summary': 's2',
              'prev': entry['hash']}
    second['hash'] = sha(journal_canonical(second))
    assert second['prev'] == entry['hash']
    journal_tests += 1
    return len(cases) + len(rounding) + 1 + len(mutations) + 3 + 8 + 8 + winter_tests + evidence_tests + 5 + 2 + journal_tests


def coverage_delta(expected, actual):
    return sorted(expected - actual), sorted(actual - expected)


def read_policy():
    return json.loads((ROOT / POLICY).read_text())


def journal_canonical(entry):
    body = {k: v for k, v in entry.items() if k != 'hash'}
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def journal_records():
    path = ROOT / JOURNAL
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def journal_entry_exists(entry_id):
    return any(entry.get('id') == entry_id for entry in journal_records())


def check_policy(m, errors):
    policy = read_policy()
    assert policy.get('schema_version') == 1, 'policy schema version'
    assert policy['journal'] == JOURNAL, 'policy journal path'
    assert policy['tasks'] == TASKS, 'policy tasks path'
    assert isinstance(policy['frozen_markdown'], list) and policy['frozen_markdown'], 'frozen Markdown list'
    for rel in policy['frozen_markdown']:
        p = Path(rel)
        assert not p.is_absolute() and '..' not in p.parts and (ROOT / p).is_file(), 'missing frozen Markdown ' + rel
    recorded = policy.get('frozen_markdown_sha256', {})
    for rel in policy['frozen_markdown']:
        if rel in recorded:
            assert sha((ROOT / rel).read_bytes()) == recorded[rel], 'frozen Markdown changed ' + rel
    budget = policy['active_markdown_budget']
    assert isinstance(budget['file_count'], int) and budget['file_count'] >= 0, 'active Markdown file count'
    assert isinstance(budget['max_bytes'], int) and budget['max_bytes'] > 0, 'active Markdown budget'
    schema = policy['journal_schema']
    for key in ('required', 'types', 'statuses'):
        assert isinstance(schema[key], list) and schema[key], 'journal schema ' + key
    bundle = policy['bundle_schema']
    for key in ('required', 'statuses'):
        assert isinstance(bundle[key], list) and bundle[key], 'bundle schema ' + key
    return {'frozen': len(policy['frozen_markdown']), 'active_files': budget['file_count'], 'active_bytes': budget['max_bytes']}


def check_journal(m, errors):
    policy = read_policy()
    schema = policy['journal_schema']
    records = journal_records()
    assert records, 'journal is empty'
    seen = set()
    previous = None
    for index, entry in enumerate(records, 1):
        for key in schema['required']:
            assert key in entry, 'journal missing field ' + key
        assert entry['schema_version'] == 1, 'journal schema version'
        assert entry['seq'] == index, 'journal sequence'
        assert entry['prev'] == previous, 'journal prev chain'
        assert entry['id'] not in seen, 'duplicate journal id ' + str(entry['id'])
        assert entry['type'] in schema['types'], 'journal type ' + str(entry['type'])
        assert entry['status'] in schema['statuses'], 'journal status ' + str(entry['status'])
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', entry['date']), 'journal date ' + str(entry['date'])
        assert re.fullmatch(r'[0-9a-f]{64}', entry['hash']), 'journal hash ' + str(entry['hash'])
        assert sha(journal_canonical(entry)) == entry['hash'], 'journal hash mismatch ' + str(entry['id'])
        seen.add(entry['id'])
        previous = entry['hash']
    return {'entries': len(records), 'last': previous}


def check_tasks(m, errors):
    data = json.loads((ROOT / TASKS).read_text())
    assert data.get('schema_version') == 1, 'tasks schema version'
    tasks = data.get('tasks')
    assert isinstance(tasks, list) and tasks, 'tasks list'
    seen = set()
    for task in tasks:
        for key in ('id', 'priority', 'owner', 'status', 'acceptance'):
            assert key in task and task[key], 'task field ' + key
        assert task['id'] not in seen, 'duplicate task id ' + str(task['id'])
        seen.add(task['id'])
    return {'tasks': len(tasks)}


def revision_provenance(m, revision):
    """Distinguish imported notes from an explicitly recorded project decision."""
    kind = revision.get('source_kind', 'obsidian')
    assert kind in {'obsidian', 'project_decision'}, 'unknown revision source kind'
    decision = revision['decision_ref']
    parsed = urlsplit(decision)
    assert not parsed.scheme and not parsed.netloc and parsed.fragment, 'local revision decision required'
    path = Path(unquote(parsed.path))
    assert not path.is_absolute() and '..' not in path.parts, 'unsafe decision reference'
    if path.suffix == '.jsonl':
        assert path == Path(JOURNAL), 'unknown decision journal'
        assert journal_entry_exists(unquote(parsed.fragment)), 'unknown journal decision'
    else:
        assert path.suffix == '.md', 'unsafe decision reference'
    sources = revision['sources']
    assert isinstance(sources, list) and sources and all(isinstance(item, str) for item in sources), 'revision sources'
    assert len(sources) == len(set(sources)), 'duplicate revision sources'
    if kind == 'project_decision':
        assert path in {Path('notes/research_log.md'), Path(JOURNAL)}, 'project decision must reference a registered decision log'
        assert sources == [decision], 'project decision sources must match decision_ref'
    elif m.get('obsidian_transfer'):
        source_ids = {item['id'] for item in m['obsidian_transfer']['source_notes']}
        assert set(sources) <= source_ids, 'unknown revision source'
    return kind


def protocol_signature_state(m):
    """Replay explicit revisions; never mutate the historical translation baseline."""
    migration = m['language_migration']
    state = dict(migration['formal_signatures_before'])
    seen = set()
    protected = set(migration['unchanged_paths'])
    for revision in m.get('protocol_revisions', []):
        assert revision['id'] and revision['id'] not in seen, 'duplicate/empty protocol revision'
        seen.add(revision['id'])
        assert revision['date'] and revision['decision_ref'], 'revision provenance'
        revision_provenance(m, revision)
        assert revision['files'], 'empty protocol revision'
        for rel, change in revision['files'].items():
            assert rel in state and rel not in protected, 'unknown/protected revision path ' + rel
            assert change['before'] == state[rel], 'revision chain ' + rel
            after = change['after']
            assert set(after) == set(state[rel]), 'revision signature fields ' + rel
            for value in after.values():
                assert set(value) == {'sha256', 'count'}, 'signature schema ' + rel
                assert re.fullmatch(r'[0-9a-f]{64}', value['sha256']), 'signature digest ' + rel
                assert isinstance(value['count'], int) and value['count'] >= 0, 'signature count ' + rel
            state[rel] = after
    return state


def evidence_consistency(directory):
    """Check saved summaries, NOT regenerate scenes, fit models, or validate physics."""
    manifest = json.loads((directory / 'manifest.json').read_text())
    audit = json.loads((directory / 'result_audit.json').read_text())
    with (directory / 'summary.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    counts = {'A': 415, 'B': 1300, 'B_control': 250, 'C': 2700}
    assert manifest['stage'] == 'evaluation' and manifest['complete'] and manifest['report_complete']
    assert manifest['completed_cases'] == manifest['expected_cases'] == audit['cases'] == 4665
    assert manifest['method_rows'] == manifest['expected_method_rows'] == audit['rows'] == 41985
    assert manifest['completed_stage_counts'] == audit['stage_counts'] == counts
    assert audit['audit_pass'] is True
    assert manifest['config']['model']['d'] == .0267 and manifest['config']['model']['m'] == 8
    assert manifest['config']['main_max'] == 70 and manifest['config']['scan_max'] == 80
    totals, methods, keys = Counter(), {}, set()
    indexed = {}
    for row in rows:
        key = (row['stage'], row['signal'], row['method'], row['group'], row['snr'])
        assert key not in keys, 'duplicate summary row'
        keys.add(key)
        n = int(row['n'])
        assert n > 0 and row['stage'] in counts
        totals[row['stage']] += n
        methods.setdefault(row['stage'], set()).add(row['method'])
        for field in ('median', 'p95', 'mean'):
            value = float(row[field])
            assert math.isfinite(value) and 0 <= value <= 180, 'summary error ' + field
        for field in ('coverage', 'ambiguity', 'within_1', 'within_5', 'out_main'):
            value = float(row[field])
            assert math.isfinite(value) and 0 <= value <= 1, 'summary fraction ' + field
        if row['group'] == 'main' and row['signal'] == 'chirp_32' and row['snr']:
            indexed[(row['stage'], float(row['snr']), row['method'])] = row
    assert dict(totals) == {stage: n * 9 for stage, n in counts.items()}
    assert all(len(items) == 9 for items in methods.values())
    for stage, snr, section in [('B', -10., 'noise_minus10_main'), ('C', 20., 'reflection_snr20_main')]:
        for method, values in audit['results'][section].items():
            row = indexed[(stage, snr, method)]
            assert int(row['n']) == values['n']
            for field in ('median', 'p95', 'mean', 'coverage', 'ambiguity', 'within_1', 'within_5', 'valid_median', 'out_main'):
                assert math.isclose(float(row[field]), values[field], abs_tol=1e-12), (stage, method, field)
    return indexed


def check_transfer(m, errors):
    transfer = m.get('obsidian_transfer')
    if transfer is None:
        return None
    sources = transfer['source_notes']
    source_ids = {item['id'] for item in sources}
    assert len(source_ids) == len(sources) == 10, 'transfer source coverage'
    for item in sources:
        p = Path(item['path'])
        assert not p.is_absolute() and '..' not in p.parts, 'unsafe source note path'
        assert re.fullmatch(r'[0-9a-f]{64}', item['sha256']), 'source note digest'
    for revision in m.get('protocol_revisions', []):
        revision_provenance(m, revision)
        parsed = urlsplit(revision['decision_ref'])
        if Path(unquote(parsed.path)).suffix == '.jsonl':
            assert journal_entry_exists(unquote(parsed.fragment)), 'revision decision journal entry'
        else:
            err = local_target_error(ROOT, ROOT / 'README.md', historical_target(m, revision['decision_ref']))
            assert not err, 'revision decision reference: ' + str(err)
    imports = transfer['evidence_imports']
    assert len(imports) == 3 and len({item['local_path'] for item in imports}) == 3
    for item in imports:
        p = Path(item['local_path'])
        assert not p.is_absolute() and '..' not in p.parts, 'unsafe evidence import path'
        assert item['local_path'] in m['post_migration_additions'], 'unregistered evidence'
        data = (ROOT / p).read_bytes()
        assert len(data) == item['bytes'] and sha(data) == item['sha256'], 'import digest ' + str(p)
    for item in transfer.get('preserved_experiments', []):
        p = Path(item['path'])
        assert not p.is_absolute() and '..' not in p.parts and p.parts[0] == 'experiments'
        data = (ROOT / p).read_bytes()
        assert len(data) == item['bytes'] and sha(data) == item['sha256'], 'pre-transfer experiment changed ' + str(p)
    policy = read_policy()
    frozen = {Path(rel) for rel in policy['frozen_markdown']}
    markdown = [p for p in files_under(ROOT) if p.suffix == '.md' and p.relative_to(ROOT) not in frozen]
    budget = policy['active_markdown_budget']
    assert len(markdown) == budget['file_count'], 'new/lost active Markdown file'
    current_bytes = sum(p.stat().st_size for p in markdown)
    assert current_bytes <= budget['max_bytes'], 'active Markdown growth budget exceeded'
    indexed = evidence_consistency(ROOT / 'experiments/ula_evidence')
    text = (ROOT / 'outputs/acoustic_frontend.md').read_text()
    report_rows = [line for line in text.splitlines() if line.startswith('| B: −10 dB |') or line.startswith('| C: 20 dB |')]
    assert len(report_rows) == 4, 'ULA report table rows'
    labels = {'Bartlett 24–32': 'bartlett_24_32', 'GCC-fit 24–28': 'gcc_24_28', 'GCC-fit 24–32': 'gcc_24_32'}
    selected = set()
    for line in report_rows:
        condition, method, n, median, p95 = [cell.strip() for cell in line.strip('|').split('|')]
        stage, snr = ('B', -10.) if condition == 'B: −10 dB' else ('C', 20.)
        key = (stage, snr, labels[method])
        assert key not in selected, 'duplicate ULA report row'
        selected.add(key)
        row = indexed[key]
        assert int(n) == int(row['n'])
        assert matches_display_precision(float(row['median']), median)
        assert matches_display_precision(float(row['p95']), p95)
    assert selected == {('B', -10., 'bartlett_24_32'), ('B', -10., 'gcc_24_28'), ('B', -10., 'gcc_24_32'), ('C', 20., 'bartlett_24_32')}
    return {'sources': len(sources), 'evidence_bytes': sum(item['bytes'] for item in imports), 'report_rows': len(report_rows), 'active_markdown_files': len(markdown), 'active_markdown_bytes': current_bytes, 'limit_bytes': budget['max_bytes'], 'frozen_markdown': len(frozen)}


def check_heading_navigation(m, errors):
    navigation = m.get('heading_navigation')
    if navigation is None:
        return None
    maps = navigation['targets']
    assert sum(len(items) for items in maps.values()) == navigation['removed_count'] == 77
    for rel, replacements in maps.items():
        p = Path(rel)
        assert not p.is_absolute() and '..' not in p.parts and p.suffix == '.md'
        headings = set(heading_ids((ROOT / p).read_text()))
        assert replacements and all(target in headings for target in replacements.values()), 'navigation heading target ' + rel
    for rel, aliases in m['language_migration']['anchor_aliases'].items():
        for alias in aliases:
            assert maps[rel][alias['old_anchor']] == alias['new_anchor'], 'historical heading map ' + rel
    for p in files_under(ROOT):
        if p.suffix == '.md':
            assert not explicit_ids(p.read_text()), 'explicit HTML anchor reintroduced: ' + str(p.relative_to(ROOT))
    err = local_target_error(ROOT, ROOT / 'README.md', navigation['decision_ref'])
    assert not err, 'navigation decision reference: ' + str(err)
    winter = 'docs/experiments/winter_field_protocol.md'
    assert sha((ROOT / winter).read_bytes()) == winter_document_sha(m), 'winter changed beyond approved navigation'
    return {'removed_html_ids': navigation['removed_count'], 'updated_links': navigation['links_rewritten'], 'current_explicit_ids': 0}


def check_heading_snapshot(m, errors):
    navigation = m.get('heading_navigation')
    if navigation is None:
        return None
    backup = navigation['backup']
    path = ROOT / backup['archive_path']
    inventory_path = ROOT / backup['inventory_path']
    if not path.is_file() or not inventory_path.is_file():
        errors.append('BLOCKED: local pre-anchor-removal snapshot unavailable')
        return 0
    assert sha(path.read_bytes()) == backup['archive_sha256']
    assert sha(inventory_path.read_bytes()) == backup['inventory_sha256']
    inventory = json.loads(inventory_path.read_text())
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        assert len(members) == len(inventory['files'])
        assert all(item.isfile() and not Path(item.name).is_absolute() and '..' not in Path(item.name).parts for item in members)
        assert {item.name for item in members} == {row['path'] for row in inventory['files']}
        for row in inventory['files']:
            data = archive.extractfile(row['path']).read()
            assert len(data) == row['bytes'] and sha(data) == row['sha256']
        for rel, mapping in navigation['targets'].items():
            assert heading_anchor_map(archive.extractfile(rel).read().decode()) == mapping
        for rel, change in navigation['documents'].items():
            original = archive.extractfile(rel).read().decode()
            assert sha(original.encode()) == change['before_sha256']
            expected = strip_html_navigation(ROOT, ROOT / rel, original, navigation['targets'])
            current = (ROOT / rel).read_text()
            if rel not in {'README.md', 'AGENTS.md', 'notes/research_log.md'}:
                assert current == expected, 'content changed beyond navigation: ' + rel
    return {'snapshot_files': len(inventory['files']), 'anchor_maps': sum(map(len, navigation['targets'].values()))}


def check_transfer_snapshot(m, errors):
    transfer = m.get('obsidian_transfer')
    if transfer is None:
        return None
    backup = transfer['backup']
    inventory_path = Path(backup['inventory_path'])
    if not inventory_path.is_file():
        errors.append('BLOCKED: transfer recovery inventory unavailable: ' + str(inventory_path))
        return 0
    assert sha(inventory_path.read_bytes()) == backup['inventory_sha256'], 'transfer inventory digest'
    inventory = json.loads(inventory_path.read_text())
    for field, rows in [('worktree_archive', inventory['files']), ('source_archive', inventory['sources'])]:
        path = Path(backup[field]['path'])
        if not path.is_file():
            errors.append('BLOCKED: transfer recovery archive unavailable: ' + str(path))
            continue
        assert sha(path.read_bytes()) == backup[field]['sha256'], 'transfer archive digest'
        with tarfile.open(path, 'r:gz') as archive:
            members = archive.getmembers()
            assert all(item.isfile() and not Path(item.name).is_absolute() and '..' not in Path(item.name).parts for item in members)
            assert len(members) == len(rows) and {item.name for item in members} == {row['path'] for row in rows}
            for row in rows:
                data = archive.extractfile(row['path']).read()
                assert len(data) == row['bytes'] and sha(data) == row['sha256'], 'transfer archived file ' + row['path']
    return {'worktree_files': len(inventory['files']), 'source_notes': len(inventory['sources'])}


def check_transfer_external(m, errors):
    transfer = m.get('obsidian_transfer')
    if transfer is None:
        return
    source_root = Path(transfer['source_root'])
    targets = [(source_root / row['path'], row['sha256']) for row in transfer['source_notes']]
    targets += [(Path(row['source_path']), row['sha256']) for row in transfer['evidence_imports']]
    targets.append((Path(transfer['primary_cases']['path']), transfer['primary_cases']['sha256']))
    for path, digest in targets:
        if not path.is_file() or sha(path.read_bytes()) != digest:
            errors.append('BLOCKED/CHANGED: transfer external evidence ' + str(path))
    print('CHECK: optional transfer source/evidence hashes:', len(targets))


def check_tree(m, errors):
    if m.get('schema_version') not in (1, 2):
        errors.append('unsupported manifest schema version')
    if m.get('protocol_revisions') and m.get('schema_version') != 2:
        errors.append('protocol revisions require manifest schema version 2')
    entries = m['files']
    originals = [f['path'] for f in entries]
    if len(originals) != len(set(originals)):
        errors.append('duplicate original manifest paths')
    if len(entries) != m['original']['file_count']:
        errors.append('manifest original count mismatch')
    if sum(f['bytes'] for f in entries) != m['original']['bytes']:
        errors.append('manifest original byte count mismatch')
    if sum(p.endswith('.md') for p in originals) != m['original']['markdown_count']:
        errors.append('manifest original Markdown count mismatch')
    protected = 0
    allowed_statuses = {'unchanged', 'updated-in-place', 'consolidated', 'retired-historical'}
    for f in entries:
        rel = Path(f['path'])
        if rel.is_absolute() or '..' in rel.parts:
            errors.append(f'unsafe manifest path: {rel}')
            continue
        p = ROOT / rel
        state = f['disposition']
        if state not in allowed_statuses:
            errors.append(f'unknown disposition: {rel}')
        if state == 'unchanged':
            protected += 1
            if not p.is_file() or sha(p.read_bytes()) != f['sha256']:
                errors.append(f'protected artifact changed/missing: {rel}')
        elif state == 'updated-in-place' and not p.is_file():
            errors.append(f'updated file missing: {rel}')
        elif state in {'consolidated', 'retired-historical'} and p.exists():
            errors.append(f'retired original still exists: {rel}')
        for dest in f['destinations']:
            if not (ROOT / dest).is_file():
                errors.append(f'missing migration destination: {dest}')
    for rel in m['new_files']:
        if not (ROOT / rel).is_file():
            errors.append(f'missing new artifact: {rel}')
    additions = m.get('post_migration_additions', [])
    if len(additions) != len(set(additions)) or set(additions) & (set(originals) | set(m['new_files'])):
        errors.append('invalid/duplicate post-migration addition paths')
    for rel in additions:
        p = Path(rel)
        if p.is_absolute() or '..' in p.parts or not (ROOT / p).is_file():
            errors.append(f'unsafe/missing post-migration addition: {rel}')
    expected = ({f['path'] for f in entries if f['disposition'] in {'unchanged', 'updated-in-place'}}
                | set(m['new_files']) | set(additions))
    actual = {p.relative_to(ROOT).as_posix() for p in files_under(ROOT)}
    missing, extra = coverage_delta(expected, actual)
    if missing or extra:
        errors.append(f'tree coverage mismatch: missing={missing}, extra={extra}')
    for dest in m['section_migrations'].values():
        err = local_target_error(ROOT, ROOT / 'README.md', historical_target(m, dest))
        if err:
            errors.append(f'migration anchor {dest}: {err}')
    # Old names are allowed in explicitly historical logs/maps, not active navigation.
    retired = [f['path'] for f in entries if f['disposition'] in {'consolidated', 'retired-historical'}]
    active = [ROOT / 'README.md', ROOT / 'AGENTS.md']
    active += list((ROOT / 'docs').rglob('*.md'))
    active += [ROOT / 'outputs/jepa_evidence.md', ROOT / 'outputs/acoustic_frontend.md']
    for p in active:
        for old in retired:
            if old in p.read_text():
                errors.append(f'active retired-path mention: {p.relative_to(ROOT)} -> {old}')
    bench = (ROOT / 'docs/experiments/bench_signal_trial.md').read_text()
    if LINK.search(bench):
        errors.append('standalone autumn instruction gained a reading dependency')
    return protected


def check_numbers(errors):
    j = json.loads((ROOT / 'experiments/synthetic_stft_tdoa.json').read_text())
    a = j['assumptions']
    assert len(j['cases']) == 6 and a['n_channels'] == 8
    pairs = [(i, i + 1) for i in range(7)] + [(0, 7)]
    clean = []
    for c in j['cases']:
        for hop in (64, 128):
            v = c['hops'][str(hop)]
            truths = [a['pitch_m'] * (i - k) * c['u'] / a['sound_speed_mps_assumed'] * 1e6 for i, k in pairs]
            assert all(math.isclose(t, q, abs_tol=1e-12) for t, q in zip(truths, v['true_tdoa_us']))
            raw = max(abs(p['lag_us'] - t) for p, t in zip(c['raw'], truths))
            tf = max(abs(p['lag_us'] - t) for p, t in zip(v['tf'], truths))
            assert math.isclose(raw, v['max_abs_raw_truth_us'], abs_tol=1e-12)
            assert math.isclose(tf, v['max_abs_tf_truth_us'], abs_tol=1e-12)
            phase_delta = v['stft_phase_pair_01_at_12k_rad'] - v['expected_phase_pair_01_rad']
            phase_error = abs(math.atan2(math.sin(phase_delta), math.cos(phase_delta)))
            assert math.isclose(phase_error, v['circular_phase_error_rad'], abs_tol=1e-12)
            assert v['frames'] == 1 + (a['record_samples'] - a['window_samples']) // hop
            assert math.isclose(v['coverage_fraction'], 12287 / 12288, abs_tol=1e-12)
            if c['condition'] == 'direct_only':
                clean.append(v)
    expected_checks = {
        'inverse_rms_ideal_under_1e-10': all(v['inverse_relative_rms'] < 1e-10 for v in clean),
        'raw_and_tf_tdoa_ideal_within_5us': all(max(v['max_abs_raw_truth_us'], v['max_abs_tf_truth_us']) <= 5 for v in clean),
        'tf_phase_ideal_within_0p2rad': all(v['circular_phase_error_rad'] <= .2 for v in clean),
    }
    assert j['checks'] == expected_checks and all(expected_checks.values())
    text = (ROOT / 'outputs/acoustic_frontend.md').read_text()
    rows = [l for l in text.splitlines() if l.startswith('| Только прямой путь |') or l.startswith('| Эхо 2 мс + шум |')]
    assert len(rows) == 4
    for row in rows:
        cells = [c.strip() for c in row.strip('|').split('|')]
        condition = 'direct_only' if cells[0] == 'Только прямой путь' else 'echo+white_noise'
        hop, frames = [int(c.strip()) for c in cells[1].split('/')]
        values = [c['hops'][str(hop)] for c in j['cases'] if c['condition'] == condition]
        assert all(v['frames'] == frames for v in values)
        for col, key in zip(cells[2:], ['inverse_relative_rms', 'max_abs_tf_truth_us', 'circular_phase_error_rad']):
            assert matches_display_precision(max(v[key] for v in values), col), (condition, hop, key)
    stress = (ROOT / 'experiments/synthetic_stft_stress_check.log').read_text()
    assert stress.count('max TF error across pairs us 7.057') == 2 and '7.057' in text
    assert 8 * 96000 * 4 * 3600 == 11059200000
    assert 8 * 96000 * 4 * 3600 * 2 == 22118400000
    assert math.isclose(.027 * 7, .189) and 96000 / 2 == 48000
    assert math.isclose(.027 / 1500 * 1e6, 18)
    assert round(1500 / (2 * .027) / 1000, 2) == 27.78
    assert .002 * 96000 == 192 and 1 / 16000 * 1e6 == 62.5
    return len(rows)


def check_snapshot(m, errors):
    path = Path(m['snapshot']['archive_path'])
    if not path.is_file():
        errors.append(f'BLOCKED: local snapshot unavailable: {path}')
        return 0
    assert sha(path.read_bytes()) == m['snapshot']['sha256'], 'snapshot digest'
    for name, digest in m['snapshot']['sidecars'].items():
        assert sha((path.parent / name).read_bytes()) == digest, 'snapshot sidecar ' + name
    with tarfile.open(path, 'r:gz') as archive:
        members = {}
        for member in archive.getmembers():
            name = member.name.removeprefix('./')
            p = Path(name)
            assert not p.is_absolute() and '..' not in p.parts, 'unsafe tar path'
            assert member.isfile(), 'unexpected non-file tar member'
            assert name not in members, 'duplicate tar member'
            members[name] = member
        assert set(members) == {f['path'] for f in m['files']}, 'snapshot file coverage'
        for f in m['files']:
            data = archive.extractfile(members[f['path']]).read()
            assert len(data) == f['bytes'] and sha(data) == f['sha256'], f['path']
        for origin in m['section_migrations']:
            rel, anchor = origin.split('#', 1)
            assert anchor in slugs(archive.extractfile(members[rel]).read().decode()), 'source anchor ' + origin
        winter = 'docs/experiments/winter_field_protocol.md'
        text = archive.extractfile(members[winter]).read().decode()
        for old, new in m['winter_navigation_replacements']:
            assert text.count(old) == 1, 'winter replacement no longer unique'
            text = text.replace(old, new)
        if 'language_migration' in m:
            before = {f['path']: f for f in m['language_migration']['before_files']}
            assert sha(text.encode()) == before[winter]['sha256'], 'winter refactor-to-translation chain'
            assert sha((ROOT / winter).read_bytes()) == winter_document_sha(m), 'winter changed beyond registered navigation'
        else:
            assert text == (ROOT / winter).read_text(), 'winter changed beyond navigation'
    return len(members)


def check_language(m, errors):
    migration = m['language_migration']
    before = {f['path']: f for f in migration['before_files']}
    actual = {p.relative_to(ROOT).as_posix() for p in files_under(ROOT)}
    missing, extra = coverage_delta(set(before) | set(m.get('post_migration_additions', [])), actual)
    assert not missing and not extra, f'baseline + registered additions changed: missing={missing}, extra={extra}'
    for rel in migration['unchanged_paths']:
        assert sha((ROOT / rel).read_bytes()) == before[rel]['sha256'], 'translation changed protected file ' + rel
    assert len(migration['translated_documents']) == len(set(migration['translated_documents']))
    current_signatures = protocol_signature_state(m)
    for rel in migration['translated_documents']:
        text = (ROOT / rel).read_text()
        observed = formal_signature(text)
        for key, wanted in current_signatures[rel].items():
            assert observed[key] == wanted, 'translation formal invariant ' + rel + ': ' + key
        for row in migration['anchor_aliases'][rel]:
            if m.get('heading_navigation') is None:
                assert row['old_anchor'] in explicit_ids(text), 'missing legacy alias ' + rel + '#' + row['old_anchor']
            assert row['new_anchor'] in heading_ids(text), 'missing translated heading ' + rel + '#' + row['new_anchor']
    winter = 'docs/experiments/winter_field_protocol.md'
    assert sha((ROOT / winter).read_bytes()) == winter_document_sha(m), 'registered winter digest'
    return {'documents': len(migration['translated_documents']),
            ('historical_heading_records' if m.get('heading_navigation') else 'legacy_anchors'): sum(len(rows) for rows in migration['anchor_aliases'].values()),
            'byte_preserved_files': len(migration['unchanged_paths'])}


def check_language_snapshot(m, errors):
    migration = m['language_migration']
    snapshot = migration['snapshot']
    path = Path(snapshot['archive_path'])
    if not path.is_file():
        errors.append(f'BLOCKED: pre-translation snapshot unavailable: {path}')
        return 0
    assert sha(path.read_bytes()) == snapshot['sha256'], 'language archive digest'
    for name, digest in snapshot['sidecars'].items():
        assert sha((path.parent / name).read_bytes()) == digest, 'language sidecar ' + name
    expected = {f['path']: f for f in migration['before_files']}
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        assert len(members) == len(expected), 'language archive member count'
        assert {item.name for item in members} == set(expected), 'language archive member coverage'
        for item in members:
            rel = Path(item.name)
            assert item.isfile() and not rel.is_absolute() and '..' not in rel.parts, 'unsafe language tar entry'
            data = archive.extractfile(item).read()
            wanted = expected[item.name]
            assert sha(data) == wanted['sha256'] and len(data) == wanted['bytes'], item.name
            if item.name in migration['translated_documents']:
                text = data.decode()
                assert formal_signature(text) == migration['formal_signatures_before'][item.name], 'baseline signature ' + item.name
                resolved = {unquote(urlsplit(historical_target(m, item.name + '#' + anchor)).fragment) for anchor in heading_ids(text)}
                assert resolved <= slugs((ROOT / item.name).read_text()), 'historical heading destination lost ' + item.name
    return len(members)


def git_checks(m, errors):
    if not (ROOT / '.git').exists():
        print('NOT CHECKED: Git metadata unavailable in this copy')
        return
    for args in (['diff', '--check'], ['diff', '--cached', '--check']):
        p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
        if p.returncode:
            errors.append('git ' + ' '.join(args) + ': ' + p.stdout + p.stderr)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    index = subprocess.check_output(['git', 'diff', '--cached', '--binary'], cwd=ROOT)
    print('Git HEAD:', head)
    # Historical identity is a refactor check, not a prohibition on future authorized commits.
    print('Original HEAD unchanged:', head == m['original']['head'])
    print('Original staged diff unchanged:', sha(index) == m['original']['cached_diff_sha256'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--snapshot', action='store_true')
    parser.add_argument('--external-evidence', action='store_true')
    parser.add_argument('--language-snapshot', action='store_true')
    args = parser.parse_args()
    errors = []
    m = json.loads((ROOT / MANIFEST).read_text())
    if args.self_test:
        print('PASS: parser/rounding/formal-invariant fixtures:', self_test())
    protected = check_tree(m, errors)
    paths = files_under(ROOT)
    markdown = [p for p in paths if p.suffix == '.md']
    md_errors, links, tables = inspect_markdown(ROOT, markdown)
    errors.extend(md_errors)
    for label, work in [('saved numerical aggregates', lambda: check_numbers(errors)),
                        ('current protocol / translation invariants', lambda: check_language(m, errors)),
                        ('policy / active Markdown budget', lambda: check_policy(m, errors)),
                        ('journal hash chain', lambda: check_journal(m, errors)),
                        ('task registry', lambda: check_tasks(m, errors)),
                        ('Obsidian transfer / compact ULA evidence', lambda: check_transfer(m, errors)),
                        ('automatic heading navigation', lambda: check_heading_navigation(m, errors)),
                        ('pre-anchor-removal snapshot', lambda: check_heading_snapshot(m, errors) if args.snapshot else None),
                        ('transfer recovery archives', lambda: check_transfer_snapshot(m, errors) if args.snapshot else None),
                        ('snapshot archive/mapping/navigation chain', lambda: check_snapshot(m, errors) if args.snapshot else None),
                        ('pre-translation snapshot', lambda: check_language_snapshot(m, errors) if args.language_snapshot else None)]:
        try:
            result = work()
            if result is not None:
                print(f'CHECK: {label}: {result}')
        except (AssertionError, OSError, ValueError, KeyError) as e:
            errors.append(f'{label}: {type(e).__name__}: {e}')
    if not args.snapshot:
        print('NOT CHECKED: local snapshot recovery (use --snapshot)')
    if not args.language_snapshot:
        print('NOT CHECKED: pre-translation archive recovery/baselines (use --language-snapshot)')
    if args.external_evidence:
        for e in m['external_evidence']:
            p = ROOT / e['path']
            if not p.is_file() or sha(p.read_bytes()) != e['sha256']:
                errors.append('BLOCKED/CHANGED: external evidence ' + e['path'])
        print('CHECK: optional sibling evidence hashes:', len(m['external_evidence']))
        check_transfer_external(m, errors)
    else:
        print('NOT CHECKED: optional read-only sibling evidence (use --external-evidence)')
    git_checks(m, errors)
    print('Original files/Markdown/bytes:', m['original']['file_count'], m['original']['markdown_count'], m['original']['bytes'])
    print('Current files/Markdown:', len(paths), len(markdown))
    print('Current bytes excluding this verification log:', sum(p.stat().st_size for p in paths if p.relative_to(ROOT).as_posix() != LOG))
    print('Markdown bytes:', sum(p.stat().st_size for p in markdown))
    print('CHECK: protected original files:', protected)
    print('CHECK: local Markdown links / tables:', links, tables)
    print('CHECK: source-to-destination anchor mappings:', len(m['section_migrations']))
    print('NOT RUN: network URL checks, generator replay, waveform export/playback, hardware, training or scientific gate validation.')
    print('LIMIT: syntax checks are not a full renderer or a semantic proof.')
    if errors:
        for e in errors:
            print('FAIL:', e)
        print('RESULT: FAIL', len(errors))
        return 1
    print('RESULT: PASS (only the checks explicitly requested above)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
