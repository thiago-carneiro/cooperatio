# Gates: guia de adoção do cooperatio

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `p-size` | `guia-de-adocao`, `method-doc` | palavras do arquivo, por divisão em espaços | 900 a 1400 / 1800 a 2600 | [brief] faixa de tamanho declarada pelo dono na especificação da produção; [hypothesis] faixa do documento de método declarada no fechamento: relata a produção inteira sem duplicar o guia |
| `p-form` | `guia-de-adocao`, `wave-reports`, `round-report`, `method-doc` | marcas de forma: tags HTML e cercas sem a marca text | 0 | [method] markdown plano com cercas marcadas text, como o corpus manda |
| `p-terms` | `guia-de-adocao`, `brief`, `sources-of-truth`, `role-cards`, `gates-doc`, `rubric`, `wave-reports`, `method-doc` | termos a evitar fora de código e de alvo de link | 0 | [method] um termo por conceito; o canon é a fonte única de vocabulário |
| `p-anonymity` | `guia-de-adocao`, `brief`, `sources-of-truth`, `gates-doc`, `wave-reports`, `method-doc` | caminhos absolutos, datas, identificadores da lista proibida | 0 | [brief] o deliverable é externo; nenhum identificador local entra |
| `p-canon-link` | `brief`, `sources-of-truth`, `role-cards` | links para o arquivo do canon | ≥ 1 | [method] todo documento vivo aponta para o canon que o rege |
| `p-card` | `role-cards` | campos de cartão ausentes, dos sete fixos | 0 | [method] sete campos fixos por papel, como o recipe genérico prescreve |
| `p-limit` | `gates-doc` | linhas de gate sem magnitude, limite ou justificativa rotulada | 0 | [method] todo limite tem rótulo de origem e seis palavras no mínimo |
| `p-references` | `03-artifacts`, `gates-doc` | donos, dependências ou alvos não declarados; ciclos no grafo | 0 | [method] o grafo é acíclico e cada nome citado tem dono declarado |
| `p-prior` | `guia-de-adocao`, `method-doc` | marcas de prior não registradas; números de prior não verificados | 0 | [method] afirmação sobre a instância anterior leva marca e número conferido |
| `p-prior-mark` | `guia-de-adocao`, `method-doc` | unidades com frase de gatilho sem a marca de prior | 0 | [method] a marca é o que torna a afirmação sobre prior verificável |
| `p-contract-shape` | `02-canon`, `round-record` | violações de esquema; palavras-chave fora do subconjunto suportado | 0 | [method] o contrato recusa ambiguidade antes do trabalho caro começar |
| `p-prior-pin` | `priors` | instância executada citada pinada em sha256 diferente do registro | equal | [method] o registro pina o documento que a citação de prior realmente usa |
| `p-notes` | `notes-ledger` | notas fora do contrato de seis campos ou com alvo fora do grafo | 0 | [method] a nota é o único pedido de mudança entre papéis, com contrato |

### Size ranges

| Document | Minimum | Maximum |
| --- | --- |
| guia-de-adocao.md | 900 | 1400 |
| metodo-de-producao.md | 1800 | 2600 |

## Rubric

Congelada antes da primeira produção; o sha256 da seção está em `07-rubric.sha256`.

### Dimensions

| Dimension | What is measured | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| D1 cobertura do mínimo | os seis itens do brief estão presentes e completos | faltam dois ou mais itens, ou um ausente por inteiro | os seis aparecem, mas um fica raso ou incompleto | os seis presentes, completos e com peso proporcional |
| D2 honestidade da evidência | toda afirmação de fato é conferível no corpus ou marcada como hipótese | claim inventada ou sem fonte no corpus | fontes existem, mas imprecisas ou mal citadas | toda claim conferida, e os limites declarados como limites |
| D3 clareza para o adotante | um leitor sem contato prévio entende e sabe o próximo passo | jargão sem definição; o leitor se perde | o todo se entende, com tropeço em termo ou passo | cada termo definido na primeira uso; o próximo passo é claro |
| D4 forma | markdown plano, tabelas e cercas corretas, tamanho na faixa | fora da faixa declarada ou forma quebrada | na faixa, com falhas locais de forma | na faixa, com forma limpa ponta a ponta |
| D5 anonimato e tom | sem identificador local e sem tom de venda | identificador local no deliverable ou pitch de venda | neutro, com escorregão pontual de tom | neutro e anônimo ponta a ponta |
| D6 terminologia do método | vocabulário usado no sentido que o corpus define | termo canônico usado com outro sentido | um ou dois deslizes pontuais de terminologia | vocabulário do corpus usado de acordo com o canon dele |

### Finding severity

| Severity | When |
| --- | --- |
| blocking | defeito que invalida o alvo: claim falsa sobre o corpus, identificador local no deliverable, item do conteúdo mínimo ausente |
| high | lacuna que impede o adotante de agir: passo da produção errado, termo do método com sentido trocado |
| medium | imprecisão sem rótulo de hipótese; citação vaga; seção desequilibrada |
| low | estilo, legibilidade local, ordem de parágrafos |

### Verdict rule

```text
if any blocking finding or any dimension scores <= 2:
    verdict = rejected
else if no high finding and every dimension >= 4:
    verdict = accepted
else:
    verdict = accepted with conditions
```

### Report format

O relatório da rodada traz: veredito; notas por dimensão; findings por severidade; verificado e correto; não verificado; fora de escopo; da segunda rodada em diante, a tabela item a item da rodada anterior (resolvido, parcial, ficou, piorou); notas no contrato.
