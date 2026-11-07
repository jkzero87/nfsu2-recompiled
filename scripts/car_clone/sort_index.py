"""Re-sort the solid hash index tables ({u32 hash, u32 0} pairs, ascending) of a renamed GEOMETRY.BIN.
Tables are located in the original file; the renamed file has the same layout."""
import struct,sys
orig=open(sys.argv[1],'rb').read();d=bytearray(open(sys.argv[2],'rb').read())
assert len(orig)==len(d)
tables=[];i=0
while i+16<=len(orig):
    if orig[i+4:i+8]==b'\0\0\0\0' and i%4==0:
        j=i;prev=-1
        while j+8<=len(orig) and orig[j+4:j+8]==b'\0\0\0\0':
            h=struct.unpack_from('<I',orig,j)[0]
            if h<=prev or h==0: break
            prev=h;j+=8
        n=(j-i)//8
        if n>=16:
            tables.append((i,n));i=j;continue
    i+=4
fixed=0
for off,n in tables:
    hs=sorted(struct.unpack_from('<I',d,off+k*8)[0] for k in range(n))
    for k,h in enumerate(hs): struct.pack_into('<II',d,off+k*8,h,0)
    fixed+=n
open(sys.argv[2],'wb').write(d)
print('tables',[(hex(o),n) for o,n in tables],'entries',fixed)
