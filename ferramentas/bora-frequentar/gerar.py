"""Gera uma página por lugar do guia "Bora frequentar SP", com imagem de prévia para o WhatsApp.

Os dados vêm do próprio bora-frequentar/index.html (D, UN, PRECO, GEO e COR).
Depois de mudar algum dado lá, rode de novo:

    python3 ferramentas/bora-frequentar/gerar.py

Cria bora-frequentar/<slug>/index.html e bora-frequentar/<slug>/og.png para cada lugar.
Precisa de node (para ler os dados em JS) e Pillow (para as imagens).
"""
import html, json, re, subprocess, unicodedata
from urllib.parse import quote_plus
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
GUIA = RAIZ / "bora-frequentar"
FONTES = Path(__file__).resolve().parent / "fontes"
BASE = "https://estevaouyra.github.io/bora-frequentar/"


def ler_dados():
    s = (GUIA / "index.html").read_text(encoding="utf-8")
    pedacos = [
        re.search(r"const D=\[\n.*?\n\];", s, re.S).group(0),
        re.search(r"const UN=.*?;\n", s).group(0),
        re.search(r"const PRECO=.*?;\n", s).group(0),
        re.search(r"const GEO=\{.*?\};", s, re.S).group(0),
        re.search(r"const COR=.*?;\n", s).group(0),
    ]
    js = "\n".join(pedacos) + "\nprocess.stdout.write(JSON.stringify({D,UN,PRECO,GEO,COR}))"
    return json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)


def slug(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


e = lambda s: html.escape(str(s), quote=True)


# ---------- imagem de prévia (1200x630) ----------
VERDE, CLARO, TINTA, AMARELO, SUAVE = (13, 107, 91), (244, 246, 243), (24, 34, 31), (226, 165, 43), (200, 228, 219)


def fonte(nome, tamanho, eixos):
    f = ImageFont.truetype(str(FONTES / nome), tamanho)
    f.set_variation_by_axes(eixos)
    return f


def quebrar(d, texto, f, largura):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=f) <= largura:
            atual = t
        else:
            linhas.append(atual)
            atual = p
    return linhas + [atual] if atual else linhas


