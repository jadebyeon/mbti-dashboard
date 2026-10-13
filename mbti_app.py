import base64
import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent

st.set_page_config(page_title="MBTI in writing", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
header, footer, #MainMenu, [data-testid="stToolbar"] {display:none !important}
html, body, .stApp, [data-testid="stAppViewContainer"], section.main {overflow:hidden !important; background:#070708 !important}
.block-container, [data-testid="stMainBlockContainer"] {padding:0 !important; max-width:100% !important}
[data-testid="stVerticalBlock"] {gap:0 !important}
iframe {height:100vh !important; border:0 !important}
</style>""", unsafe_allow_html=True)

# Fixed notebook result (all 8,600 users): largest rank-biserial effect across the 6 measures
LETTER_EFFECT = {"I/E": 0.221, "S/N": 0.082, "T/F": 0.335, "J/P": 0.096}

# Nickname and tagline from 16Personalities (personality types page)
INFO = {
    "INTJ": ["Architect", "Imaginative and strategic thinkers, with a plan for everything."],
    "INTP": ["Logician", "Innovative inventors with an unquenchable thirst for knowledge."],
    "ENTJ": ["Commander", "Bold, imaginative and strong-willed leaders, always finding a way – or making one."],
    "ENTP": ["Debater", "Smart and curious thinkers who cannot resist an intellectual challenge."],
    "INFJ": ["Advocate", "Quiet and mystical, yet very inspiring and tireless idealists."],
    "INFP": ["Mediator", "Poetic, kind and altruistic people, always eager to help a good cause."],
    "ENFJ": ["Protagonist", "Charismatic and inspiring leaders, able to mesmerize their listeners."],
    "ENFP": ["Campaigner", "Enthusiastic, creative and sociable free spirits, who can always find a reason to smile."],
    "ISTJ": ["Logistician", "Practical and fact-minded individuals, whose reliability cannot be doubted."],
    "ISFJ": ["Defender", "Very dedicated and warm protectors, always ready to defend their loved ones."],
    "ESTJ": ["Executive", "Excellent administrators, unsurpassed at managing things – or people."],
    "ESFJ": ["Consul", "Extraordinarily caring, social and popular people, always eager to help."],
    "ISTP": ["Virtuoso", "Bold and practical experimenters, masters of all kinds of tools."],
    "ISFP": ["Adventurer", "Flexible and charming artists, always ready to explore and experience something new."],
    "ESTP": ["Entrepreneur", "Smart, energetic and very perceptive people, who truly enjoy living on the edge."],
    "ESFP": ["Entertainer", "Spontaneous, energetic and enthusiastic people – life is never boring around them."],
}

METRICS = ["emotion", "self_words", "other_words", "love_family", "mbti_talk", "hobbies"]
MIME = {".svg": "image/svg+xml", ".png": "image/png"}


def avatar_files():
    folder = HERE / "avatars"
    if not folder.exists():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in MIME and p.stem.upper() in INFO)


@st.cache_data
def build_payload(signature):
    df = pd.read_csv(HERE / "mbti_dashboard.csv")
    cap = max(float(df["emotion"].quantile(0.99)), 1e-6)
    bins = np.linspace(0, cap, 21)
    types = {}
    for t, g in df.groupby("type"):
        counts, _ = np.histogram(g["emotion"].clip(upper=cap), bins=bins)
        types[t] = {
            "n": int(len(g)),
            "sums": {m: float(g[m].sum()) for m in METRICS},
            "hist": counts.tolist(),
            "med": float(g["emotion"].median()),
            "rest_med": float(df.loc[df["type"] != t, "emotion"].median()),
        }
    avatars = {}
    for p in avatar_files():
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        avatars[p.stem.upper()] = f"data:{MIME[p.suffix.lower()]};base64,{b64}"
    return {"N": int(len(df)), "K": 20, "cap": cap, "types": types,
            "letters": LETTER_EFFECT, "info": INFO, "avatars": avatars}


TEMPLATE = r"""<!doctype html><html><head><meta charset="utf-8"><style>
:root{--bg:#070708;--card:#0d0d0f;--panel:#131315;--panel2:#1c1c20;--line:#26262b;--text:#f4f4f5;--mute:#8a8a93;--warm:#f0a04b;--mine:#5be08f;--rest:#5a5a63}
*{box-sizing:border-box;margin:0}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:-apple-system,"Inter",system-ui,sans-serif;overflow:hidden}
#stage{position:absolute;left:0;top:0;width:1280px;height:760px;transform-origin:0 0;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 28px 18px;display:flex;flex-direction:column;gap:14px}
.top{display:flex;align-items:center;gap:28px;height:46px}
.brand{font-size:15px;font-weight:800;color:var(--text);letter-spacing:.14em;white-space:nowrap}
.letters{display:flex;align-items:center;gap:18px}
.letters .cap{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--warm);text-align:right;line-height:1.3}
.chips{display:flex;gap:14px}
.chip{width:112px}
.chip b{font-size:14px}.chip span{font-size:12px;color:var(--mute);margin-left:6px}
.track{height:7px;background:repeating-linear-gradient(90deg,var(--line) 0 4px,transparent 4px 6px);margin:5px 0 3px}
.fill{height:7px;background:repeating-linear-gradient(90deg,var(--mine) 0 4px,transparent 4px 6px)}
.chip em{font-style:normal;font-size:11px;color:var(--mute)}
.main{flex:1;min-height:0;display:flex;gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;min-width:0}
.avatar{width:250px;padding-top:40px;position:relative;overflow:hidden;background:radial-gradient(ellipse 85% 48% at 50% 30%,color-mix(in srgb,var(--mine) 26%,transparent),transparent 72%),var(--panel);display:flex;flex-direction:column;align-items:center;text-align:center}
#art{position:relative;width:100%;height:210px;display:flex;align-items:center;justify-content:center}
#art img{max-width:100%;max-height:100%;object-fit:contain}
.badge{width:150px;height:150px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:30px;color:#0b0b0c}
#pick{position:relative;display:inline-flex;align-items:center;gap:10px;border-bottom:2px dashed var(--line);padding:0 4px 4px;margin-top:8px;cursor:pointer}
#pick:hover,#pick:focus-within{border-bottom-color:var(--mine)}
#name{white-space:nowrap;font-size:54px;font-weight:900;letter-spacing:-.02em;line-height:1.1}
#name.ph{font-size:30px;color:var(--mute)}
.caret{font-size:28px;color:var(--mine);line-height:1}
#sel{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;cursor:pointer;font-size:16px;color-scheme:dark}
#nick{font-size:16px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;margin-top:10px;color:var(--mine)}
#tag{font-size:14px;line-height:1.45;color:var(--text);margin-top:8px}
#meta{font-size:13px;color:var(--mute);margin-top:auto}
#warn{display:none;margin-top:8px;font-size:12px;color:#ffb86b;border:1px solid #ffb86b;border-radius:999px;padding:2px 10px}
.mid{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px}
#lg{flex:1;font-size:13px;color:var(--text);display:flex;align-items:center;white-space:nowrap}
#lg i{display:inline-block;width:9px;height:9px;border-radius:50%;margin:0 6px 0 0}
#lg i:not(:first-child){margin-left:16px}
#empty{flex:1;display:flex;align-items:center;justify-content:center;color:var(--mute);font-size:18px;border:1px dashed var(--line);border-radius:12px}
#panels{flex:1;min-height:0;display:none;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:14px}
#panels .wide{grid-column:1 / 3}
.panel{display:flex;flex-direction:column;min-height:0}
.panel h3{font-size:16px;font-weight:800;letter-spacing:.06em;text-transform:uppercase}
.panel p{font-size:12px;color:var(--warm);margin:2px 0 4px}
.panel svg{flex:1;min-height:0;width:100%}
.board{width:280px;display:flex;flex-direction:column}
.board h3{font-size:16px;font-weight:800;letter-spacing:.06em;text-transform:uppercase}
.board p{font-size:12px;color:var(--warm);margin:2px 0 8px}
#tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:10px}
#tabs button{background:var(--panel2);color:var(--mute);border:1px solid var(--line);border-radius:8px;padding:5px 2px;font-size:11.5px;font-family:inherit;cursor:pointer}
#tabs button.on{color:#0b0b0c;background:var(--mine);border-color:var(--mine);font-weight:700}
#rows{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:space-between}
.row{display:grid;grid-template-columns:20px 44px 1fr 46px;align-items:center;gap:6px;padding:2px 4px;border-radius:10px;border:1px solid transparent}
.row.me{background:var(--panel2);border-color:var(--mine);box-shadow:0 0 10px color-mix(in srgb,var(--mine) 35%,transparent)}
.rk{font-size:12px;color:var(--mute);text-align:right}
.pill{font-size:11px;font-weight:800;color:#0b0b0c;border-radius:6px;text-align:center;padding:2px 0}
.bar{height:10px;background:repeating-linear-gradient(90deg,var(--line) 0 4px,transparent 4px 6px)}
.bar i{display:block;height:10px}
.val{font-size:12px;text-align:right}
.note{font-size:11px;color:var(--mute);margin-top:8px;line-height:1.35}
.foot{height:58px;display:flex;flex-direction:column;gap:3px}
.take{font-size:14px;color:var(--text)}
.take b{color:var(--mine);margin-right:8px;text-transform:uppercase;letter-spacing:.1em;font-size:12px}
.lim{font-size:12px;color:var(--mute)}
.take b.w{color:var(--warm)}
.v{fill:var(--text);font-size:11px;font-weight:600}.sel{filter:drop-shadow(0 0 5px var(--mine))}.x{fill:var(--mute);font-size:12px}
#tip{position:fixed;display:none;max-width:250px;background:#000;color:var(--text);border:1px solid var(--line);padding:8px 10px;font-size:12px;line-height:1.4;pointer-events:none;z-index:9;border-radius:8px}
</style></head><body>
<div id="stage">
 <div class="top">
  <div class="brand">MBTI IN WRITING</div>
  <div id="lg"></div>
  <div class="letters"><div class="cap">Which letters show up in writing<br>all 8,600 people</div><div class="chips" id="chips"></div></div>
 </div>
 <div class="main">
  <div class="card avatar">
   <div id="art"></div>
   <div id="pick"><span id="name">Pick a type</span><span class="caret">▾</span><select id="sel"></select></div>
   <div id="nick"></div>
   <div id="tag"></div>
   <div id="warn">Small sample, unstable</div>
   <div id="meta"></div>
  </div>
  <div class="mid">
   <div id="empty">Pick a type to compare it with everyone else</div>
   <div id="panels">
    <div class="card panel wide"><h3>Spirit</h3><p>emotion · laughs + exclamation marks per post · dashed lines = medians</p><svg id="c1" viewBox="0 0 630 235"></svg></div>
    <div class="card panel"><h3>Who they talk about</h3><p>words per post</p><svg id="c2" viewBox="0 0 290 240"></svg></div>
    <div class="card panel"><h3>What's on their mind</h3><p>share of posts that mention each topic</p><svg id="c3" viewBox="0 0 290 240"></svg></div>
   </div>
  </div>
  <div class="card board">
   <h3>Ranking</h3><p id="bsub"></p>
   <div id="tabs"></div>
   <div id="rows"></div>
   <div class="note">Bars start at 0, so close bars mean similar writing. * fewer than 100 people.</div>
  </div>
 </div>
<div class="foot"><div class="take"><b>Takeaway</b>Types differ a little on average, most clearly for T vs F, but people of every type overlap a lot, so a type is a weak guide to how any one person writes.</div><div class="take"><b class="w">Themes</b>Two stood out in the 150 posts we read (all 8,600 people, not changed by your pick). One is MBTI talk and the other is relationships and family. Many posts fit neither.</div><div class="lim">
 Self-reported types · online forum posts · keyword-based measures · type descriptions from 16Personalities</div></div>
</div>
<div id="tip"></div>
<script>
const D=__DATA__;
const T=D.types,N=D.N,K=D.K,INFO=D.info,AV=D.avatars;
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
const keys=Object.keys(T).sort();
const COL={a:'#b18cf0',d:'#4fc38a',s:'#5aa9e6',e:'#f0c24b'};
const grp=c=>c[1]==='N'?(c[2]==='T'?'a':'d'):(c[3]==='J'?'s':'e');
const col=c=>COL[grp(c)];
const pct=v=>(v*100).toFixed(1)+'%',dec=v=>v.toFixed(2);
const M=[
 {k:'emotion',n:'Spirit',u:'laughs + ! per post',f:dec},
 {k:'self_words',n:'About self',u:'I / me / my per post',f:dec},
 {k:'other_words',n:'To others',u:'you / we / us per post',f:dec},
 {k:'love_family',n:'Heart',u:'share of posts',f:pct},
 {k:'mbti_talk',n:'MBTI talk',u:'share of posts',f:pct},
 {k:'hobbies',n:'Hobbies',u:'share of posts',f:pct}];
const tot={hist:Array(K).fill(0),sums:{}};
keys.forEach(k=>{T[k].hist.forEach((v,i)=>tot.hist[i]+=v);for(const m in T[k].sums)tot.sums[m]=(tot.sums[m]||0)+T[k].sums[m]});
const mean=(t,m)=>T[t].sums[m]/T[t].n;
let sel='',cur='emotion';

$('sel').innerHTML='<option value="">Pick a type</option>'+keys.map(k=>`<option value="${k}">${k}</option>`).join('');
$('chips').innerHTML=Object.entries(D.letters).map(([k,r])=>
 `<div class="chip" data-tip="${esc(k+': effect size '+r.toFixed(2)+'. Higher means this letter shows up more in how people write.')}"><b>${k}</b><span>${r.toFixed(2)}</span><div class="track"><div class="fill" style="width:${Math.min(r/0.4,1)*100}%"></div></div><em>${r>=0.2?'visible':'barely visible'}</em></div>`).join('');
$('tabs').innerHTML=M.map(m=>`<button data-k="${m.k}">${m.n}</button>`).join('');

function bars(ms,rs,labels,fmt,tipFn){
 const W=290,H=240,l=4,t=26,b=34,k=ms.length,gw=(W-2*l)/k,bw=Math.min(gw*0.32,40),ph=H-t-b;
 const mx=Math.max(...ms,...rs)||1;let s='';
 ms.forEach((v,i)=>{
  const x0=l+i*gw+gw/2,o=rs[i];
  s+=`<g data-tip="${esc(tipFn(v,o,i))}"><rect x="${l+i*gw}" y="0" width="${gw}" height="${H}" fill="transparent"/>`;
  [[o,x0-bw-2,'var(--rest)'],[v,x0+2,'var(--mine)']].forEach(([val,x,c])=>{
   const h=val/mx*ph;
   s+=`<rect class="${c==='var(--mine)'?'sel':''}" x="${x}" y="${t+ph-h}" width="${bw}" height="${h}" rx="2" fill="${c}"/>`;
   s+=`<text x="${x+bw/2}" y="${t+ph-h-5}" text-anchor="middle" class="v">${fmt(val)}</text>`;
  });
  s+=`<text x="${x0}" y="${H-12}" text-anchor="middle" class="x">${labels[i]}</text></g>`;
 });
 return s+`<line x1="${l}" x2="${W-l}" y1="${t+ph}" y2="${t+ph}" stroke="var(--line)"/>`;
}

function hist(d,name){
 const W=630,H=235,l=4,rr=4,t=22,b=30,pw=W-l-rr,ph=H-t-b,bw=pw/K;
 const rest=tot.hist.map((v,i)=>v-d.hist[i]);
 const sm=d.hist.reduce((x,y)=>x+y,0),sr=rest.reduce((x,y)=>x+y,0);
 const m=d.hist.map(v=>v/sm),q=rest.map(v=>v/sr),mx=Math.max(...m,...q)||1;let s='';
 for(let i=0;i<K;i++){
  const x=l+i*bw,hr=q[i]/mx*ph,hm=m[i]/mx*ph;
  s+=`<rect x="${x+1}" y="${t+ph-hr}" width="${bw-2}" height="${hr}" fill="var(--rest)" opacity=".85"/>`;
  s+=`<rect x="${x+1}" y="${t+ph-hm}" width="${bw-2}" height="${hm}" fill="var(--mine)" opacity=".7"/>`;
 }
 const xm=v=>l+Math.min(v/D.cap,1)*pw;
 s+=`<line x1="${xm(d.rest_med)}" x2="${xm(d.rest_med)}" y1="${t}" y2="${t+ph}" stroke="var(--mute)" stroke-width="1.5" stroke-dasharray="4 3"/>`;
 s+=`<line x1="${xm(d.med)}" x2="${xm(d.med)}" y1="${t}" y2="${t+ph}" stroke="var(--mine)" stroke-width="1.5" stroke-dasharray="4 3"/>`;
 s+=`<line x1="${l}" x2="${W-rr}" y1="${t+ph}" y2="${t+ph}" stroke="var(--line)"/>`;
 s+=`<text x="${l}" y="${H-10}" class="x">0</text><text x="${W-rr}" y="${H-10}" text-anchor="end" class="x">${D.cap.toFixed(1)}+</text>`;
 s+=`<text x="${l}" y="12" class="x">share of people</text>`;
 return s+`<rect x="${l}" y="${t}" width="${pw}" height="${ph}" fill="transparent" data-tip="${esc('Where the colored and gray bars overlap, people write alike. Median: '+d.med.toFixed(2)+' for '+name+', '+d.rest_med.toFixed(2)+' for others.')}"/>`;
}

function art(t){
 if(!t)return '<div class="badge" style="background:var(--line);color:var(--mute)">?</div>';
 if(AV[t])return `<img src="${AV[t]}" alt="${t} avatar">`;
 return `<div class="badge" style="background:${col(t)}">${t}</div>`;
}

function board(){
 const m=M.find(x=>x.k===cur);
 const rows=keys.map(c=>({c,v:mean(c,m.k),n:T[c].n})).sort((a,b)=>b.v-a.v);
 const mx=rows[0].v||1;
 $('bsub').textContent=m.u+' · average per person';
 $('rows').innerHTML=rows.map((r,i)=>`<div class="row${r.c===sel?' me':''}" data-tip="${esc(r.c+': '+m.f(r.v)+' ('+m.u+'), n='+r.n.toLocaleString())}"><span class="rk">${i+1}</span><span class="pill" style="background:${col(r.c)}">${r.c}</span><span class="bar"><i style="width:${r.v/mx*100}%;background:repeating-linear-gradient(90deg,${col(r.c)} 0 4px,transparent 4px 6px)"></i></span><span class="val">${m.f(r.v)}${r.n<100?'*':''}</span></div>`).join('');
 [...$('tabs').children].forEach(b=>b.classList.toggle('on',b.dataset.k===cur));
}

function render(){
 sel=$('sel').value;
 const has=!!sel;
 document.documentElement.style.setProperty('--mine',has?col(sel):'#5be08f');
 $('name').textContent=sel||'Pick a type';
 $('name').classList.toggle('ph',!has);
 $('art').innerHTML=art(sel);
 $('empty').style.display=has?'none':'flex';
 $('panels').style.display=has?'grid':'none';
 board();
 if(!has){$('nick').textContent='';$('tag').textContent='';$('meta').textContent='';$('warn').style.display='none';$('lg').innerHTML='';return;}
 const d=T[sel],n=d.n,rn=N-n;
 $('nick').textContent=INFO[sel]?INFO[sel][0]:'';
 $('tag').textContent=INFO[sel]?INFO[sel][1]:'';
 $('meta').textContent=`${n.toLocaleString()} people · ${(n/N*100).toFixed(n/N<0.1?1:0)}% of ${N.toLocaleString()}`;
 $('warn').style.display=n<100?'block':'none';
 $('lg').innerHTML=`<i style="background:var(--mine)"></i>${sel} (n=${n.toLocaleString()})<i style="background:var(--rest)"></i>Others (n=${rn.toLocaleString()})`;
 const rmean=m=>(tot.sums[m]-d.sums[m])/rn,own=m=>d.sums[m]/n;
 const rel=(v,o)=>{const r=(v/o-1)*100;return (r>=0?'+':'')+r.toFixed(0)+'% vs others'};
 const k2=['self_words','other_words'],L2=['I / me / my','you / we / us'];
 const k3=['love_family','mbti_talk','hobbies'],L3=['Love & family','MBTI talk','Hobbies'];
 $('c1').innerHTML=hist(d,sel);
 $('c2').innerHTML=bars(k2.map(own),k2.map(rmean),L2,dec,(v,o,i)=>`${L2[i]}: ${sel} ${dec(v)} vs others ${dec(o)} per post (${rel(v,o)})`);
 $('c3').innerHTML=bars(k3.map(own),k3.map(rmean),L3,pct,(v,o,i)=>`${L3[i]}: ${pct(v)} of ${sel} posts vs ${pct(o)} for others (${rel(v,o)})`);
}

function fit(){
 const s=Math.min(innerWidth/1280,innerHeight/760)*0.97,st=$('stage');
 st.style.transform=`scale(${s})`;
 st.style.left=(innerWidth-1280*s)/2+'px';st.style.top=(innerHeight-760*s)/2+'px';
}
document.addEventListener('mousemove',e=>{
 const g=e.target.closest('[data-tip]'),tp=$('tip');
 if(!g){tp.style.display='none';return;}
 tp.textContent=g.getAttribute('data-tip');tp.style.display='block';
 tp.style.left=Math.min(e.clientX+14,innerWidth-266)+'px';tp.style.top=(e.clientY+14)+'px';
});
$('tabs').addEventListener('click',e=>{const b=e.target.closest('button');if(b){cur=b.dataset.k;board();}});
$('sel').addEventListener('change',render);
addEventListener('resize',fit);fit();render();
</script></body></html>"""

signature = tuple((p.name, p.stat().st_mtime) for p in avatar_files()) + (
    (HERE / "mbti_dashboard.csv").stat().st_mtime,
)
payload = build_payload(signature)
components.html(TEMPLATE.replace("__DATA__", json.dumps(payload)), height=700, scrolling=False)