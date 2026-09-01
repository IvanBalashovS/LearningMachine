#!/usr/bin/env python3
"""Солнечная система 3D (софт-рендер) — сервер на стандартной библиотеке"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8081

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Солнечная система 3D</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000;font-family:system-ui,sans-serif;color:#fff}
canvas{display:block;cursor:grab}
canvas:active{cursor:grabbing}
#panel{
position:fixed;top:0;right:-380px;width:340px;height:100vh;
background:rgba(8,8,28,.95);padding:28px 20px;
transition:right .4s;z-index:100;backdrop-filter:blur(10px);
border-left:1px solid rgba(255,255,255,.08);overflow-y:auto
}
#panel.open{right:0}
#panel .close{position:absolute;top:12px;right:16px;background:none;border:none;
color:rgba(255,255,255,.4);font-size:22px;cursor:pointer}
#panel .close:hover{color:#fff}
#panel h2{font-size:24px;margin-bottom:2px}
#panel .sub{color:rgba(255,255,255,.35);font-size:13px;margin-bottom:14px}
#panel .row{margin-bottom:10px}
#panel .row label{display:block;font-size:10px;text-transform:uppercase;
letter-spacing:1px;color:rgba(255,255,255,.25);margin-bottom:1px}
#panel .row p{font-size:14px;line-height:1.4;color:rgba(255,255,255,.8)}
#hint{
position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
color:rgba(255,255,255,.2);font-size:12px;pointer-events:none;z-index:10;
text-align:center;background:rgba(255,255,255,.04);padding:6px 16px;
border-radius:16px;backdrop-filter:blur(4px)
}
#controls{
position:fixed;bottom:70px;left:50%;transform:translateX(-50%);
display:flex;align-items:center;gap:10px;
background:rgba(255,255,255,.06);padding:8px 18px;
border-radius:20px;backdrop-filter:blur(6px);
z-index:50;border:1px solid rgba(255,255,255,.08)
}
.ctrl-btn{
width:32px;height:32px;border-radius:50%;border:1px solid rgba(255,255,255,.2);
background:rgba(255,255,255,.05);color:#fff;font-size:18px;
cursor:pointer;display:flex;align-items:center;justify-content:center;
transition:all .15s
}
.ctrl-btn:hover{background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.4)}
#scale-val{font-size:15px;min-width:24px;text-align:center;color:rgba(255,255,255,.7)}
.ctrl-label{font-size:11px;color:rgba(255,255,255,.3);margin-left:4px}

#loading{
position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
background:#000;z-index:200;color:rgba(255,255,255,.5);
font-size:16px;transition:opacity .4s
}
#loading.hide{opacity:0;pointer-events:none}
</style>
</head>
<body>
<div id="loading">Загрузка...</div>

<div id="panel">
<button class="close" onclick="closeP()">&times;</button>
<h2 id="p-name"></h2>
<div class="sub" id="p-type"></div>
<div class="row"><label>Описание</label><p id="p-desc"></p></div>
<div class="row"><label>Диаметр</label><p id="p-diam"></p></div>
<div class="row"><label>Расстояние от Солнца</label><p id="p-dist"></p></div>
<div class="row"><label>Период обращения</label><p id="p-per"></p></div>
<div class="row"><label>Температура</label><p id="p-temp"></p></div>
</div>

<div id="controls">
<button id="btn-minus" class="ctrl-btn">−</button>
<span id="scale-val">5</span>
<button id="btn-plus" class="ctrl-btn">+</button>
<span class="ctrl-label">размер планет</span>
</div>

<div id="hint"><span>Мышь: вращение · Колёсико: зум · Клик по планете: инфо</span></div>

<canvas id="c"></canvas>

<script>
// ===== Planet data (realistic size ratios) =====
const SUN_DIAM = 1391000; // km

const PLANET_DATA = [
{id:'sun',name:'Солнце',type:'Звезда',
desc:'Солнце — звезда, центральное тело Солнечной системы. Состоит в основном из водорода и гелия.',
diam:'1 391 000 км',dist:'—',per:'—',temp:'5 500 °C',
color:'#fdb813',diamKm:SUN_DIAM,orbit:0,speed:0,labelOffset:8},
{id:'mercury',name:'Меркурий',type:'Планета земной группы',
desc:'Самая маленькая и ближайшая к Солнцу планета. Поверхность покрыта кратерами.',
diam:'4 879 км',dist:'57.9 млн км',per:'88 дней',temp:'-180..+430 °C',
color:'#b5b5b5',diamKm:4879,orbit:14,speed:.026,labelOffset:3},
{id:'venus',name:'Венера',type:'Планета земной группы',
desc:'Вторая планета от Солнца. Плотная токсичная атмосфера создаёт мощный парниковый эффект.',
diam:'12 104 км',dist:'108.2 млн км',per:'225 дней',temp:'462 °C',
color:'#e8cda0',diamKm:12104,orbit:20,speed:.019,labelOffset:4},
{id:'earth',name:'Земля',type:'Планета земной группы',
desc:'Третья планета от Солнца. Единственное известное тело во Вселенной с живыми организмами.',
diam:'12 742 км',dist:'149.6 млн км',per:'365.25 дней',temp:'-89..+57 °C',
color:'#4b7be5',diamKm:12742,orbit:26,speed:.016,labelOffset:4},
{id:'mars',name:'Марс',type:'Планета земной группы',
desc:'Четвёртая планета. Красноватый цвет из-за оксида железа. Имеет самую высокую гору — Олимп.',
diam:'6 779 км',dist:'227.9 млн км',per:'687 дней',temp:'-140..+20 °C',
color:'#d4735e',diamKm:6779,orbit:32,speed:.013,labelOffset:3},
{id:'jupiter',name:'Юпитер',type:'Газовый гигант',
desc:'Самая большая планета. Состоит из водорода и гелия. Известен Большим Красным Пятном.',
diam:'139 820 км',dist:'778.5 млн км',per:'11.86 лет',temp:'-110 °C',
color:'#d4a574',diamKm:139820,orbit:48,speed:.008,labelOffset:8},
{id:'saturn',name:'Сатурн',type:'Газовый гигант',
desc:'Шестая планета, известна системой колец из частиц льда и камня.',
diam:'116 460 км',dist:'1.43 млрд км',per:'29.46 лет',temp:'-140 °C',
color:'#ead6b8',diamKm:116460,orbit:60,speed:.006,labelOffset:7},
{id:'uranus',name:'Уран',type:'Ледяной гигант',
desc:'Седьмая планета. Голубоватый цвет из-за метана. Ось наклонена почти на 98°.',
diam:'50 724 км',dist:'2.87 млрд км',per:'84 года',temp:'-195 °C',
color:'#7ec8e3',diamKm:50724,orbit:72,speed:.004,labelOffset:5},
{id:'neptune',name:'Нептун',type:'Ледяной гигант',
desc:'Самая дальняя планета. Скорость ветра достигает 2100 км/ч. Ярко-синий цвет.',
diam:'49 244 км',dist:'4.5 млрд км',per:'164.8 года',temp:'-200 °C',
color:'#3b5cf5',diamKm:49244,orbit:84,speed:.003,labelOffset:5}
];

// scale: map sun to 1 unit visually, keep exact ratios
const SUN_R = 1;
let visualScale = 5; // начальное значение
const scale = SUN_R / SUN_DIAM;
for(const p of PLANET_DATA){
p.r = p.diamKm * scale * 8;
if(p.id==='sun')p.r=SUN_R;
}

const DATA = {};
for(const p of PLANET_DATA) DATA[p.id]=p;

const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
let W,H;

function resize(){
W=canvas.width=window.innerWidth;
H=canvas.height=window.innerHeight;
}
resize();
window.addEventListener('resize',resize);

// ===== 3D Camera =====
let theta = Math.PI/4;     // horizontal angle
let phi = Math.PI/3;       // vertical angle
let camDist = 120;         // distance from origin
let targetX=0, targetY=0, targetZ=0;
let fov = 60; // degrees

function getCameraPos(){
return[
camDist*Math.sin(phi)*Math.cos(theta),
camDist*Math.cos(phi),
camDist*Math.sin(phi)*Math.sin(theta)
];
}

// ===== 3D Math =====
function vecSub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
function vecAdd(a,b){return [a[0]+b[0],a[1]+b[1],a[2]+b[2]];}
function vecScale(v,s){return [v[0]*s,v[1]*s,v[2]*s];}
function vecDot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function vecLen(v){return Math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);}
function vecNorm(v){const l=vecLen(v);return l?[v[0]/l,v[1]/l,v[2]/l]:[0,0,0];}
function vecCross(a,b){return[
a[1]*b[2]-a[2]*b[1],
a[2]*b[0]-a[0]*b[2],
a[0]*b[1]-a[1]*b[0]
];}

// lookAt matrix
function lookAt(eye, center, up){
const f=vecNorm(vecSub(center,eye));
const s=vecNorm(vecCross(f,up));
const u=vecCross(s,f);
return[
s[0],u[0],-f[0],0,
s[1],u[1],-f[1],0,
s[2],u[2],-f[2],0,
-vecDot(s,eye),-vecDot(u,eye),vecDot(f,eye),1
];
}

// perspective matrix
function perspective(fovDeg, aspect, near, far){
const f=1/Math.tan(fovDeg*Math.PI/360);
const nf=1/(near-far);
return[
f/aspect,0,0,0,
0,f,0,0,
0,0,(far+near)*nf,-1,
0,0,2*far*near*nf,0
];
}

// transform 4D vector by 4x4 matrix
function transform(m,v){
return[
m[0]*v[0]+m[4]*v[1]+m[8]*v[2]+m[12]*v[3],
m[1]*v[0]+m[5]*v[1]+m[9]*v[2]+m[13]*v[3],
m[2]*v[0]+m[6]*v[1]+m[10]*v[2]+m[14]*v[3],
m[3]*v[0]+m[7]*v[1]+m[11]*v[2]+m[15]*v[3]
];
}

// world → screen
const NEAR=0.1, FAR=500;

function worldToScreen(world){
const eye=getCameraPos();
const view=lookAt(eye,[targetX,targetY,targetZ],[0,1,0]);
const aspect=W/H;
const proj=perspective(fov,aspect,NEAR,FAR);

const v=transform(view,[world[0],world[1],world[2],1]);
const p=transform(proj,v);

if(p[3]===0)return null;
const ndc=[p[0]/p[3],p[1]/p[3],p[2]/p[3]];
if(ndc[2]>1)return null; // behind camera

return[(ndc[0]+1)*W/2,(-ndc[1]+1)*H/2,ndc[2]];
}

// compute projected radius
function projectedRadius(world, r){
const eye=getCameraPos();
const d=vecLen(vecSub(world,eye));
if(d<NEAR)return 0;
// screen radius ≈ W/2 * (r/d) / tan(fov/2)
return(W/2)*(r/d)/Math.tan(fov*Math.PI/360);
}

// ===== Orbit Controls =====
let drag=false, prevX, prevY;
let panMode=false;

canvas.addEventListener('mousedown',e=>{
drag=true;prevX=e.clientX;prevY=e.clientY;
panMode=e.button===1||e.button===2;
});
window.addEventListener('mousemove',e=>{
if(!drag)return;
const dx=e.clientX-prevX,dy=e.clientY-prevY;
if(panMode){
// pan
const s=camDist*0.003;
targetX-=dx*Math.cos(theta)*s;
targetZ+=dx*Math.sin(theta)*s;
targetY+=dy*s;
}else{
theta-=dx*0.008;
phi=Math.max(0.05,Math.min(Math.PI-0.05,phi+dy*0.008));
}
prevX=e.clientX;prevY=e.clientY;
});
window.addEventListener('mouseup',()=>{drag=false});
window.addEventListener('contextmenu',e=>e.preventDefault());

canvas.addEventListener('wheel',e=>{
e.preventDefault();
const f=e.deltaY>0?1.08:1/1.08;
camDist=Math.max(5,Math.min(400,camDist*f));
},{passive:false});

// ===== Click detection =====
canvas.addEventListener('click',e=>{
const rect=canvas.getBoundingClientRect();
const mx=e.clientX-rect.left, my=e.clientY-rect.top;

// find closest hit
let best=null,bestDist=Infinity;
for(const p of PLANET_DATA){
if(p.id==='sun')continue;
const w=[p.wx,p.wy,p.wz];
const s=worldToScreen(w);
if(!s)continue;
const dx=mx-s[0],dy=my-s[1];
// include visualScale for click area
const screenR=projectedRadius(w,p.r*visualScale);
if(dx*dx+dy*dy<screenR*screenR){
const d=s[2]; // depth
if(d<bestDist){bestDist=d;best=p;}
}
}
// check sun
if(!best){
const ws=[0,0,0];
const ss=worldToScreen(ws);
if(ss){
const dx=mx-ss[0],dy=my-ss[1];
    const sunR=projectedRadius(ws,SUN_R*visualScale);
    if(dx*dx+dy*dy<sunR*sunR)best=PLANET_DATA[0];
}
}
if(best)openPanel(best);
});

function openPanel(p){
document.getElementById('p-name').textContent=p.name;
document.getElementById('p-type').textContent=p.type;
document.getElementById('p-desc').textContent=p.desc;
document.getElementById('p-diam').textContent=p.diam;
document.getElementById('p-dist').textContent=p.dist;
document.getElementById('p-per').textContent=p.per;
document.getElementById('p-temp').textContent=p.temp;
document.getElementById('panel').classList.add('open');
}
window.closeP=()=>document.getElementById('panel').classList.remove('open');
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeP()});

// ===== Управление масштабом планет (кнопки + и -) =====
const scaleValSpan = document.getElementById('scale-val');
const btnMinus = document.getElementById('btn-minus');
const btnPlus = document.getElementById('btn-plus');

function updateScaleUI() {
    scaleValSpan.textContent = visualScale;
}

// Обработчик для кнопки минус
btnMinus.addEventListener('click', () => {
    visualScale = Math.max(1, visualScale - 1);
    updateScaleUI();
});

// Обработчик для кнопки плюс
btnPlus.addEventListener('click', () => {
    visualScale = Math.min(10, visualScale + 1);
    updateScaleUI();
});

// Инициализация отображения значения
updateScaleUI();

// ===== Drawing =====
let animTime=0;
let lastTime=0;

function draw(t){
const dt=lastTime?(t-lastTime)/1000:0.016;
lastTime=t;
animTime+=dt;

// planet positions
for(const p of PLANET_DATA){
if(p.id==='sun'){p.wx=0;p.wy=0;p.wz=0;continue;}
const angle=animTime*p.speed;
p.wx=p.orbit*Math.cos(angle);
p.wz=p.orbit*Math.sin(angle);
p.wy=0;
}

// clear
ctx.fillStyle='#000005';
ctx.fillRect(0,0,W,H);

// stars in world space
const eye=getCameraPos();
for(let i=0;i<300;i++){
const sx=Math.sin(i*137.508)*400;
const sy=Math.sin(i*99.718+54321)*400;
const sz=Math.cos(i*73.117+12345)*400;
const ss=worldToScreen([sx,sy,sz]);
if(!ss)continue;
const sz2=(sz+400)/800;
ctx.fillStyle=`rgba(255,255,255,${0.1+sz2*0.4})`;
const size=0.5+sz2;
ctx.fillRect(ss[0]-size/2,ss[1]-size/2,size,size);
}

// collect visible objects with depth
const objects=[];

for(const p of PLANET_DATA){
const w=[p.wx,p.wy,p.wz];
const s=worldToScreen(w);
if(!s)continue;
// Для планет применяем visualScale, для Солнца — нет (оставляем фиксированный размер)
const finalRadius = p.id === 'sun' ? p.r : p.r * visualScale;
const screenR=projectedRadius(w, finalRadius);
if(screenR<0.5)continue;
objects.push({
p, world:w, screen:s, r:screenR,
depth:-s[2]
});
}

// sort by depth (far first)
objects.sort((a,b)=>a.depth-b.depth);

// render
for(const o of objects){
const[w,wy,z]=o.world;
const[sx,sy]=o.screen;
const r=o.r;
const p=o.p;

// lighting: normal = normalized vector from sphere center to camera
const toCam=vecNorm(vecSub(eye,[w,wy,z]));
const diff=Math.max(0.1,toCam[1]*0.5+0.5);

const baseColor=p.color||'#888';

if(p.id==='sun'){
// sun glow layers (уменьшенные эффекты для маленького солнца)
for(let i=0;i<2;i++){
const gr=ctx.createRadialGradient(sx,sy,0,sx,sy,r*(2+i*1.5));
gr.addColorStop(0,`rgba(253,184,19,${0.12-i*0.03})`);
gr.addColorStop(1,'rgba(253,184,19,0)');
ctx.fillStyle=gr;
ctx.beginPath();ctx.arc(sx,sy,r*(2+i*1.5),0,Math.PI*2);
ctx.fill();
}
// sun body
const cg=ctx.createRadialGradient(sx-r*0.15,sy-r*0.15,0,sx,sy,r);
cg.addColorStop(0,'rgba(255,230,130,1)');
cg.addColorStop(0.4,'rgba(253,200,50,1)');
cg.addColorStop(0.7,'rgba(240,160,20,0.9)');
cg.addColorStop(1,'rgba(200,120,10,0.5)');
ctx.fillStyle=cg;
ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);
ctx.fill();

// label
ctx.font='13px system-ui';
ctx.textAlign='center';
ctx.fillStyle='rgba(255,255,255,0.4)';
ctx.fillText(p.name,sx,sy+r+p.labelOffset+2);
continue;
}

// sphere gradient with lighting
const grad=ctx.createRadialGradient(
sx-r*0.3*diff,sy-r*0.3*diff,0,
sx,sy,r
);
grad.addColorStop(0,lighten(baseColor,30+30*diff));
grad.addColorStop(0.6,lighten(baseColor,10*diff));
grad.addColorStop(0.85,baseColor);
grad.addColorStop(1,darken(baseColor,50));

ctx.fillStyle=grad;
ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);
ctx.fill();

// saturn ring
if(p.id==='saturn' && r>3){
ctx.save();
ctx.translate(sx,sy);
ctx.rotate(-0.4);
ctx.strokeStyle='rgba(200,184,154,0.4)';
ctx.lineWidth=Math.max(1,r*0.2);
ctx.beginPath();
ctx.ellipse(0,0,r*1.8,r*0.55,0,0,Math.PI*2);
ctx.stroke();
ctx.restore();
}

// orbit line
ctx.strokeStyle='rgba(100,130,200,0.4)';
ctx.lineWidth=1.2;
ctx.beginPath();
const segs=64;
let first=true;
for(let i=0;i<=segs;i++){
const a=i/segs*Math.PI*2;
const w2=[p.orbit*Math.cos(a),0,p.orbit*Math.sin(a)];
const s2=worldToScreen(w2);
if(s2){
if(first){ctx.moveTo(s2[0],s2[1]);first=false;}
else ctx.lineTo(s2[0],s2[1]);
}
}
ctx.stroke();

// label
const fontSize=Math.max(8,Math.min(13,r*0.8));
ctx.font=`${fontSize}px system-ui`;
ctx.textAlign='center';
ctx.fillStyle='rgba(255,255,255,0.35)';
ctx.fillText(p.name,sx,sy+r+p.labelOffset+2);
} // end for objects

requestAnimationFrame(draw);
}

function lighten(hex,pct){
const n=parseInt(hex.slice(1),16);
const r=Math.min(255,(n>>16)+pct);
const g=Math.min(255,((n>>8)&255)+pct);
const b=Math.min(255,(n&255)+pct);
return`rgb(${r},${g},${b})`;
}
function darken(hex,pct){
const n=parseInt(hex.slice(1),16);
const r=Math.max(0,(n>>16)-pct);
const g=Math.max(0,((n>>8)&255)-pct);
const b=Math.max(0,(n&255)-pct);
return`rgb(${r},${g},${b})`;
}

document.getElementById('loading').classList.add('hide');
requestAnimationFrame(draw);
</script>
</body>
</html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    class Server(socketserver.TCPServer):
        allow_reuse_address = True
    url = f"http://localhost:{PORT}/"
    print(f"Солнечная система 3D: {url}")
    print("Ctrl+C для остановки.")
    webbrowser.open(url)
    with Server(("0.0.0.0", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")