#!/usr/bin/env python3
"""Read-only documentation/evidence checks (stdlib, no downloads or model runs).

Default: portable tree/link/migration/protected-artifact and saved-number checks.
--snapshot additionally checks the local pre-refactor archive without extracting it.
--external-evidence checks the optional read-only sibling research inputs.
--language-snapshot checks the separate pre-translation archive and signatures.
--self-test runs bounded positive/negative parser/invariant fixtures in a temp dir.

Markdown support: ATX headings with GitHub-style slugs, explicit HTML anchors,
inline local links, fenced blocks and pipe tables as used here. Not a full renderer.
Text canaries are regression hints, NOT proof of semantic/scientific equivalence.
"""
import argparse
from collections import Counter
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
SKIP_DIRS = {'.git', '__pycache__', '.venv', '.pytest_cache'}
LINK = re.compile(r'!?\[[^\]\n]+\]\(([^)\n]+)\)')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def files_under(root):
    return sorted(p for p in root.rglob('*') if p.is_file()
                  and not (set(p.relative_to(root).parts) & SKIP_DIRS))


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
    return len(cases) + len(rounding) + 1 + len(mutations)


def check_tree(m, errors):
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
    expected = {f['path'] for f in entries if f['disposition'] in {'unchanged', 'updated-in-place'}} | set(m['new_files'])
    actual = {p.relative_to(ROOT).as_posix() for p in files_under(ROOT)}
    if actual != expected:
        errors.append(f'tree coverage mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}')
    for dest in m['section_migrations'].values():
        err = local_target_error(ROOT, ROOT / 'README.md', dest)
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


def check_canaries(errors):
    # Intentionally redundant with manual review; token presence does not prove intent.
    cases = [
        ('scope/minimum', 'docs/project.md', ['2027-03-31', 'подлёдные', 'M1', 'M5', 'угол места', 'не подтверждены']),
        ('deadlines', 'docs/project.md', ['2026-11-15', '2027-01-15', '2027-02-01', '2027-02-15', '2027-02-28', '2027-03-10']),
        ('tensors/scaffold', 'docs/method.md', ['[N,M,2,F,T]', '[N_ch,C,F_e,T_e]', '[N_ch*F_e,T_e,C]', 'C=2*C_s', 'T_e≈T/2']),
        ('Fusion', 'docs/method.md', ['[N*F_e*T_e,M,C]', 'g_r:3→C→C', '2*C', 'Полностью закрытые', 'нулевой трёхмерный вектор']),
        ('head/loss', 'docs/method.md', ['не нормируется', 'суммы', 'atan2(b,a)', 'tau≥0', 'нулевой вектор всегда недопустим']),
        ('targets/gate', 'docs/method.md', ['X_m=D_m+R_m+N_m', 'будущего наблюдаемого', 'raw/фильтра/STFT', 'Проверка замороженного E до Fusion', 'исходным входом и необученным E']),
        ('mask contract', 'docs/method.md', ['N_good≥3', '1≤K≤N_good−2', 'во всех позициях', 'только по скрытым пригодным', 'до агрегации по датчикам и TF']),
        ('parallel stages', 'docs/method.md', ['одного checkpoint E+Fusion после этапа 2', 'разными заново', 'параллельны', 'не последовательность 3a→3b', 'с учителем с нуля']),
        ('access', 'docs/evaluation.md', ['только симуляции', 'R:', 'E1:', 'до извлечения каналов/окон', 'нельзя переводить в разработку', 'Без подгонки по азимутным меткам или настройки симулятора']),
        ('physics', 'docs/evaluation.md', ['Каждый приёмник', 'непрерывные задержки', 'ровно один раз', 'линейную свёртку', 'один скаляр', 'не лёд']),
        ('metrics/units', 'docs/evaluation.md', ['180 градусов', 'равные веса независимых единиц', 'только по допустимым', 'не число окон', 'множественности']),
        ('required controls/costs', 'docs/evaluation.md', ['MVDR/Capon', 'MUSIC', 'Bartlett', 'три парных нейросетевых seed', 'учителей/предикторы/пробы']),
        ('autumn boundary', 'docs/experiments/bench_signal_trial.md', ['одной геометрии', 'P0 — обязательное завершение', 'DEV_QA', 'не подготовлены']),
        ('evidence limitations', 'outputs/acoustic_frontend.md', ['не выполнялся', 'не показал преимущества', 'периодический сдвиг Фурье', '192 отсчёта']),
        ('RF qualification', 'outputs/jepa_evidence.md', ['40.39', '2.70', '32.42', '65.45', 'не доказана', 'после энкодера']),
    ]
    for name, rel, terms in cases:
        text = (ROOT / rel).read_text()
        for term in terms:
            if term not in text:
                errors.append(f'text canary {name}: missing {term!r} in {rel}')
    return len(cases)


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
            assert sha((ROOT / winter).read_bytes()) == m['language_migration']['winter_translated_sha256'], 'winter changed after translation'
        else:
            assert text == (ROOT / winter).read_text(), 'winter changed beyond navigation'
    return len(members)


