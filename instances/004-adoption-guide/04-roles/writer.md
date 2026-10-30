# Role card: writer

Canon: [02-canon.json](02-canon.json)

**Decides:**

- a redação, a ordem e o nível de detalhe do guia, dentro do conteúdo mínimo do brief e do vocabulário do canon.

**Does not decide:**

- fatos (vêm do corpus, por meio das fontes de verdade); termos do método (vêm do canon); limites e gates (vêm de `06-gates.md`); o veredito (é do reviewer); o registro da instância (é do dono, fase posterior).

**Inputs:**

- `00-brief.md`, `01-sources-of-truth.md`, `02-canon.json`, `06-gates.md` e o corpus do cooperatio, por caminho relativo.

**Outputs:**

- `guia-de-adocao.md`.

**Exit gate:**

- p-size, p-form, p-terms, p-anonymity, p-prior e p-prior-mark verdes no guia.

**Notes it emits:**

- to the `02-canon`, quando falta termo ou número canônico para o que o guia precisa dizer; to the `sources-of-truth`, quando o corpus não sustenta uma claim pedida pelo brief.

**Code-conversion degree:**

- (c) contrato e gate apenas; executor: modelo de linguagem da família A em esforço alto; nenhum código além dos gates.
