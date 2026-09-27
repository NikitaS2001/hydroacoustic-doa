#!/usr/bin/env python3
"""Repeat the independent nongrid-angle and close-echo checks using the main pilot."""
import argparse
import numpy as np
import synthetic_stft_tdoa as m


def independent():
    for u in (.37, -.41):
        x = m.signals(u)
        raw, _ = m.metrics(x)
        truth = -m.D*u/m.C*1e6
        assert abs(raw[0]['lag_us']-truth) < .2
        print('u',u,'truth pair01 us',truth,'raw us',raw[0]['lag_us'])
        for h in (64,128):
            z, starts, win = m.stft(x,h)
            rec, covered = m.istft(z,starts,win)
            tf, _ = m.metrics(x,z)
            maxdiff = np.max(np.abs(rec[:,covered]-x[:,covered]))
            assert maxdiff < 1e-12
            assert abs(tf[0]['lag_us']-truth) < .2
            print('hop',h,'TF pair01 us',tf[0]['lag_us'],'max abs reconstruction error',maxdiff)
    print('independent nongrid signed-delay and reconstruction checks PASS')


def stress():
    u=.6
    loc=m.D*np.arange(m.N_CH)
    src=m.source()
    direct=m.signals(u)
    close=np.stack([m.shift(src,.00008+d*(-.3)/m.C) for d in loc])
    rng=np.random.default_rng(221)
    x=direct+.8*close+.02*rng.standard_normal(direct.shape)
    raw,_=m.metrics(x)
    truth0=-m.D*u/m.C*1e6
    print('stress: echo delay 80us amplitude .8 alternate u=-.3; fixed-seed noise .02; truth adjacent',truth0)
    for h in (64,128):
        z,_,_=m.stft(x,h)
        tf,_=m.metrics(x,z)
        err=max(abs(v['lag_us']-m.D*(i-j)*u/m.C*1e6) for v,(i,j) in zip(tf,[(i,i+1) for i in range(7)]+[(0,7)]))
        print('hop',h,'TF adjacent',tf[0]['lag_us'],'raw adjacent',raw[0]['lag_us'],'max TF error across pairs us',round(err,3))


if __name__=='__main__':
    arg=argparse.ArgumentParser()
    arg.add_argument('case',choices=['independent','stress'])
    args=arg.parse_args()
    (independent if args.case=='independent' else stress)()
