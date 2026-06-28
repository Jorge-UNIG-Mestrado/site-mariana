# Handoff: Site de Receitas — Mariana Tavares

## Visão geral
Site de receitas single-page da Mariana Tavares (médica, mãe, cozinheira nas horas livres).
O público chega pelo Instagram (@mari_mtavaresg), majoritariamente no **celular**. O objetivo do
site é: a pessoa abre o link, acha a receita em segundos e **vê o vídeo + lê o passo a passo
sem precisar sair do site**.

Estilo visual inspirado no Panelinha (limpo, claro, editorial), sobre o design system do projeto:
fundo creme, acento turquesa, tipografia serifada (Newsreader) + sans (Instrument Sans).

## Sobre os arquivos deste pacote
Os arquivos aqui são uma **referência de design feita em HTML** — um protótipo funcional que mostra
o visual e o comportamento pretendidos. Você pode:

- **Opção A (rápida, recomendada pra começar):** publicar o `index.html` como está. Ele é um
  **arquivo único, autocontido e offline** (fontes, scripts e estilos já embutidos). Basta jogar
  num repositório e ligar o GitHub Pages. Funciona como site estático.
- **Opção B (produção/escala):** recriar o design no ambiente do seu codebase (React/Vite, Next,
  Astro, etc.) seguindo os padrões dele, usando este protótipo como espelho de pixel. Os dados das
  receitas devem sair do código e virar um `receitas.json` externo (ver "Automação" abaixo).

> O `index.html` é o arquivo **compilado** — não edite à mão. Para mudar o design, edite
> `Mariana Tavares - Receitas.dc.html` (fonte) e recompile.

## Fidelidade
**Alta fidelidade (hifi).** Cores, tipografia, espaçamentos e interações são finais. Ao recriar
num codebase, reproduza pixel a pixel com a biblioteca de UI existente.

## Como publicar no GitHub Pages (Opção A)
1. Crie um repositório no GitHub (ex.: `site-mariana`).
2. Copie o `index.html` deste pacote para a raiz do repositório.
3. Faça commit e push na branch `main`.
4. No GitHub: **Settings → Pages → Source: Deploy from a branch → main / (root) → Save**.
5. Em ~1 min o site fica no ar em `https://SEU_USUARIO.github.io/site-mariana/`.
6. (Opcional) Domínio próprio: aponte o DNS e configure em Settings → Pages → Custom domain.

## Vídeos do YouTube (importante)
Hoje cada receita está com o vídeo como **"Vídeo em breve no canal"** porque os IDs do YouTube
ainda são placeholders. Para o player tocar **embutido dentro do site**, preencha o campo
`youtubeId` de cada receita com o ID do vídeo (a parte depois de `watch?v=`).

Exemplo: para `https://youtube.com/watch?v=dQw4w9WgXcQ` → `youtubeId: "dQw4w9WgXcQ"`.

- Onde editar na fonte: arquivo `Mariana Tavares - Receitas.dc.html`, dentro do array `RECIPES`.
- Comportamento: se `youtubeId` está vazio → mostra o pôster "Vídeo em breve" que abre o canal.
  Se preenchido → mostra um pôster "Assistir o preparo aqui" e, ao tocar, carrega o player
  do YouTube embutido (lazy: só carrega no clique, pra não pesar no celular).

## Telas / Views (single-page)
Tudo numa página só, com rolagem. Ordem:

1. **Header (sticky)** — marca "Mariana Tavares" à esquerda; nav "Em Alta / Receitas" e ícones
   Instagram/YouTube à direita. Fundo creme translúcido com blur, hairline turquesa embaixo.
2. **Hero** — eyebrow "MÉDICA · MÃE DE DOIS · ESPOSA"; título serifado grande
   "Comida de verdade, *sem complicação.*" (palavra em itálico turquesa); frase de apoio;
   3 estatísticas (419k / 12 / 8) em serifa turquesa separadas por filetes verticais.
3. **Em Alta no Instagram** — divisor em caixa-alta + 2 cards virais (Quibe 200k / Caldo Verde 127k)
   com selo âmbar "🔥 Viral" e **contador de views animado** (conta de 0 até o número, easing cúbico, ~1,5s).
4. **Todas as Receitas** — divisor + barra de busca (filtro em tempo real por nome/descrição) +
   pills de categoria (turquesa quando ativa). Grid responsivo `auto-fill minmax(268px,1fr)`.
5. **Card de receita** — área de emoji com tint suave por categoria + borda superior de 3px na cor
   da categoria; chip de categoria em caixa-alta; tempo; título serifado; chip de benefício;
   descrição; botões "Ingredientes" (abre ficha) e "Vídeo" (turquesa).
