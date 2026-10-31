# estevaouyra.github.io

Site pessoal, em HTML estático e sem build. Publicado pelo GitHub Pages em https://estevaouyra.github.io/.

## Estrutura

- `index.html`: página inicial, com a lista de páginas
- `bora-frequentar/`: guia "Bora frequentar SP"
  - `index.html`: a página. Os dados ficam no `<script>`: `D` (lugares), `UN` (unidades de quem tem mais de um endereço), `PRECO` (preços de referência) e `GEO` (coordenadas).
  - `convite.js`: a janela "Convidar alguém", que monta a mensagem do WhatsApp
  - `<lugar>/`: uma página por lugar (ex.: `balaio-ims/`), com `og.png` para a prévia do link. São geradas: não edite à mão.
  - `lugares-mymaps.csv`: os lugares com endereço, para importar no Google My Maps
- `ferramentas/bora-frequentar/gerar.py`: gera as páginas dos lugares a partir dos dados do `index.html`. Depois de mudar algum dado, rode `python3 ferramentas/bora-frequentar/gerar.py` (precisa de `node` e `Pillow`).

Para criar uma página nova, faça uma pasta com um `index.html` dentro e adicione um link para ela na página inicial.
O arquivo `.nojekyll` desliga o Jekyll, então os arquivos são servidos exatamente como estão.
