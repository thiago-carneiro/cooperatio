# Validator rules

O que o validador da célula mede, gate a gate. Todos os gates leem o canon como dado: a lista não mora no código.

- `p-terms`: termos a evitar, palavra inteira, sem caixa, plural tolerado, fora de código e de alvo de link.
- `p-form`: tag HTML no texto; cerca de código sem a marca text; cerca aberta.
- `p-size`: palavras do documento contra a faixa declarada em "Size ranges".
- `p-anonymity`: caminho absoluto, data ISO, data dia/mês, data de feitura, identificador da lista proibida.
- `p-canon-link`: pelo menos um link para o arquivo do canon.
- `p-card`: os sete campos fixos em cada cartão de papel.
- `p-limit`: magnitude, limite e justificativa em cada linha de gate; justificativa começa com rótulo de origem e tem seis palavras no mínimo.
- `p-references`: dono, dependência e alvo de nota declarados no grafo; grafo acíclico.
- `p-prior`: marca de prior registrada no registro; número sob a marca conferido no documento de método da instância anterior.
- `p-prior-mark`: unidade com frase de gatilho leva a marca de prior.
- `p-contract-shape`: dado contra o esquema do contrato; censo de palavras-chave fora do subconjunto suportado.
- `p-prior-pin`: sha256 da instância executada citada, contra o valor pinado no registro.
- `p-notes`: nota com seis campos, severidade válida, alvo no grafo.

Código de saída: 0 sem nota alta ou bloqueante; 1 com pelo menos uma; 2 entrada inválida ou falha de ferramenta. O relatório é determinístico: sem data, caminhos relativos, saída ordenada.
