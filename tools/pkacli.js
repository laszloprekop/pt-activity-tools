#!/usr/bin/env node
// Usage:
//   node tools/pkacli.js decode <in.pka|pkt> <out.xml>      (auto-detects modern vs legacy)
//   node tools/pkacli.js encode <in.xml> <out.pka>          (modern format, PT 7.x/8.x)
//   node tools/pkacli.js encode-legacy <in.xml> <out.pka>   (PT 4.x/5.x format)
//   node tools/pkacli.js info <in.pka>                      (format, version, size)
const fs=require('fs'),p=require('./pka');
const [cmd,a,b]=process.argv.slice(2);
if(cmd==='decode'){const r=p.decodeAny(fs.readFileSync(a));fs.writeFileSync(b,r.xml);console.log(r.format,'->',b,r.xml.length,'bytes');}
else if(cmd==='encode'){const x=fs.readFileSync(a);const e=p.encode(x);fs.writeFileSync(b,e);
  if(!p.decode(fs.readFileSync(b)).equals(x)) throw new Error('round-trip verification failed');console.log('encoded+verified',b,e.length,'bytes');}
else if(cmd==='encode-legacy'){fs.writeFileSync(b,p.encodeLegacy(fs.readFileSync(a)));console.log('encoded legacy',b);}
else if(cmd==='info'){const r=p.decodeAny(fs.readFileSync(a));const v=(r.xml.toString('utf8',0,400).match(/<VERSION>([^<]+)/)||[])[1];console.log(a,'| format:',r.format,'| PT version:',v,'| xml bytes:',r.xml.length);}
else {console.error('usage: pkacli.js decode|encode|encode-legacy|info ...');process.exit(1);}
