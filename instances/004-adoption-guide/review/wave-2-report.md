# Relatório da onda 2: guia de adoção do cooperatio

## Proveniência do instrumento

Mesma proveniência da onda 1: o binário do validador não executou (ambiente do dispatch sem shell); as medidas vêm de replicação mecânica das regras do fonte, com sha256 próprio validado contra vetor conhecido e a hash da rúbrica recalculada batendo byte a byte com a congelada. Nenhum código de saída do binário é claimado; a re-execução — comando no relatório da onda 1 — permanece pendência do orquestrador antes da rodada de revisão.

## O que a onda 2 fez

- Endereçou as duas notas de redação da onda 1 no guia (a terceira nota, de instrumento, é endereçada ao orquestrador, não ao guia).
- Re-mediu o guia revisado: 1054 palavras, na faixa de 900 a 1400; todos os gates do guia verdes.
- Rodou o teste de sensibilidade do instrumento: dez defeitos conhecidos injetados em cópia em memória do guia, dez pegos — registro em `08-validator/sensitivity.md`.
- Registrou a linha da onda 2 no round-record, com a hash da rúbrica congelada.

## Notas da onda 1, item a item

| Nota | Severidade | Estado | Evidência |
| --- | --- | --- | --- |
| voz de leitor interno na seção de evidência ("as regras que agora lhe entrego") | low | resolvido | guia revisado: "o prior de onde o cooperatio extraiu as regras que este guia apresenta" |
| "notas no contrato" em vez de registro de notas | low | resolvido | guia revisado: "os achados viram notas no registro de notas" |
| re-execução do binário do validador | medium | parcial | comando pronto no relatório da onda 1; a execução segue pendente, tarefa do orquestrador antes da rodada de revisão |

A nota parcial não fecha em onda de produção: a execução do binário é ação fora do alcance do writer, e a pendência está declarada onde a decisão acontece. Nenhuma nota nova foi emitida na onda 2 — o self-review não achou defeito que os gates e a leitura não tivessem pegado.

## Medições

Réplica das checagens sobre os artefatos da célula no fechamento da onda 2.

| Documento | Gate | Magnitude | Limite | Resultado |
| --- | --- | --- | --- | --- |
| `00-brief.md` | `p-anonymity` | 0 | 0 | pass |
| `00-brief.md` | `p-canon-link` | 1 | ≥ 1 | pass |
| `00-brief.md` | `p-terms` | 0 | 0 | pass |
| `01-sources-of-truth.md` | `p-anonymity` | 0 | 0 | pass |
| `01-sources-of-truth.md` | `p-canon-link` | 1 | ≥ 1 | pass |
| `01-sources-of-truth.md` | `p-terms` | 0 | 0 | pass |
| `02-canon.json` | `p-contract-shape` | 0 violações | 0 | pass |
| `03-artifacts.json` | `p-references` | 0 | 0 | pass |
| `04-roles/reviewer.md` | `p-card` | 0 campos ausentes | 0 | pass |
| `04-roles/reviewer.md` | `p-canon-link` | 1 | ≥ 1 | pass |
| `04-roles/reviewer.md` | `p-terms` | 0 | 0 | pass |
| `04-roles/validator.md` | `p-card` | 0 campos ausentes | 0 | pass |
| `04-roles/validator.md` | `p-canon-link` | 1 | ≥ 1 | pass |
| `04-roles/validator.md` | `p-terms` | 0 | 0 | pass |
| `04-roles/verifier.md` | `p-card` | 0 campos ausentes | 0 | pass |
| `04-roles/verifier.md` | `p-canon-link` | 1 | ≥ 1 | pass |
| `04-roles/verifier.md` | `p-terms` | 0 | 0 | pass |
| `04-roles/writer.md` | `p-card` | 0 campos ausentes | 0 | pass |
| `04-roles/writer.md` | `p-canon-link` | 1 | ≥ 1 | pass |
| `04-roles/writer.md` | `p-terms` | 0 | 0 | pass |
| `06-gates.md` | `p-anonymity` | 0 | 0 | pass |
| `06-gates.md` | `p-frozen-rubric` | equal | equal | pass |
| `06-gates.md` | `p-limit` | 0 | 0 | pass |
| `06-gates.md` | `p-references` | 0 | 0 | pass |
| `06-gates.md` | `p-terms` | 0 | 0 | pass |
| `07-rubric.md` | `p-terms` | 0 | 0 | pass |
| `08-validator/sensitivity.md` | `p-sensitivity` | 0 de 10 perdidos | 0 missed | pass |
| `guia-de-adocao.md` | `p-anonymity` | 0 | 0 | pass |
| `guia-de-adocao.md` | `p-form` | 0 | 0 | pass |
| `guia-de-adocao.md` | `p-prior` | 1 marca, 0 não registradas; números não medidos (sem documento do prior) | 0 | pending |
| `guia-de-adocao.md` | `p-prior-mark` | 0 | 0 | pass |
| `guia-de-adocao.md` | `p-size` | 1054 | 900 a 1400 | pass |
| `guia-de-adocao.md` | `p-terms` | 0 | 0 | pass |
| `priors.json` | `p-prior-pin` | 1 prior executado citado; não medido (sem documento do prior) | equal | pending |
| `review/wave-1-report.md` | `p-anonymity` | 0 | 0 | pass |
| `review/wave-1-report.md` | `p-form` | 0 | 0 | pass |
| `review/wave-1-report.md` | `p-terms` | 0 | 0 | pass |
| `review/wave-2-report.md` | `p-anonymity` | 0 | 0 | pass |
| `review/wave-2-report.md` | `p-form` | 0 | 0 | pass |
| `review/wave-2-report.md` | `p-terms` | 0 | 0 | pass |
| `state/notes.jsonl` | `p-notes` | 3 notas, 0 inválidas | 0 inválidas | pass |
| `state/round-record.jsonl` | `p-contract-shape` | 2 linhas, 0 violações | 0 | pass |

## Pendências

- Re-execução do binário do validador (comando no relatório da onda 1), com o documento do prior em `--case`: fecha `p-prior` (números) e `p-prior-pin` — os dois únicos pendentes — e roda o autoteste e o modo determinismo.
- As fases seguintes, fora das ondas: rodada de revisão (executor distinto, rúbrica congelada), documento de método da instância e registro dela no corpus do método.
