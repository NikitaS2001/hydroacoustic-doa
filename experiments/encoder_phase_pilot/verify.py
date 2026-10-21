#!/usr/bin/env python3
"""Post-run checks: checkpoint replay, one training replay, controls. Not independent physics."""
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as fn
import benchmark as b

OUT=Path(__file__).resolve().parent


def main():
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False
    saved=json.loads((OUT/'results.json').read_text())
    assert saved['status']=='COMPLETED' and len(saved['runs'])==9
    assert saved['source_sha256']==hashlib.sha256((OUT/'benchmark.py').read_bytes()).hexdigest()
    assert saved['lock_sha256']==hashlib.sha256((b.ROOT/'uv.lock').read_bytes()).hexdigest()
    # Check unique parent sources via full generated amplitude/phase/u hashes.
    group_hashes={}
    counts={'train':2048,'dev':256,'probe':512,'test':512}
    for name,s in b.CFG['source_seeds'].items():
        src=b.sources(counts[name],s)
        group_hashes[name]=[hashlib.sha256(np.concatenate((src[0][k],src[1][k],[src[2][k]])).tobytes()).hexdigest() for k in range(counts[name])]
    allhash=[v for rows in group_hashes.values() for v in rows]
    assert len(allhash)==len(set(allhash))
    scale=saved['scale_train_only']
    fit=b.pairs(512,8103,9103,'train',scale)
    test=b.pairs(512,8104,9204,10,scale)
    a,bb,target,tau,phase=test
    maxdiff=0.;checks=[]
    for row in saved['runs']:
        path=Path(row['weight_path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['weight_sha256']
        checkpoint=torch.load(path,map_location='cuda',weights_only=True)
        model=b.MODELS[row['architecture']]().cuda().eval()
        model.load_state_dict(checkpoint['encoder']);model.requires_grad_(False)
        f,std=b.features(model,fit[0],fit[1]);probe=b.probe_fit(f,fit[2])
        ff,_=b.features(model,a,bb);m=b.metrics(b.probe_apply(probe,ff),tau,phase)
        for key in ('median_tdoa_us','p95_tdoa_us','median_phase_rad','p95_phase_rad'):
            diff=abs(m[key]-row['results']['trained']['10'][key]);maxdiff=max(maxdiff,diff)
            assert diff<1e-5,(row['architecture'],row['seed'],key,diff)
        checks.append(dict(architecture=row['architecture'],seed=row['seed'],weight_hash='PASS',readout_reload='PASS'))
    # Independent execution of the recorded optimization loop for seed101 real model.
    x,d=b.mono(2048,8101,9101);x=x/scale;d=d/scale
    b.seed(101);enc=b.RealEncoder().cuda();dec=nn.Conv2d(16,2,1).cuda()
    opt=torch.optim.AdamW(list(enc.parameters())+list(dec.parameters()),lr=.001,weight_decay=.0001)
    indices=np.random.default_rng(101).integers(0,len(x),(300,16))
    step_count=0
    for idx in indices:
        opt.zero_grad(set_to_none=True)
        prediction=fn.interpolate(dec(enc(x[idx])),size=d.shape[-2:],mode='bilinear',align_corners=False)
        loss=fn.mse_loss(prediction,d[idx]);loss.backward();opt.step();step_count+=1
    first=next(r for r in saved['runs'] if r['architecture']=='real_conv' and r['seed']==101)
    actual=torch.load(first['weight_path'],map_location='cuda',weights_only=True)
    diffs=[float((v-actual['encoder'][k]).abs().max()) for k,v in enc.state_dict().items()]
    diff=max(diffs);assert diff<1e-5,('one-run-weight-replay',diff)
    # Magnitude-only readout retains Hann spectral/temporal interference; not a proof of no phase info.
    def mag(x):
        r=torch.sqrt(x[:,0:1].square()+x[:,1:2].square())
        return torch.cat((r,torch.zeros_like(r)),dim=1)
    f,_=b.features(None,mag(fit[0]),mag(fit[1]));probe=b.probe_fit(f,fit[2]);mag_results={}
    for k,s in enumerate(b.CFG['test_snrs']):
        aa,bb,_,tau,phase=b.pairs(512,8104,9200+k*2,s,scale)
        ff,_=b.features(None,mag(aa),mag(bb));mag_results[str(s)]=b.metrics(b.probe_apply(probe,ff),tau,phase)
    # Verify AWGN noises not identical and clean fixed-source power/sign, no shift by a peak detector.
    src=b.sources(64,8104);clean=b.wave(src,np.zeros(64))
    n0=b.noisy(clean,10,9900)-clean;n1=b.noisy(clean,10,9901)-clean
    corr=float(torch.nn.functional.cosine_similarity(n0.flatten(),n1.flatten(),dim=0))
    assert abs(corr)<.03 and not torch.equal(n0,n1)
    power_error=float((clean.square().mean(-1)-1).abs().max());assert power_error<1e-5
    result=dict(status='PASS',checkpoints=checks,maximum_metric_reload_difference=maxdiff,
                one_training_replay=dict(steps=step_count,max_weight_difference=diff),
                split_unique_parent_hashes={k:len(v) for k,v in group_hashes.items()},
                maximum_clean_power_error=power_error,receiver_noise_cosine=corr,
                magnitude_readout=mag_results,
                limitations='same generator/readout implementation; not independent physics. One optimizer replay only.')
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
