# estevaouyra.github.io

Site pessoal, em HTML estático e sem build. Publicado pelo GitHub Pages em https://estevaouyra.github.io/.

## Estrutura

- `index.html`: página inicial, com a lista de páginas
- `bora-frequentar/`: guia "Bora frequentar SP"
  - `index.html`: a página. Os dados ficam no array `const D=[...]` do `<script>`.
  - `lugares-mymaps.csv`: os lugares com endereço, para importar no Google My Maps

Para criar uma página nova, faça uma pasta com um `index.html` dentro e adicione um link para ela na página inicial.
O arquivo `.nojekyll` desliga o Jekyll, então os arquivos são servidos exatamente como estão.
