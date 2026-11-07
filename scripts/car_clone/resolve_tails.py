"""Recover full solid names that GEOMETRY.BIN truncates to 27 characters, by matching the stored
name hash against suffixes built from other cars' names (geo_*.bin in the current directory).

Usage: python resolve_tails.py geo_<CAR>.bin <CAR> tails.json
"""
import re,struct,sys,itertools,glob,json
def h(s,x=0xFFFFFFFF):
    for c in s: x=(x*33+c)&0xFFFFFFFF
    return x
fn,old=sys.argv[1],sys.argv[2].encode()
d=open(fn,'rb').read()
tokens=set()
for g in glob.glob('geo_*.bin'):
    for m in re.finditer(rb'[A-Z0-9]+(?:_[A-Z0-9]+)+',open(g,'rb').read()):
        for t in m.group().split(b'_'):
            if 1<len(t)<=12: tokens.add(t)
tokens|={b'MEDIUM',b'SMALL',b'LARGE',b'WIDE',b'RECT',b'SQUARE',b'MIRROR',b'UNIT',b'PANEL',b'LEFT',b'RIGHT',b'TALL',b'A',b'B',b'C',b'D'}
tokens=sorted(tokens);print('tokens',len(tokens),file=sys.stderr)
found={}
for m in re.finditer(re.escape(old)+rb'(_[A-Z0-9_]*)\x00',d):
    suf=m.group(1)
    if len(old)+len(suf)<27: continue
    if suf in found: continue
    target=struct.unpack_from('<I',d,m.start()-148)[0]
    if h(old+suf)==target: continue
    # split truncated suffix: last partial token completes, then 0-2 more tokens
    head,_,part=suf.rpartition(b'_')
    best=None
    for t in tokens:
        if not t.startswith(part): continue
        base=old+head+b'_'+t
        if h(base)==target: best=head+b'_'+t;break
        for t2 in tokens:
            s2=base+b'_'+t2
            if h(s2)==target: best=head+b'_'+t+b'_'+t2;break
            for t3 in (b'A',b'B',b'C',b'L',b'R',b'LEFT',b'RIGHT',b'MEDIUM',b'SMALL',b'LARGE'):
                if h(s2+b'_'+t3)==target: best=head+b'_'+t+b'_'+t2+b'_'+t3;break
            if best: break
        if best: break
    found[suf]=best
    print(suf.decode(),'->',best.decode() if best else None,file=sys.stderr)
json.dump({k.decode():v.decode() for k,v in found.items() if v},open(sys.argv[3],'w'))
