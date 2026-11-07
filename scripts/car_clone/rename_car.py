"""Clone a car GEOMETRY.BIN under another car name: rewrite solid names and their bStringHash keys.
A solid stores the hash of its full name 148 bytes before its (possibly truncated) name string."""
import re,struct,sys,json,glob
def h(s,x=0xFFFFFFFF):
    for c in s: x=(x*33+c)&0xFFFFFFFF
    return x
src,old,new,out,tails=sys.argv[1],sys.argv[2].encode(),sys.argv[3].encode(),sys.argv[4],json.load(open(sys.argv[5]))
orig=open(src,'rb').read();d=bytearray(orig)
vocab=set()
for g in glob.glob('geo_*.bin'):
    pre=g[4:-4].encode()
    for m in re.finditer(re.escape(pre)+rb'(_[A-Z0-9_]+)\x00',open(g,'rb').read()): vocab.add(m.group(1))
occ=[(m.start(),m.group(1) or b'') for m in re.finditer(re.escape(old)+rb'(_[A-Z0-9_]*)?\x00',orig)]
hashes=set(struct.unpack_from('<I',orig,o-148)[0] for o,_ in occ if o>=148)
full={}
for o,suf in occ:
    if suf in full: continue
    cands=[suf]+([tails[suf.decode()].encode()] if suf.decode() in tails else [])+sorted(v for v in vocab if v.startswith(suf) and v!=suf)
    for c in cands:
        if c and h(old+c) in hashes: full[suf]=c;break
mapping={h(old+f):h(new+f) for f in full.values()}
for o,suf in occ:
    span=len(old)+len(suf);s=(new+full.get(suf,suf))[:span]
    d[o:o+span+1]=s+b'\0'*(span+1-len(s))
writes=0
for oh,nh in mapping.items():
    a,b=struct.pack('<I',oh),struct.pack('<I',nh);i=orig.find(a)
    while i!=-1: d[i:i+4]=b;writes+=1;i=orig.find(a,i+1)
open(out,'wb').write(d)
miss=sorted({s.decode() for o,s in occ if s and s not in full})
print(f'occurrences {len(occ)}, solids renamed {len(mapping)} ({writes} hash writes), unresolved {len(miss)}: {miss}')
