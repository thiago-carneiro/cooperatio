# Role card: validator

Canon: [02-canon.json](02-canon.json)

**Decides:**

- nada; mede e emite notas com magnitude. Ferramenta que não roda é falha de ferramenta, nunca lista vazia.

**Does not decide:**

- conteúdo, limites, veredito, registro; não cria regra nova sem nota ao dono do instrumento.

**Inputs:**

- `layout.json`, `02-canon.json`, `03-artifacts.json`, `06-gates.md`, `state/forbidden.txt`, `priors.json`, `state/notes.jsonl`, `state/round-record.jsonl`, e o documento de método da instância anterior quando os números de prior são medidos.

**Outputs:**

- o relatório das checagens (`08-validator/report.md` quando o binário executa; nesta produção, a replicação mecânica das regras registrada em `review/wave-1-report.md` e `review/wave-2-report.md`).

**Exit gate:**

- relatório determinístico, sem data e com caminhos relativos; código de saída próprio quando a ferramenta falha.

**Notes it emits:**

- to the artefato onde o defeito nasce, com severidade e magnitude; to the `03-artifacts`, quando um alvo de nota não está no grafo.

**Code-conversion degree:**

- (a) convertido; executor: `08-validator/validator.py` (nesta produção, não executado no dispatch do writer: a célula foi verificada por replicação mecânica das regras do fonte, e o binário deve ser re-executado antes da rodada de revisão).
