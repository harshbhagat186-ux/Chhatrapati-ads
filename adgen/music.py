"""Synthesize a short festive track: tanpura-like drone, temple bells, bansuri-style melody."""
import sys, wave, numpy as np
SR = 44100
def env(n, a=0.02, r=0.3):
    e = np.ones(n); ai, ri = int(a*SR), int(r*SR)
    e[:ai] = np.linspace(0, 1, ai); e[-ri:] *= np.linspace(1, 0, ri); return e
def tone(f, dur, harm=(1, .5, .25, .12), vib=0.0):
    t = np.arange(int(dur*SR))/SR
    ph = 2*np.pi*f*t + (vib*np.sin(2*np.pi*5.5*t)/5.5)
    return sum(a*np.sin((i+1)*ph) for i, a in enumerate(harm))
def bell(f, dur=2.5):
    t = np.arange(int(dur*SR))/SR
    parts = [(1, 1), (2.76, .5), (5.4, .25), (8.93, .12)]
    return sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*(1.5+m*.8)) for m, a in parts)
def track(dur, seed=0):
    n = int(dur*SR); out = np.zeros(n + SR*3)
    sa = 261.63  # C
    # drone: Pa Sa Sa Sa(low) plucks repeating
    for k, t0 in enumerate(np.arange(0, dur, 0.5)):
        f = [sa*1.5/2, sa, sa, sa/2][k % 4]
        s = tone(f, 1.6, (1, .6, .45, .3, .2, .1)) * np.exp(-np.arange(int(1.6*SR))/SR*1.2) * 0.10
        i = int(t0*SR); out[i:i+len(s)] += s
    # melody (Yaman flavour): Ni Re Ga Ma# Pa Dha Ni Sa'
    r = {"N.": 15/16, "S": 1, "R": 9/8, "G": 5/4, "M": 45/32, "P": 3/2, "D": 5/3, "N": 15/8, "S'": 2}
    phrases = [
        [("N.",.5),("R",.5),("G",1),("M",.5),("G",.5),("R",.5),("S",1),("G",.5),("M",.5),("P",1),("D",.5),("N",.5),("S'",1.5)],
        [("S",.5),("G",.5),("P",1),("D",.5),("P",.5),("M",.5),("G",1),("R",.5),("G",.5),("S",1.5)],
        [("P",.5),("D",.5),("N",.5),("S'",1),("N",.5),("D",.5),("P",1),("M",.5),("G",.5),("R",.5),("S",1.5)],
    ]
    phrase = phrases[seed % len(phrases)]
    t0 = 0.6
    while t0 < dur - 1:
        for note, d in phrase:
            if t0 >= dur - 0.8: break
            s = tone(sa*r[note]*2, d*0.7+0.15, (1, .3, .08), vib=3) * env(int((d*0.7+0.15)*SR), .06, .15) * 0.16
            i = int(t0*SR); out[i:i+len(s)] += s; t0 += d*0.7
    for t0 in [0.0, dur/2, dur-1.6]:
        s = bell(sa*4)*0.22; i = int(t0*SR); out[i:i+len(s)] += s
    # simple reverb
    for dly, g in [(0.031, .3), (0.047, .25), (0.083, .2), (0.13, .15)]:
        k = int(dly*SR); out[k:] += out[:-k]*g
    out = out[:n]; out *= env(n, 0.3, 1.0); out /= np.abs(out).max()*1.15
    st = np.stack([out, np.roll(out, 300)], 1)
    return (st*32767).astype(np.int16)
def write(dur, path, seed=0):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(track(dur, seed).tobytes())

if __name__ == "__main__":
    write(float(sys.argv[1]), sys.argv[2])
