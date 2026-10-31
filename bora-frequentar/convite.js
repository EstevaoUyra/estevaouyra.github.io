/* Janela "Convidar alguém": monta uma mensagem de convite para um lugar e manda no WhatsApp.
   Usada na lista (index.html) e nas páginas de cada lugar.
   Convite.abrir(x, extra) — x é o item de D; extra = {unidades:[...], precos:{itens:[...]}} */
(function(){
const BASE="https://estevaouyra.github.io/bora-frequentar/";
const slug=s=>s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
const url=x=>BASE+slug(x.name)+"/";
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* "no Balaio IMS", "na Cuia", "na Casa do Porco" */
const FEM=["Cuia","Taberna 474","Adega Santiago","Casa Europa","Cervejaria Central","La Guapa","Mamma Vanzetto","Heavy House","WeProtein"];
function noNa(name){
  if(/^A /.test(name))return "na "+name.slice(2);
  if(/^O /.test(name))return "no "+name.slice(2);
  return (FEM.includes(name)?"na ":"no ")+name;
}
/* O que fazer lá, conforme o tipo. O primeiro é o padrão. */
function verbos(x){
  if(x.b==="Delivery")return [{v:"pedir um "+x.name,s:"Pedir"}];
  const n=noNa(x.name);
  const V={
    "Samba":/samba/i.test(x.name)?[["ir "+n,"Ir no samba"],["tomar uma "+n,"Tomar uma"]]:[["ir pro samba "+n,"Ir pro samba"],["tomar uma "+n,"Tomar uma"]],
    "Bar":[["tomar uma "+n,"Tomar uma"],["jantar "+n,"Jantar"],["comemorar alguma coisa "+n,"Comemorar"]],
    "Restaurante":[["jantar "+n,"Jantar"],["almoçar "+n,"Almoçar"],["comemorar alguma coisa "+n,"Comemorar"]],
    "Alta gastronomia":[["jantar "+n,"Jantar"],["comemorar alguma coisa "+n,"Comemorar"],["almoçar "+n,"Almoçar"]],
    "Rápido / empório":[["dar uma passada "+n,"Dar uma passada"],["fazer um lanche "+n,"Lanchar"]]
  }[x.t]||[["ir "+n,"Ir"]];
  return V.map(([v,s])=>({v,s}));
}
const QUANDO=[["hoje","Hoje"],["amanhã","Amanhã"],["nessa sexta","Sexta"],["no fim de semana","Fim de semana"],["semana que vem","Semana que vem"],["","Sem data"]];

function onde(x,un){
  if(un&&un.length>1){const ns=un.map(u=>u.nome);return "Tem unidades em "+(ns.length>4?ns.slice(0,4).join(", ")+" e mais "+(ns.length-4):ns.slice(0,-1).join(", ")+" e "+ns[ns.length-1])+".";}
  if(x.b==="Delivery")return "Funciona por delivery.";
  const bairro=x.b.replace(/ \(.*\)$/,"");
  return "📍 "+x.ref.replace(/\.$/,"")+(x.ref.includes(bairro.split(" / ")[0])?"":" ("+bairro+")");
}
function dica(pr){
  if(!pr||!pr.itens||!pr.itens.length)return "";
  const it=pr.itens.find(i=>!/água|agua|coca|refri|guaran|cerveja|heineken|chope|original|corona|litrão/i.test(i.item))||pr.itens[0];
  return "Dica: "+it.item.charAt(0).toLowerCase()+it.item.slice(1)+" por "+it.preco+".";
}
const PORQUE="Eles se posicionaram em defesa da democracia e estão sendo boicotados. Bora fortalecer!";

function texto(x,o,ex){
  const q=o.quando?" "+o.quando:"";
  const linhas=["Que tal "+o.verbo+q+"?"];
  if(o.inc.oque)linhas.push(x.d);
  if(o.inc.onde)linhas.push(onde(x,ex.unidades));
  if(o.inc.preco&&dica(ex.precos))linhas.push(dica(ex.precos));
  let t=linhas[0]+(linhas.length>1?"\n\n"+linhas.slice(1).join("\n"):"");
  if(o.inc.porque)t+="\n\n"+PORQUE;
  return t+"\n\n"+url(x);
}

const CSS=`
.cv-dlg{border:0;padding:0;border-radius:16px;width:min(520px,calc(100vw - 24px));max-height:calc(100dvh - 24px);background:var(--surface);color:var(--ink);box-shadow:0 20px 60px rgba(0,0,0,.35)}
.cv-dlg::backdrop{background:rgba(10,20,17,.55)}
.cv-in{padding:18px 18px 16px;display:flex;flex-direction:column;gap:14px}
.cv-top{display:flex;justify-content:space-between;align-items:start;gap:12px}
.cv-top h2{font:800 22px/1.1 var(--display);margin:0;letter-spacing:-.01em}
.cv-top p{margin:4px 0 0;font-size:13px;color:var(--muted)}
.cv-x{flex:none;font:600 20px/1 var(--body);background:none;border:0;color:var(--muted);cursor:pointer;padding:4px 6px;border-radius:8px}
.cv-g{display:flex;flex-direction:column;gap:6px}
.cv-g>span{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}
.cv-ops{display:flex;flex-wrap:wrap;gap:6px}
.cv-ops button{font:500 13px var(--body);border:1px solid var(--line);background:var(--bg);color:var(--ink);padding:6px 11px;border-radius:999px;cursor:pointer}
.cv-ops button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.cv-ops.chk button[aria-pressed="true"]::before{content:"✓ "}
.cv-msg{width:100%;min-height:150px;font:14px/1.45 var(--body);padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);resize:vertical}
.cv-acts{display:flex;gap:8px;flex-wrap:wrap}
.cv-acts a,.cv-acts button{flex:1 1 auto;display:inline-flex;justify-content:center;align-items:center;gap:8px;font:600 15px var(--body);text-decoration:none;border-radius:12px;padding:12px 16px;border:1px solid var(--line);background:var(--bg);color:var(--ink);cursor:pointer}
.cv-acts .wa{background:#25D366;border-color:#25D366;color:#0B2A17;flex-basis:100%}
.cv-acts svg{width:18px;height:18px}
.cv-dlg button:focus-visible,.cv-dlg a:focus-visible,.cv-msg:focus-visible{outline:2px solid var(--mark);outline-offset:2px}
`;
const WA='<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2c0 1.3.9 2.5 1 2.7.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2l-.5-.3Z"/></svg>';

let dlg;
function abrir(x,ex={}){
  if(!document.getElementById("cv-css")){const s=document.createElement("style");s.id="cv-css";s.textContent=CSS;document.head.appendChild(s)}
  dlg?.remove();
  const vs=verbos(x),temPreco=!!dica(ex.precos);
  const o={verbo:vs[0].v,quando:x.b==="Delivery"?"hoje":"no fim de semana",inc:{oque:true,onde:x.b!=="Delivery",preco:false,porque:true}};
  dlg=document.createElement("dialog");dlg.className="cv-dlg";dlg.setAttribute("aria-labelledby","cv-t");
  const grupo=(nome,ops,chk)=>`<div class="cv-g"><span>${nome}</span><div class="cv-ops${chk?" chk":""}">${ops}</div></div>`;
  const b=(k,v,label,on)=>`<button type="button" data-k="${k}" data-v="${esc(v)}" aria-pressed="${on}">${esc(label)}</button>`;
  dlg.innerHTML=`<div class="cv-in">
    <div class="cv-top"><div><h2 id="cv-t">Convidar alguém</h2><p>${esc(x.name)} · escolha as opções e ajuste a mensagem se quiser.</p></div><button class="cv-x" type="button" aria-label="Fechar">✕</button></div>
    ${vs.length>1?grupo("Pra quê",vs.map(y=>b("verbo",y.v,y.s,y.v===o.verbo)).join("")):""}
    ${grupo("Quando",QUANDO.map(([v,l])=>b("quando",v,l,v===o.quando)).join(""))}
    ${grupo("Incluir na mensagem",[["oque","O que é"],["onde","Onde fica"],...(temPreco?[["preco","Dica de preço"]]:[]),["porque","Por que ir"]].map(([k,l])=>b("inc",k,l,o.inc[k])).join(""),true)}
    <textarea class="cv-msg" aria-label="Mensagem"></textarea>
    <div class="cv-acts"><a class="wa" href="#" target="_blank" rel="noopener">${WA}Mandar no WhatsApp</a><button type="button" class="cv-cp">Copiar</button>${navigator.share?'<button type="button" class="cv-sh">Outros apps</button>':""}</div>
  </div>`;
  document.body.appendChild(dlg);
  const msg=dlg.querySelector(".cv-msg"),wa=dlg.querySelector(".wa");
  const upd=()=>{msg.value=texto(x,o,ex);syncWa()};
  const syncWa=()=>{wa.href="https://wa.me/?text="+encodeURIComponent(msg.value)};
  msg.addEventListener("input",syncWa);
  dlg.addEventListener("click",e=>{
    if(e.target===dlg||e.target.closest(".cv-x")){dlg.close();return}
    const t=e.target.closest("[data-k]");if(!t)return;
    const k=t.dataset.k,v=t.dataset.v;
    if(k==="inc"){o.inc[v]=!o.inc[v];t.setAttribute("aria-pressed",o.inc[v])}
    else{o[k]=v;t.parentElement.querySelectorAll("button").forEach(c=>c.setAttribute("aria-pressed",c===t))}
    upd();
  });
  dlg.querySelector(".cv-cp").onclick=async e=>{const btn=e.currentTarget;try{await navigator.clipboard.writeText(msg.value);btn.textContent="Copiado!"}catch(_){msg.select();btn.textContent="Selecionado, copie"}setTimeout(()=>btn.textContent="Copiar",1800)};
  const sh=dlg.querySelector(".cv-sh");
  if(sh)sh.onclick=()=>{const t=msg.value,u=url(x);navigator.share({text:t.replace(u,"").trim(),url:u}).catch(()=>{})};
  dlg.addEventListener("close",()=>dlg.remove());
  upd();
  dlg.showModal();
  msg.blur();dlg.querySelector(".cv-x").focus();
}
window.Convite={abrir,slug,url};
})();
