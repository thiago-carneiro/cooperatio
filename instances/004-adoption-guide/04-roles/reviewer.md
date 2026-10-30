# Role card: reviewer

Canon: [02-canon.json](02-canon.json)

**Decides:**

- o veredito da rodada de revisão (rejected, accepted with conditions, accepted), pela regra mecânica da rúbrica congelada; a severidade de cada finding.

**Does not decide:**

- o conteúdo do guia (não o reescreve); os gates e limites; o canon; o registro da instância.

**Inputs:**

- `guia-de-adocao.md`, a seção Rubric de `06-gates.md` com `07-rubric.sha256`, e o corpus do cooperatio para conferir claims factuais; sem acesso ao raciocínio do produtor.

**Outputs:**

- `review/round-report.md`, no formato que a rúbrica prescreve.

**Exit gate:**

- o relatório segue o formato da rúbrica; o veredito sai da regra mecânica, não do juízo solto.

**Notes it emits:**

- to the `guia-de-adocao`, defeitos de conteúdo e de forma; to the `gates-doc`, quando um defeito que escapou pede gate novo.

**Code-conversion degree:**

- (c) contrato e gate apenas; executor: o modelo do produtor por outra rota, em esforço máximo (família A), em despacho separado — o cartão original dizia "de outra família"; o alias usado mapeava para a mesma família, corrigido no fechamento da v0.4.1 do método.
