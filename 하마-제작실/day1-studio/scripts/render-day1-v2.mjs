import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
const out=path.resolve('../Day1-v2');fs.mkdirSync(path.join(out,'review'),{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
const comps=[['Day1-V2-Mini','02-점심-ETF-미니.png'],['Day1-V2-Save','저장카드-복리.png'],['Day1-V2-Morning-1','01-아침-가격.png'],['Day1-V2-Morning-2','01-아침-예고.png'],['Day1-V2-Morning-3','01-아침-투표.png'],['Day1-V2-Night-1','04-밤-트렌치.png'],['Day1-V2-Night-2','04-밤-내일예고.png']];
for(const [id,name] of comps){const composition=await selectComposition({serveUrl,id});await renderStill({serveUrl,composition,output:path.join(out,name),imageFormat:'png'});console.log(name);}
const composition=await selectComposition({serveUrl,id:'Day1-V2-Reel'});
for(const frame of [1,45,135,225,285,390,435,495,600,690,840]){await renderStill({serveUrl,composition,frame,output:path.join(out,'review',`${frame}.png`),imageFormat:'png'});}
if(process.argv.includes('--stills-only'))process.exit(0);
await renderMedia({serveUrl,composition,outputLocation:path.join(out,'03-저녁-복리-릴스.mp4'),codec:'h264',crf:18,concurrency:4});
console.log('30초 릴스 렌더 완료');
