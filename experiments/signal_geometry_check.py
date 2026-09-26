"""Planning arithmetic only: c and d are assumptions, not measured site values."""
fs = 96000
n = 8
d = 0.027
for c in (1400, 1500, 1550):
    print(f'c={c} m/s; f_alias={c/(2*d):.1f} Hz; adjacent tau={d/c*1e6:.2f} us ({d/c*fs:.3f} samples); aperture tau={(n-1)*d/c*1e6:.2f} us ({(n-1)*d/c*fs:.3f} samples)')
print('aperture m:', (n-1)*d)
for f in (4000, 12000, 20000, 26000, 30000):
    print('f=', f, 'lambda at 1500=', 1500/f, 'd/lambda=', d*f/1500, 'fraunhofer_m=', 2*((n-1)*d)**2*f/1500)
for nfft, hop in ((256, 64), (512, 128), (512, 64)):
    print('STFT', nfft, hop, 'window_ms', nfft/fs*1e3, 'hop_ms', hop/fs*1e3, 'bin_Hz', fs/nfft, 'frames_50ms_no_padding', 1+(round(fs*.05)-nfft)//hop)
print('B=16k resolution order us:', 1e6/16000)