def check_language(m, errors):
    migration = m['language_migration']
    before = {f['path']: f for f in migration['before_files']}
    assert set(before) == {p.relative_to(ROOT).as_posix() for p in files_under(ROOT)}, 'translation changed file layout'
    for rel in migration['unchanged_paths']:
        assert sha((ROOT / rel).read_bytes()) == before[rel]['sha256'], 'translation changed protected file ' + rel
    assert len(migration['translated_documents']) == len(set(migration['translated_documents']))
    for rel in migration['translated_documents']:
        text = (ROOT / rel).read_text()
        observed = formal_signature(text)
        for key, wanted in migration['formal_signatures_before'][rel].items():
            assert observed[key] == wanted, 'translation formal invariant ' + rel + ': ' + key
        for row in migration['anchor_aliases'][rel]:
            assert row['old_anchor'] in explicit_ids(text), 'missing legacy alias ' + rel + '#' + row['old_anchor']
            assert row['new_anchor'] in heading_ids(text), 'missing translated heading ' + rel + '#' + row['new_anchor']
    winter = 'docs/experiments/winter_field_protocol.md'
    assert sha((ROOT / winter).read_bytes()) == migration['winter_translated_sha256'], 'translated winter digest'
    return {'documents': len(migration['translated_documents']),
            'legacy_anchors': sum(len(rows) for rows in migration['anchor_aliases'].values()),
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
                assert set(heading_ids(text)) <= slugs((ROOT / item.name).read_text()), 'old heading lost ' + item.name
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
    canaries = check_canaries(errors)
    for label, work in [('saved numerical aggregates', lambda: check_numbers(errors)),
                        ('translation formal invariants', lambda: check_language(m, errors)),
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
    else:
        print('NOT CHECKED: optional read-only sibling evidence (use --external-evidence)')
    git_checks(m, errors)
    print('Original files/Markdown/bytes:', m['original']['file_count'], m['original']['markdown_count'], m['original']['bytes'])
    print('Current files/Markdown:', len(paths), len(markdown))
    print('Current bytes excluding this verification log:', sum(p.stat().st_size for p in paths if p.relative_to(ROOT).as_posix() != LOG))
    print('Markdown bytes:', sum(p.stat().st_size for p in markdown))
    print('CHECK: protected original files:', protected)
    print('CHECK: local Markdown links / tables / text-canary groups:', links, tables, canaries)
    print('CHECK: source-to-destination anchor mappings:', len(m['section_migrations']))
    print('NOT RUN: network URL checks, generator replay, waveform export/playback, hardware, training or scientific gate validation.')
    print('LIMIT: syntax subset and token canaries are not a full renderer or a semantic proof.')
    if errors:
        for e in errors:
            print('FAIL:', e)
        print('RESULT: FAIL', len(errors))
        return 1
    print('RESULT: PASS (only the checks explicitly requested above)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