6. **Ficha da receita (modal/folha)** — abre ao tocar no card. Header turquesa (emoji, nome, tempo,
   porções, views) → **player de vídeo 16:9** (pôster click-to-play) → chip de benefício →
   **Ingredientes** (lista com bullets) → **Modo de preparo** (passos numerados) → botão coral
   "Assistir no YouTube" (backup) → "Fechar". No celular ocupa quase a tela inteira, com rolagem interna.
7. **Footer** — frase inspiracional serifada, nome, papéis, botões Instagram/YouTube. Fundo turquesa escuro.

## Interações & comportamento
- **Busca:** filtra `recipes` por `name`/`desc` (case-insensitive) a cada tecla.
- **Filtro de categoria:** clique numa pill seta `cat`; "Todas" mostra tudo.
- **Contador "Em Alta":** anima no mount via `requestAnimationFrame` (easing `1 - (1-t)^3`).
- **Ficha:** clique no card seta `sel` e reseta `playing=false`; clique fora ou "Fechar" fecha.
- **Vídeo:** pôster → `playing=true` → injeta `<iframe>` do YouTube com `autoplay=1&rel=0`.
- **Hover (desktop):** cards sobem (`translateY(-5px)`) com sombra mais forte; pills/links mudam cor.
- **Mobile-first:** alvos de toque ≥ 44px; grid colapsa pra 1 coluna; ficha rolável.

## Estado (state)
- `cat` (string) — categoria ativa. Default `"todas"`.
- `q` (string) — termo de busca.
- `sel` (objeto receita | null) — receita aberta na ficha.
- `playing` (bool) — se o vídeo da ficha já foi acionado.
- `count` (0→1) — progresso da animação do contador de views.

## Design tokens (do design system)
Cores:
- `--bg` creme `#F6F4EE` · `--bg-alt` `#FBFAF6` · `--paper` `#FFFFFF`
- `--ink` `#0F2A33` · `--ink-soft` `#41606B` · `--ink-mute` `#7C9099`
- `--rule` `#D8DDD3`
- `--teal` `#1A7A8C` (primário) · `--teal-deep` `#0E5A6F` · `--teal-tint` `#E8F1F2`
- `--coral` `#D9633E` (botão YouTube) · `--amber` `#C8893B` (selo Viral)

Acentos por categoria (borda + label do card):
- fit `#5E8C72` · sopas `#1A7A8C` · cafe `#C8893B` · paes `#A4824B`
- petiscos `#7A8C5E` · sobremesas `#C25B45` · bebidas `#2E8C8C`

Tipografia:
- Títulos/nome: **Newsreader** (serif), pesos 300–500, itálico nos destaques.
- Corpo/nav: **Instrument Sans**, 400–700.
- Labels/eyebrows: caixa-alta, `letter-spacing` 0.14–0.22em.

Raios: cards 12px · ficha 16px · pills/botões 999px (pill). Sombra base: `0 1px 3px rgba(15,42,51,.05)`.

## Estrutura dos dados (cada receita)
```js
{
  id, name, category,        // category: fit|sopas|cafe|paes|petiscos|sobremesas|bebidas
  time, servings,            // "35 min", "6 porções"
  desc,                      // texto curto do card
  yt,                        // link do canal/vídeo (fallback)
  youtubeId,                 // ID do vídeo p/ player embutido ("" = sem vídeo ainda)
  ingredients: [ ... ],      // lista de strings
  steps: [ ... ],            // modo de preparo, lista de strings (passos)
  benefit, bEmoji,           // "Low carb", "🥗"
  views,                     // "200k views" ou null
  featured,                  // true = aparece em "Em Alta" + selo Viral
  emoji                      // emoji ilustrativo do prato
}
```

## Automação (n8n) — Opção B
Para a Mariana publicar receitas sozinha sem mexer no código:
1. Externalize o array `RECIPES` para um `receitas.json` na raiz do site (já há um esqueleto em
   `receitas.json` no pacote original).
2. No app, faça `fetch('receitas.json')` no carregamento em vez do array embutido.
3. n8n: um fluxo que recebe a receita nova (formulário / planilha / webhook), monta o objeto no
   formato acima, dá commit do `receitas.json` atualizado no repositório (GitHub node) → o GitHub
   Pages republica sozinho. Sem rebuild, sem deploy manual.

## Arquivos deste pacote
- `index.html` — site compilado, autocontido, pronto pra GitHub Pages.
- `Mariana Tavares - Receitas.dc.html` — fonte editável do design (markup + lógica).
- `README.md` — este documento.
