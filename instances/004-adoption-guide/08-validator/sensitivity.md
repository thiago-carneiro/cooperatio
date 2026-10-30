# Sensitivity: instrumento de checagem desta célula

Proveniência: o teste rodou sobre a replicação mecânica das regras do fonte do validador (a mesma transcrição usada nos relatórios de onda), injetando cada defeito numa cópia em memória do `guia-de-adocao.md`. A re-execução do binário com este mesmo protocolo acompanha a pendência registrada no relatório da onda 1.

Cada defeito conhecido é injetado numa cópia do guia e o gate correspondente é re-executado; o teste quer que todos sejam pegos — um defeito injetado que passa é um gate que não morde.

| # | Defeito injetado | Gate | Pego |
| --- | --- | --- | --- |
| 1 | termo a evitar na prosa | `p-terms` | sim |
| 2 | caminho absoluto na prosa | `p-anonymity` | sim |
| 3 | data em formato ISO | `p-anonymity` | sim |
| 4 | data em formato dia/mês/ano | `p-anonymity` | sim |
| 5 | cerca de código sem a marca text | `p-form` | sim |
| 6 | tag HTML na prosa | `p-form` | sim |
| 7 | frase de gatilho de prior sem a marca | `p-prior-mark` | sim |
| 8 | tamanho abaixo da faixa declarada | `p-size` | sim |
| 9 | identificador proibido da lista externa | `p-anonymity` | sim |
| 10 | marca de prior não registrada | `p-prior` | sim |

Caught 10 of 10. Not measured: 0.

Cada pega produziu ao menos uma nota do gate correspondente na passada registrada (o termo contado, o caminho citado, a linha da cerca, a unidade da frase de gatilho). O que este protocolo não exercita: o pin sha256 do prior (pede o documento do prior, pendente para a re-execução do binário) e o modo determinismo, que compara o relatório do binário entre duas execuções — ambos ficam para a re-execução.