def imagem(x, destino):
    W, H, M = 1200, 630, 64
    im = Image.new("RGB", (W, H), VERDE)
    d = ImageDraw.Draw(im)
    d.text((M, 52), "BORA FREQUENTAR SP", font=fonte("IBMPlexSans.ttf", 26, [600, 100]), fill=SUAVE)
    # nome: o maior tamanho que caiba em até 2 linhas
    for tam in range(132, 50, -4):
        f = fonte("BricolageGrotesque.ttf", tam, [96, 800, 100])
        linhas = quebrar(d, x["name"], f, W - 2 * M)
        if len(linhas) <= 2:
            break
    y = 100
    for ln in linhas:
        d.text((M, y), ln, font=f, fill=CLARO)
        y += int(tam * 0.98)
    # etiqueta amarela com tipo e bairro
    ft = fonte("IBMPlexSans.ttf", 28, [700, 100])
    etiqueta = f"{x['t']} · {re.sub(r' \(.*\)$', '', x['b'])}"
    w = d.textlength(etiqueta, font=ft)
    y += 26
    d.rounded_rectangle([M, y, M + w + 32, y + 50], radius=10, fill=AMARELO)
    d.text((M + 16, y + 8), etiqueta, font=ft, fill=TINTA)
    y += 76
    fd = fonte("IBMPlexSans.ttf", 30, [500, 100])
    for ln in quebrar(d, x["d"], fd, W - 2 * M)[: max(1, (H - 90 - y) // 42)]:
        d.text((M, y), ln, font=fd, fill=CLARO)
        y += 42
    d.text((M, H - 70), "Defendeu a democracia e sofre boicote. Bora frequentar!", font=fonte("IBMPlexSans.ttf", 26, [600, 100]), fill=SUAVE)
    im.save(destino, optimize=True)


# ---------- página ----------
CSS = """
:root{
  --bg:#F4F6F3; --surface:#FFFFFF; --ink:#18221F; --muted:#5C6A65; --line:#DCE3DF;
  --accent:#0D6B5B; --accent-soft:#DDEFE9; --mark:#E2A52B; --mark-soft:#FBF0D6;
  --display:"Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --body:"IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#111816; --surface:#18211E; --ink:#E7EEEA; --muted:#9AA8A2; --line:#2A3733;
  --accent:#4FC2A8; --accent-soft:#16332C; --mark:#F0BC52; --mark-soft:#3A2F14; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#111816; --surface:#18211E; --ink:#E7EEEA; --muted:#9AA8A2; --line:#2A3733;
  --accent:#4FC2A8; --accent-soft:#16332C; --mark:#F0BC52; --mark-soft:#3A2F14; color-scheme:dark}
*{box-sizing:border-box}
html{color-scheme:light}
body{margin:0;font-size:16px;background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.5;
  padding:0 max(16px,env(safe-area-inset-right,0px)) 56px max(16px,env(safe-area-inset-left,0px))}
.wrap{max-width:760px;margin:0 auto}
.voltar{display:inline-block;margin-top:20px;font-size:14px;font-weight:600;color:var(--accent);text-decoration:none}
.eyebrow{display:block;margin:24px 0 8px;font:600 13px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font:800 clamp(40px,10vw,72px)/.95 var(--display);letter-spacing:-.03em;margin:0;text-wrap:balance}
.pills{display:flex;gap:6px;flex-wrap:wrap;margin-top:14px}
.pill{font-size:13px;font-weight:600;padding:3px 9px;border-radius:6px;background:var(--mark-soft);color:var(--ink)}
.pill.t{background:var(--c);color:#fff}
.desc{font-size:clamp(18px,2.6vw,21px);line-height:1.45;margin:16px 0 0;text-wrap:pretty}
.cta{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font:600 15px var(--body);text-decoration:none;border-radius:12px;padding:12px 18px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.btn:hover{border-color:var(--accent)}
.btn.wa{background:#25D366;border-color:#25D366;color:#0B2A17}
.btn svg{width:18px;height:18px;flex:none}
@media (max-width:520px){.cta .btn{flex:1 1 calc(50% - 5px)}.cta .btn.wa{flex-basis:100%}}
.btn:focus-visible,.voltar:focus-visible{outline:2px solid var(--mark);outline-offset:2px}
section{margin-top:30px}
h2{font:800 22px/1.15 var(--display);margin:0 0 10px;letter-spacing:-.01em}
.fatos{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:6px 16px}
.fatos dl{margin:0}
.fatos div{display:grid;grid-template-columns:90px 1fr;gap:12px;padding:10px 0;border-top:1px solid var(--line)}
.fatos div:first-child{border-top:0}
.fatos dt{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600;padding-top:3px}
.fatos dd{margin:0}
.fatos ul{margin:0;padding:0;list-style:none}
.fatos li+li{margin-top:2px}
.fatos a{color:var(--accent)}
.note{font-size:14px;margin:12px 0 0;padding:8px 11px;border-left:3px solid var(--mark);background:var(--mark-soft);border-radius:0 8px 8px 0}
#map{height:min(55vh,380px);border:1px solid var(--line);border-radius:14px;background:var(--surface);z-index:0}
.pin{width:26px;height:26px;border-radius:50%;background:var(--c);border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)}
.leaflet-container{font-family:var(--body)}
.leaflet-popup-content-wrapper,.leaflet-popup-tip{background:var(--surface);color:var(--ink)}
.leaflet-popup-content a{color:var(--accent);font-weight:600}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.95) contrast(.9)}}
:root[data-theme="dark"] .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.95) contrast(.9)}
.precos{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 16px}
.precos ul{list-style:none;margin:0;padding:0}
.precos li{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-top:1px solid var(--line)}
.precos li:first-child{border-top:0}
.precos li small{color:var(--muted)}
.precos li b{flex:none;font-variant-numeric:tabular-nums;font-weight:600}
.precos p{margin:8px 0 0;font-size:13px;color:var(--muted)}
.precos p a{color:var(--accent)}
.ig .instagram-media{min-width:0!important;max-width:100%!important;width:100%!important;margin:0!important;border-radius:14px!important}
.porque{margin-top:36px;padding:20px;border-radius:14px;background:var(--accent);color:var(--bg)}
.porque h2{color:inherit}
.porque p{margin:0 0 14px}
.porque .btn{border-color:transparent;background:var(--bg);color:var(--ink)}
footer{margin-top:26px;font-size:13px;color:var(--muted)}
"""

ICONE_WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2c0 1.3.9 2.5 1 2.7.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2l-.5-.3Z"/></svg>'


def precos_html(p):
    if not p or not p.get("itens"):
        return ""
    bebida = lambda i: 0 if re.search(r"água|agua|coca|refri", i["item"], re.I) else 1
    itens = sorted(p["itens"], key=bebida)
    lis = "".join(f'<li><span>{e(i["item"])}{" <small>" + e(i["obs"]) + "</small>" if i.get("obs") else ""}</span><b>{e(i["preco"])}</b></li>' for i in itens)
    fontes = " ".join(f'<a href="{e(f)}" target="_blank" rel="noopener">{k + 1}</a>' for k, f in enumerate(p.get("fonte", [])))
    nota = (e(p["nota"]) + " ") if p.get("nota") else ""
    return f'<section><h2>Quanto custa</h2><div class="precos"><ul>{lis}</ul><p>{nota}Preços de {e(p.get("data", ""))}, podem ter mudado.{" Fontes: " + fontes if fontes else ""}</p></div></section>'


def pagina(x, dados):
    n = str(x["n"])
    un = dados["UN"].get(n)
    geo = dados["GEO"].get(n)
    pontos = [{"nome": u["nome"], "end": u["end"], "lat": u["lat"], "lng": u["lng"]} for u in un] if un else ([{"nome": "", "end": x["ref"], "lat": geo[0], "lng": geo[1]}] if geo else [])
    cor = dados["COR"][x["t"]]
    s = slug(x["name"])
    h = (x.get("ig") or "").rstrip("?")
    maps = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(x["q"] + " São Paulo")

    fatos = []
    if un:
        fatos.append(("Unidades", "<ul>" + "".join(f'<li><b>{e(u["nome"])}</b> · {e(u["end"])}</li>' for u in un) + "</ul>"))
    else:
        fatos.append(("Onde", f'{e(x["ref"])}<br><small>{e(x["b"])}</small>'))
    if x.get("hr"):
        fatos.append(("Quando", e(x["hr"])))
    if x.get("info"):
        fatos.append(("Mais", e(x["info"])))
    links = []
    if h:
        links.append(f'<a href="https://www.instagram.com/{e(h)}/" target="_blank" rel="noopener">@{e(h)}</a>')
    if x.get("site"):
        links.append(f'<a href="{e(x["site"])}" target="_blank" rel="noopener">Site</a>')
    if links:
        fatos.append(("Links", " · ".join(links)))
    fatos_html = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in fatos)

    post = x.get("post")
    foto = (f'<section><h2>No Instagram</h2><div class="ig"><blockquote class="instagram-media" data-instgrm-permalink="https://www.instagram.com/{e(post)}/" data-instgrm-version="14">'
            f'<a href="https://www.instagram.com/{e(post)}/" target="_blank" rel="noopener">Ver post de {e(x["name"])} no Instagram</a></blockquote></div></section>') if post else ""
    mapa = '<section><h2>No mapa</h2><div id="map" role="region" aria-label="Mapa"></div></section>' if pontos else ""
    titulo = f'{x["name"]} · Bora frequentar SP'
    desc_og = f'{x["d"]} {x["t"]} · {re.sub(r" \(.*\)$", "", x["b"])}.'

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc_og)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}{s}/">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(desc_og)}">
<meta property="og:image" content="{BASE}{s}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0D6B5B">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
{'<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">' if pontos else ''}
<style>{CSS}</style>
</head>
<body>
<!-- Página gerada por ferramentas/bora-frequentar/gerar.py. Não edite à mão: mude os dados em bora-frequentar/index.html e rode o gerador. -->
<div class="wrap">
<a class="voltar" href="../">← Todos os lugares</a>
<span class="eyebrow">Bora frequentar SP · #{x["n"]} da lista</span>
<h1>{e(x["name"])}</h1>
<div class="pills"><span class="pill t" style="--c:{cor}">{e(x["t"])}</span><span class="pill">{e(x["b"])}</span></div>
<p class="desc">{e(x["d"])}</p>
{f'<p class="note">{e(x["note"])}</p>' if x.get("note") else ""}
<div class="cta">
  <button class="btn wa" type="button" id="convidar">{ICONE_WA}Convidar alguém</button>
  <a class="btn" href="{e(maps)}" target="_blank" rel="noopener">Como chegar</a>
  {f'<a class="btn" href="https://www.instagram.com/{e(h)}/" target="_blank" rel="noopener">Instagram</a>' if h else ""}
