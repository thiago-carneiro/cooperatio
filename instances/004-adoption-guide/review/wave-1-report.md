# Relatório da onda 1: guia de adoção do cooperatio

## Proveniência do instrumento

O binário do validador não executou nesta onda: o ambiente do dispatch não executa shell. As medidas abaixo vêm de replicação mecânica das regras do fonte do validador do corpus do método — as mesmas expressões regulares, a mesma lógica de unidades e a mesma hash de rúbrica, transcritas para execução em outra linguagem, após leitura integral do fonte. A re-execução do binário fica como pendência para o orquestrador, antes da rodada de revisão; da raiz do corpus do método:

```text
cp 02-reflexive-application/80-validator/validator.py 08-validator/
python 08-validator/validator.py --folder . --layout layout.json \
    --registry priors.json --forbidden state/forbidden.txt \
    --rubric-hash 07-rubric.sha256 --notes state/notes.jsonl \
    --case <documento de método da instância 000-av-production> --determinism
```

Até a re-execução, nenhum código de saída do binário é claimado; o que este relatório registra são medidas da replicação.

## O que a onda 1 fez

- Versão integral do guia (`guia-de-adocao.md`), escrita contra os seis itens do conteúdo mínimo do brief: 1052 palavras, na faixa de 900 a 1400.
- Rúbrica congelada antes da produção: sha256 da seção "Rubric" de `06-gates.md` gravado em `07-rubric.sha256` e conferido igual na medição do fechamento desta onda.
- Números de prior conferidos por leitura do documento de método da instância anterior: "18 papéis" (seção 1.1, "O método separa o trabalho em 18 papéis") e "49 artefatos" (seção 2.1, o grafo do piloto 1 "tem 49 artefatos"). No guia, os dois números aparecem na unidade que carrega a marca `[prior:000-av-production]`.
- A própria replicação achou um defeito neste relatório na primeira passada: um caminho com prefixo de marcador no bloco de comando, pego pelo detector de caminho absoluto do gate de anonimato — corrigido para caminho relativo antes do fechamento da onda.

## Medições

Réplica das checagens sobre os artefatos da célula; gate pendente é o que não pôde ser medido sem entrada que a replicação não tinha (o documento do prior), nem aprovação nem reprovação.

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
| `guia-de-adocao.md` | `p-anonymity` | 0 | 0 | pass |
| `guia-de-adocao.md` | `p-form` | 0 | 0 | pass |
| `guia-de-adocao.md` | `p-prior` | 1 marca, 0 não registradas; números não medidos (sem documento do prior) | 0 | pending |
| `guia-de-adocao.md` | `p-prior-mark` | 0 | 0 | pass |
| `guia-de-adocao.md` | `p-size` | 1052 | 900 a 1400 | pass |
| `guia-de-adocao.md` | `p-terms` | 0 | 0 | pass |
| `priors.json` | `p-prior-pin` | 1 prior executado citado; não medido (sem documento do prior) | equal | pending |
| `review/wave-1-report.md` | `p-anonymity` | 0 | 0 | pass |
| `review/wave-1-report.md` | `p-form` | 0 | 0 | pass |
| `review/wave-1-report.md` | `p-terms` | 0 | 0 | pass |
| `state/notes.jsonl` | `p-notes` | 3 notas, 0 inválidas | 0 inválidas | pass |
| `state/round-record.jsonl` | `p-contract-shape` | 1 linha, 0 violações | 0 | pass |
| `08-validator/sensitivity.md` | `p-sensitivity` | não medido | 0 missed | pending |

## Notas emitidas

Três notas da onda 1, registradas em `state/notes.jsonl`: duas `low` de redação no guia (a voz de leitor interno na seção de evidência; "notas no contrato" em vez de registro de notas) e uma `medium` de instrumento (a re-execução do binário pendente, alvo `wave-reports`). As duas primeiras são endereçadas na onda 2; a terceira permanece aberta até a re-execução.

## Pendências

- `p-prior` (números) e `p-prior-pin`: pendentes na replicação, que rodou sem o documento do prior; os dois números citados foram conferidos por leitura (seção "O que a onda 1 fez") e a re-execução do binário com `--case` fecha os dois gates.
- `p-sensitivity`: sensibilidade do instrumento ainda não medida nesta produção; o teste roda na onda 2, e o resultado vai em `08-validator/sensitivity.md`.
