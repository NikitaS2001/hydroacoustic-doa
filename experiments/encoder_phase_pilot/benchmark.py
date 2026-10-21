#!/usr/bin/env python3
"""Bounded mono reconstruction benchmark; NOT JEPA or a physical E gate."""
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import numpy as np
import torch
from torch import nn
from torch.nn import functional as fn

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
WEIGHTS = Path.home() / '.cache/hydroacoustic-doa/encoder-phase-pilot-20261002'
CFG = dict(fs=96000, nfft=256, hop=64, length=2048, low_bin=11, high_bin=53,
           width=16, train_sources=2048, dev_sources=256, probe_sources=512,
           test_sources=512, steps=300, batch=16, lr=.001, weight_decay=.0001,
           ridge=.01, seed_runs=[101,202,303], d=.027, c=1500., umax=.8,
           source_seeds=dict(train=8101,dev=8102,probe=8103,test=8104),
           test_snrs=['clean',0,10,20], precision='float32', phase_bin=32,
           objective='clean STFT reconstruction; not EMA/JEPA', norm_floor=1e-6)
DEVICE = 'cuda'


def seed(s):
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


class ComplexConv(nn.Module):
    def __init__(self, a, b, kernel=3, stride=(1,1)):
        super().__init__()
        self.r = nn.Conv2d(a,b,kernel,stride=stride,padding=kernel//2,bias=False)
        self.i = nn.Conv2d(a,b,kernel,stride=stride,padding=kernel//2,bias=False)
    def forward(self,z):
        r,i=z.chunk(2,dim=1)
        return torch.cat((self.r(r)-self.i(i),self.r(i)+self.i(r)),dim=1)


def radial(z):
    r,i=z.chunk(2,dim=1)
    # smooth radial gain, no learned phase or raw-input bypass
    gain=torch.sigmoid(torch.sqrt(r.square()+i.square()+1e-8))
    return torch.cat((r*gain,i*gain),dim=1)


class ComplexEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.stem=ComplexConv(1,8,stride=(1,2))
        self.layers=nn.ModuleList([ComplexConv(8,8),ComplexConv(8,8)])
    def forward(self,x):
        x=radial(self.stem(x))
        for layer in self.layers:x=radial(layer(x))
        return x


class RealEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.net=nn.Sequential(nn.Conv2d(2,16,3,stride=(1,2),padding=1),nn.GELU(),
                               nn.Conv2d(16,16,3,padding=1),nn.GELU(),
                               nn.Conv2d(16,16,3,padding=1),nn.GELU())
    def forward(self,x):return self.net(x)


class HybridEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.stem=ComplexConv(1,8,stride=(1,2))
        self.n1=nn.LayerNorm(16);self.n2=nn.LayerNorm(16);self.n3=nn.LayerNorm(16);self.n4=nn.LayerNorm(16)
        self.ff1=nn.Sequential(nn.Linear(16,64),nn.GELU(),nn.Linear(64,16))
        self.ff2=nn.Sequential(nn.Linear(16,64),nn.GELU(),nn.Linear(64,16))
        self.attn=nn.MultiheadAttention(16,4,dropout=0,batch_first=True)
        self.temporal=nn.Sequential(nn.Conv1d(16,16,3,padding=1,groups=16),nn.GELU(),nn.Conv1d(16,16,1))
        self.freq=nn.Conv2d(16,16,(3,1),padding=(1,0))
    def forward(self,x):
        x=radial(self.stem(x));n,c,f,t=x.shape
        q=x.permute(0,2,3,1).reshape(n*f,t,c)
        q=q+.5*self.ff1(self.n1(q));v=self.n2(q)
        q=q+self.attn(v,v,v,need_weights=False)[0]
        q=q+self.temporal(self.n3(q).transpose(1,2)).transpose(1,2)
        q=q+.5*self.ff2(self.n4(q))
        x=q.reshape(n,f,t,c).permute(0,3,1,2)
        return x+self.freq(x)


MODELS={'real_conv':RealEncoder,'complex_conv':ComplexEncoder,'hybrid_small':HybridEncoder}


def sources(n,s):
    rng=np.random.default_rng(s)
    bins=np.arange(11,54)
    amp=rng.uniform(.25,1,(n,len(bins)))
    amp=amp/np.sqrt(np.sum(amp**2,axis=1,keepdims=True)/2)
    ph=rng.uniform(-np.pi,np.pi,amp.shape)
    u=rng.uniform(-.8,.8,n)
    return amp,ph,u


def wave(source,taus):
    amp,ph,_=source
    freq=np.arange(11,54)*96000/256
    theta=2*np.pi*freq[:,None]*np.arange(2048)[None,:]/96000
    basis_cos=torch.tensor(np.cos(theta),dtype=torch.float32,device=DEVICE)
    basis_sin=torch.tensor(np.sin(theta),dtype=torch.float32,device=DEVICE)
    angle=ph-2*np.pi*taus[:,None]*freq[None,:]
    a=torch.tensor(amp*np.cos(angle),dtype=torch.float32,device=DEVICE)
    b=torch.tensor(amp*np.sin(angle),dtype=torch.float32,device=DEVICE)
    return a@basis_cos-b@basis_sin


def stft(raw):
    z=torch.stft(raw,256,64,window=torch.hann_window(256,device=DEVICE),center=False,return_complex=True)
    z=z[:,11:54,:]
    return torch.stack((z.real,z.imag),dim=1)


def noisy(clean,snr,s):
    gen=torch.Generator(device=DEVICE).manual_seed(s)
    noise=torch.randn(clean.shape,generator=gen,device=DEVICE)
    if isinstance(snr,str):return clean.clone()
    snr=torch.as_tensor(snr,device=DEVICE,dtype=torch.float32)
    if snr.ndim==1:snr=snr[:,None]
    return clean+noise*torch.sqrt(clean.square().mean(-1,keepdim=True)*10**(-snr/10))


def mono(n,source_seed,noise_seed):
    src=sources(n,source_seed);rng=np.random.default_rng(noise_seed)
    clean=wave(src,CFG['d']*src[2]/CFG['c'])
    obs=noisy(clean,rng.uniform(0,20,n),noise_seed)
    return stft(obs),stft(clean)


def pairs(n,source_seed,noise_seed,snr,scale):
    src=sources(n,source_seed)
    a=wave(src,np.zeros(n));b=wave(src,CFG['d']*src[2]/CFG['c'])
    snr0=snr
    if snr=='train':snr0=np.random.default_rng(noise_seed).uniform(0,20,n)
    xa=stft(noisy(a,snr0,noise_seed))/scale
    xb=stft(noisy(b,snr0,noise_seed+1))/scale
    da=stft(a);db=stft(b)
    za=torch.complex(da[:,0,21],da[:,1,21]);zb=torch.complex(db[:,0,21],db[:,1,21])
    phase=torch.angle((za*zb.conj()).mean(-1)).cpu().numpy()
    tau=-CFG['d']*src[2]/CFG['c']*1e6
    target=np.column_stack((tau/14.4,np.cos(phase),np.sin(phase)))
    return xa,xb,target,tau,phase


@torch.no_grad()
def encoded(enc,x):
    return torch.cat([enc(v) if enc else v[:,:, :,::2] for v in x.split(32)])


@torch.no_grad()
def features(enc,a,b):
    za=encoded(enc,a);zb=encoded(enc,b)
    # Identical pair readout: pooled bilinear terms and 12kHz terms, no coords.
    cross=torch.einsum('ncft,ndft->nfcd',za,zb)/za.shape[-1]
    feat=torch.cat((cross.mean(1).flatten(1),cross[:,21].flatten(1)),dim=1)
    std=float(za.std(dim=(0,2,3)).mean().cpu())
    return feat.double().cpu().numpy(),std


def probe_fit(x,y):
    mean=x.mean(0);std=x.std(0);std=np.maximum(std,1e-6)
    xx=np.column_stack((np.ones(len(x)),(x-mean)/std))
    reg=np.eye(xx.shape[1])*CFG['ridge']*len(x);reg[0,0]=0
    w=np.linalg.solve(xx.T@xx+reg,xx.T@y)
    return mean,std,w


def probe_apply(probe,x):
    mean,std,w=probe
    return np.column_stack((np.ones(len(x)),(x-mean)/std))@w


def metrics(pred,tau,phase):
    norm=np.linalg.norm(pred[:,1:3],axis=1)
    valid=np.isfinite(pred).all(1)&(norm>CFG['norm_floor'])
    et=np.abs(pred[valid,0]*14.4-tau[valid])
    ep=np.abs(np.angle(np.exp(1j*(np.arctan2(pred[valid,2],pred[valid,1])-phase[valid]))))
    return dict(n=len(tau),valid=int(valid.sum()),coverage=float(valid.mean()),
                median_tdoa_us=float(np.median(et)),p95_tdoa_us=float(np.percentile(et,95)),
                median_phase_rad=float(np.median(ep)),p95_phase_rad=float(np.percentile(ep,95)))


def checks():
    seed(7)
    x=torch.randn(2,2,43,29,device=DEVICE)
    cc=ComplexConv(1,8).to(DEVICE)
    r,i=x.chunk(2,1)
    weight=torch.complex(cc.r.weight,cc.i.weight)
    direct=fn.conv2d(torch.complex(r,i),weight,padding=1)
    z=cc(x);actual=torch.complex(*z.chunk(2,1))
    rel=float((actual-direct).norm()/direct.norm());assert rel<2e-5
    phi=.7;rot=torch.cat((r*np.cos(phi)-i*np.sin(phi),r*np.sin(phi)+i*np.cos(phi)),1)
    rr,ii=radial(x).chunk(2,1)
    expected=torch.cat((rr*np.cos(phi)-ii*np.sin(phi),rr*np.sin(phi)+ii*np.cos(phi)),1)
    assert torch.allclose(radial(rot),expected,atol=2e-6,rtol=2e-5)
    for cls in MODELS.values():
        e=cls().to(DEVICE);z=e(x);assert z.shape==(2,16,43,15)
        z.square().mean().backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in e.parameters())
    assert len(set(CFG['source_seeds'].values()))==4
    for u in [-.6,0,.6]:
        tau=-CFG['d']*u/CFG['c'];phase=-2*np.pi*12000*tau
        assert abs(-np.angle(np.exp(1j*phase))/(2*np.pi*12000)-tau)<1e-12
    return dict(complex_conv_relative_l2=rel,radial_equivariance='PASS',shapes_gradients='PASS',
                split_source_seeds='PASS',single_tone_delay_sign='PASS')


def main():
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False
    assert torch.cuda.is_available()
    started=time.time();unit=checks()
    x,d=mono(2048,8101,9101);vx,vd=mono(256,8102,9102)
    scale=float(x.square().mean().sqrt());assert scale>0
    x=x/scale;d=d/scale;vx=vx/scale;vd=vd/scale
    fit=pairs(512,8103,9103,'train',scale)
    tests={str(s):pairs(512,8104,9200+k*2,s,scale) for k,s in enumerate(CFG['test_snrs'])}
    WEIGHTS.mkdir(parents=True,exist_ok=True)
    result=dict(config=CFG,scale_train_only=scale,unit_checks=unit,runs=[],baselines={},
                versions=dict(python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,
                              gpu=torch.cuda.get_device_name(0)),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                lock_sha256=hashlib.sha256((ROOT/'uv.lock').read_bytes()).hexdigest(),
                status='IN_PROGRESS',weight_directory=str(WEIGHTS))
    rawfit,_=features(None,fit[0],fit[1]);rawprobe=probe_fit(rawfit,fit[2])
    for snr,(a,b,target,tau,phase) in tests.items():
        f,_=features(None,a,b)
        const=np.tile(fit[2].mean(0),(len(tau),1));const[:,0]=0
        result['baselines'][snr]=dict(raw=metrics(probe_apply(rawprobe,f),tau,phase),zero_delay_mean_phase=metrics(const,tau,phase))
    for s in CFG['seed_runs']:
        # same indexed batches for all architectures for this paired seed
        indices=np.random.default_rng(s).integers(0,len(x),(CFG['steps'],CFG['batch']))
        for name,cls in MODELS.items():
            if time.time()-started>900:raise RuntimeError('15-minute budget exceeded')
            seed(s);enc=cls().to(DEVICE);untrained=copy.deepcopy(enc).eval()
            dec=nn.Conv2d(16,2,1).to(DEVICE)
            opt=torch.optim.AdamW(list(enc.parameters())+list(dec.parameters()),lr=.001,weight_decay=.0001)
            torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();t0=time.time();losses=[]
            for step,idx in enumerate(indices):
                opt.zero_grad(set_to_none=True)
                h=enc(x[idx]);recon=fn.interpolate(dec(h),size=d.shape[-2:],mode='bilinear',align_corners=False)
                loss=fn.mse_loss(recon,d[idx]);assert torch.isfinite(loss)
                loss.backward();assert all(torch.isfinite(p.grad).all() for p in enc.parameters())
                opt.step()
                if step%50==0 or step==299:losses.append([step+1,float(loss.detach())])
            torch.cuda.synchronize();seconds=time.time()-t0
            enc.eval();dec.eval()
            with torch.no_grad():
                devpred=fn.interpolate(dec(enc(vx)),size=vd.shape[-2:],mode='bilinear',align_corners=False)
                devloss=float(fn.mse_loss(devpred,vd));rawloss=float(fn.mse_loss(vx,vd))
            peak=torch.cuda.max_memory_allocated()
            path=WEIGHTS/f'{name}-{s}.pt';torch.save(dict(encoder=enc.state_dict(),decoder=dec.state_dict(),config=CFG),path)
            row=dict(architecture=name,seed=s,encoder_params=sum(p.numel() for p in enc.parameters()),
                     decoder_params=sum(p.numel() for p in dec.parameters()),training_seconds=seconds,
                     peak_allocated_bytes=peak,steps=300,loss_trace=losses,dev_reconstruction_mse=devloss,
                     dev_noisy_input_mse=rawloss,weight_path=str(path),weight_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),results={})
            for label,model in [('untrained',untrained),('trained',enc)]:
                model.eval().requires_grad_(False)
                f,feature_std=features(model,fit[0],fit[1]);probe=probe_fit(f,fit[2])
                row.setdefault('fit_feature_std',{})[label]=feature_std
                row['results'][label]={}
                for snr,(a,b,target,tau,phase) in tests.items():
                    f,std=features(model,a,b)
                    row['results'][label][snr]=metrics(probe_apply(probe,f),tau,phase)
                    row['results'][label][snr]['feature_std']=std
            result['runs'].append(row)
            (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
            with (OUT/'autoresearch.jsonl').open('a') as out:
                out.write(json.dumps(dict(architecture=name,seed=s,status='completed',decision='keep evidence; no architecture promotion',
                                          evidence='results.json',dev_mse=devloss,train_seconds=seconds))+'\n')
            print(json.dumps(dict(architecture=name,seed=s,seconds=seconds,dev_mse=devloss,
                                  trained_10db=row['results']['trained']['10'])),flush=True)
            del enc,untrained,dec,opt
    result['status']='COMPLETED';result['wall_seconds']=time.time()-started
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('COMPLETED',result['wall_seconds'],flush=True)


if __name__=='__main__':main()