</div>

<section><h2>Informações</h2><div class="fatos"><dl>{fatos_html}</dl></div></section>
{precos_html(dados["PRECO"].get(n))}
{mapa}
{foto}

<section class="porque">
  <h2>Por que este lugar está aqui</h2>
  <p>{e(x["name"])} está numa lista de bares e restaurantes de São Paulo que se posicionaram em defesa da democracia e agora estão sendo alvo de boicote nas redes. A resposta é casa cheia.</p>
  <a class="btn" href="../">Ver os 38 lugares da lista</a>
</section>
<footer>Informações conferidas em out/2026; horários e preços mudam, vale checar antes de ir.</footer>
</div>

<script src="../convite.js"></script>
{'<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>' if pontos else ''}
<script>
const X={json.dumps({k: x[k] for k in x}, ensure_ascii=False)};
const EXTRA={json.dumps({"unidades": un, "precos": dados["PRECO"].get(n)}, ensure_ascii=False)};
const PONTOS={json.dumps(pontos, ensure_ascii=False)};
document.getElementById("convidar").onclick=()=>Convite.abrir(X,EXTRA);
if(PONTOS.length&&window.L){{
  const map=L.map("map",{{scrollWheelZoom:false}});
  L.tileLayer("https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",{{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}}).addTo(map);
  const g=L.featureGroup().addTo(map);
  const icon=L.divIcon({{className:"",html:'<div class="pin" style="--c:{cor}"></div>',iconSize:[26,26],iconAnchor:[13,13],popupAnchor:[0,-12]}});
  PONTOS.forEach(p=>L.marker([p.lat,p.lng],{{icon}}).addTo(g).bindPopup(`<b>${{p.nome||X.name}}</b><br>${{p.end}}<br><a target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination=${{encodeURIComponent(X.name+" "+p.end+" São Paulo")}}">Como chegar</a>`));
  PONTOS.length>1?map.fitBounds(g.getBounds(),{{padding:[30,30]}}):map.setView([PONTOS[0].lat,PONTOS[0].lng],16);
}}
{'''(()=>{const s=document.createElement("script");s.async=true;s.src="https://www.instagram.com/embed.js";document.body.appendChild(s)})();''' if post else ''}
</script>
</body>
</html>
"""


def main():
    dados = ler_dados()
    vistos = set()
    for x in dados["D"]:
        s = slug(x["name"])
        assert s not in vistos, s
        vistos.add(s)
        pasta = GUIA / s
        pasta.mkdir(exist_ok=True)
        (pasta / "index.html").write_text(pagina(x, dados), encoding="utf-8")
        imagem(x, pasta / "og.png")
    print(f"{len(vistos)} páginas geradas em {GUIA}")


if __name__ == "__main__":
    main()
