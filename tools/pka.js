const zlib=require('zlib');
const tf=require('twofish').twofish();
const key=new Array(16).fill(137), iv=new Array(16).fill(16);
const E=b=>Array.from(tf.encrypt(key,Array.from(b))).slice(0,16);
const dbl=b=>{const o=[];let c=0;for(let i=15;i>=0;i--){const v=(b[i]<<1)|c;o[i]=v&0xff;c=b[i]>>7;} if(b[0]&0x80)o[15]^=0x87;return o;};
const L=E(new Array(16).fill(0)),K1=dbl(L),K2=dbl(K1);
function cmac(m){const nb=Math.max(1,Math.ceil(m.length/16));let x=new Array(16).fill(0);
 for(let b=0;b<nb;b++){let blk=Array.from(m.subarray?m.subarray(b*16,b*16+16):m.slice(b*16,b*16+16));
  if(b==nb-1){ if(blk.length==16&&m.length>0) blk=blk.map((v,i)=>v^K1[i]); else {blk.push(0x80);while(blk.length<16)blk.push(0);blk=blk.map((v,i)=>v^K2[i]);} }
  x=E(x.map((v,i)=>v^blk[i]));}
 return x;}
const pre=t=>{const a=new Array(16).fill(0);a[15]=t;return a;};
const N=cmac([...pre(0),...iv]);
function ctr(data){const out=Buffer.alloc(data.length);let c=N.slice();
 for(let off=0;off<data.length;off+=16){const ks=E(c);for(let j=0;j<16&&off+j<data.length;j++)out[off+j]=data[off+j]^ks[j];
  for(let k=15;k>=0;k--){c[k]=(c[k]+1)&0xff;if(c[k])break;}}return out;}
function tag(ct){const H=cmac(pre(1)); const C=cmac(Buffer.concat([Buffer.from(pre(2)),ct])); return Buffer.from(N.map((v,i)=>v^H[i]^C[i]));}
function decodeRaw(inp){const n=inp.length;const s1=Buffer.alloc(n);
 for(let i=0;i<n;i++) s1[i]=(inp[n+~i] ^ ((n - i*n)&0xff))&0xff;
 const ct=s1.subarray(0,n-16), t=s1.subarray(n-16);
 const ok=tag(ct).equals(t);
 const pt=ctr(ct); const m=pt.length; for(let i=0;i<m;i++) pt[i]^=(m-i)&0xff;
 return {pt,ok};}
function decode(inp){const {pt,ok}=decodeRaw(inp); if(!ok) throw new Error('tag mismatch'); return zlib.inflateSync(pt.subarray(4));}
function encodeRaw(pt){pt=Buffer.from(pt);const m=pt.length;for(let i=0;i<m;i++) pt[i]^=(m-i)&0xff;
 const ct=ctr(pt); const s1=Buffer.concat([ct,tag(ct)]); const n=s1.length; const out=Buffer.alloc(n);
 for(let i=0;i<n;i++) out[n+~i]=(s1[i]^((n-i*n)&0xff))&0xff; return out;}
function encode(xml){const z=zlib.deflateSync(Buffer.from(xml)); const h=Buffer.alloc(4); h.writeUInt32BE(Buffer.byteLength(xml)); return encodeRaw(Buffer.concat([h,z]));}
// Legacy format (Packet Tracer 4.x/5.x): byte[i] ^= (len - i), then 4-byte BE size + zlib.
function decodeLegacy(inp){const n=inp.length;const o=Buffer.alloc(n);
 for(let i=0;i<n;i++) o[i]=inp[i]^((n-i)&0xff);
 return zlib.inflateSync(o.subarray(4));}
function encodeLegacy(xml){xml=Buffer.from(xml);const z=zlib.deflateSync(xml);const h=Buffer.alloc(4);h.writeUInt32BE(xml.length);
 const o=Buffer.concat([h,z]);const n=o.length;for(let i=0;i<n;i++) o[i]^=(n-i)&0xff;return o;}
// Auto-detect: try the modern format (EAX tag must verify), fall back to legacy.
function decodeAny(inp){
 try{const {pt,ok}=decodeRaw(inp); if(ok) return {format:'modern',xml:zlib.inflateSync(pt.subarray(4))};}catch(e){}
 return {format:'legacy',xml:decodeLegacy(inp)};}
module.exports={decode,decodeRaw,encodeRaw,encode,decodeLegacy,encodeLegacy,decodeAny};
