# Método de produção do guia de adoção do cooperatio

Como esta célula de produção levou o guia de adoção do cooperatio do brief ao registro: o alvo e por quê, a anatomia da célula, os papéis e os modelos que os exerceram, o caminho da produção com os resultados reais dos gates, as notas do ledger e as que ficaram abertas, os desvios do recipe e o ato de registro. O público é quem quer auditar esta produção ou reproduzi-la noutro alvo; o documento diz o porquê e a ordem, e aponta para onde está o detalhe. Esta produção terminou com veredito accepted na rodada de revisão, e este documento é o último artefato dela: ao fechar, a instância se registra.

**Como ler.**

- Todo caminho é relativo à raiz desta célula; os arquivos do corpus do método são citados pelo nome relativo à raiz dele.
- Toda afirmação sobre o prior leva a marca `[prior:000-av-production]`; o documento de método dele é citado relativo à raiz do repositório dele e mora fora daqui.
- "Run real" é o binário do validador executado pelo orquestrador, com código de saída e relatório próprios; "replicação" é a conferência mecânica das regras do fonte do validador que as ondas usaram, rotulada como tal, sem claim de código de saída. A distinção importa: na fase de ondas só houve replicação; o run real veio depois, antes da revisão.
- As notas abertas no fechamento são duas, uma de instrumento e uma de terminologia; estão em `open-notes.json` e na seção 6.
- As seções são numeradas para que produções futuras possam citá-las (a citação de número de prior aponta para seção do documento de método dela, como este documento aponta para as seções do prior).

## Onde está o detalhe

| Documento | O que tem |
| --- | --- |
| `00-brief.md` | o alvo, o conteúdo mínimo, as decisões de dono, a faixa de tamanho |
| `01-sources-of-truth.md` | as fontes por tipo de conteúdo |
| `02-canon.json` | números canônicos, variantes aceitas, termos a evitar, gatilhos de prior |
| `03-artifacts.json` | o grafo de artefatos com donos, caminhos e gates |
| `04-roles/*.md` | os cartões de papel dos quatro papéis |
| `06-gates.md` e `07-rubric.md` | os gates e a rúbrica congelada |
| `review/wave-1-report.md` e `review/wave-2-report.md` | os relatórios das ondas, com as medições |
| `review/round-1-notes.md` | o registro verbatim da rodada de revisão |
| `08-validator/report.md` | o relatório do run real do validador |
| `08-validator/sensitivity.md` | o teste de sensibilidade do instrumento |
| `state/notes.jsonl` e `state/round-record.jsonl` | o ledger de notas e o registro de rodadas |
| `lessons.md` | as lições, uma entrada por onda |
| `09-engine/README.md` | a decisão de não haver motor separado nesta escala |

## 1. O alvo e por quê

O alvo é um guia de adoção do cooperatio para quem nunca viu o método: o que ele é, para quem serve e para quem não, a anatomia de uma célula, o caminho de uma produção e o que a evidência sustenta — em português do Brasil, entre 900 e 1400 palavras, sem identificador local e sem tom de venda. O dono declarou seis itens de conteúdo mínimo no brief, e a rúbrica de revisão cobra os seis.

O porquê é a lacuna que o próprio corpus declara: o material se apresentava como hipótese de trabalho sustentada por uma execução — o prior de onde o cooperatio extraiu as regras, uma produção audiovisual em português do Brasil com 18 papéis e 49 artefatos no grafo [prior:000-av-production] — e por três instâncias desenhadas, não executadas. Um guia que fala ao adotante externo era a peça faltante entre o corpus e quem quer usá-lo; esta instância a produziu aplicando o método ao próprio material de divulgação, e é a primeira execução real da versão corrente do método.

## 2. Anatomia da célula

A célula segue o layout do recipe: documentos fundadores (brief, fontes de verdade, canon, grafo de artefatos, cartões de papel, gates), rúbrica com hash congelado, registro de priors pinados por sha256, ledger de notas no contrato de seis campos, registro de rodadas com esquema, validador copiado do corpus, e os relatórios de onda e de revisão em `review/`. Os artefatos declarados no grafo somam catorze, do guia aos relatórios de onda; o dono é humano nos documentos fundadores, agente no resto.

O deliverable mora na raiz (`guia-de-adocao.md`); o estado, em `state/` e `open-notes.json`; o instrumento, em `08-validator/`. O canon é JSON — os números canônicos, as variantes aceitas (entre elas "onda", o nome desta instância para uma passagem de produção), os termos a evitar e os gatilhos de afirmação de prior. O grafo é acíclico; cada artefato tem dono único e gates declarados no `06-gates.md`.

## 3. Papéis e modelos

Quatro papéis com cartão: writer, verifier, validator e reviewer; o dono decide o que o recipe deixa a ele e não tem cartão de execução. Os papéis de produção e conferência foram exercidos por um modelo de linguagem da família A, em esforço alto; o reviewer, pelo modelo da mesma família, por outra rota e em esforço máximo, em despacho separado, sem acesso ao raciocínio do produtor — somente aos artefatos, ao corpus e ao documento do prior. O round-record registra os executores por família (letra) e esforço; o mapa de letra para identificador fica com o dono, fora do material: o deliverable e este documento são anônimos por gate. A separação de família que o método pede não ocorreu nesta produção — o alias do reviewer mapeava para o mesmo modelo do produtor, por outra rota — e isso foi descoberto e corrigido no fechamento da v0.4.1 do método; o que houve foi separação de sessão e de raciocínio: o reviewer veio sem o raciocínio do produtor.

## 4. O caminho da produção

### 4.1 Montagem

A célula foi montada escrevendo os arquivos diretamente pelo contrato do scaffold do skill `cooperatio-teamwork` — o ambiente do dispatch não executa shell, e o scaffold não rodou; a forma que ele produz é que foi replicada, inclusive o `layout.json` que aponta cada artefato ao seu arquivo. A cópia do validador que o scaffold faria foi feita à mão pelo orquestrador, depois, antes do run real.

### 4.2 Rúbrica congelada antes da produção

Antes da primeira palavra do guia, a seção "Rubric" de `06-gates.md` foi congelada: o sha256 dela está gravado em `07-rubric.sha256` e vale
`ba88324b5536e027c4d2b671c4bbc4433c8d195e2c79f7ba2f1b89bf2661f67f`.
O congelamento antes da produção é o que impede a rúbrica de ser moldada ao resultado; o run real o confirmou (`p-frozen-rubric`, equal), e as três linhas do round-record carregam a mesma hash.

### 4.3 Onda 1

A onda 1 escreveu o guia inteiro, 1052 palavras — a onda existe para ser medida, não para ser boa. As medidas vieram da replicação mecânica das regras do fonte do validador do corpus, após leitura integral dele: as mesmas expressões regulares, a mesma lógica de unidades, o mesmo sha256 de rúbrica, transcritas para execução em outra linguagem. Nenhum código de saída do binário foi claimado nesta fase; a honestidade estava em rotular a proveniência em cada relatório. A própria replicação mordeu: achou um caminho absoluto no primeiro relatório de onda, no detector de anonimato — corrigido antes do fechamento da onda. Três notas foram ao ledger, duas de redação e uma de instrumento.

### 4.4 Onda 2

A onda 2 endereçou na origem as duas notas de redação: a voz de leitor interno virou formulação voltada ao próprio guia, e "notas no contrato" virou "notas no registro de notas". O guia re-medido fechou com 1054 palavras, na faixa de 900 a 1400. O teste de sensibilidade do instrumento injetou dez defeitos conhecidos em cópia em memória do guia e a replicação pegou os dez — registro em `08-validator/sensitivity.md`. A nota de instrumento (re-execução do binário) não era endereçável pelo writer: ficou declarada onde a decisão acontece, e o orquestrador a fechou com o run real antes da revisão.

### 4.5 Rodada de revisão

Um executor em despacho separado, sem o raciocínio do produtor — o mesmo modelo por outra rota, como registra a correção da seção 3, e não um de outra família — aplicou a rúbrica congelada ao guia. Veredito: accepted, pela regra mecânica — nenhum finding blocking, nenhum high, toda dimensão com nota 4 ou mais. As notas por dimensão: D1 5, D2 5, D3 4, D4 5, D5 5, D6 4. Dois findings: um medium (o gate global de sensibilidade pendente no instrumento real, detalhado na seção 5) e um low (o termo "contratos" usado como guarda-chuva no guia). O registro verbatim da rodada está em `review/round-1-notes.md`; o reviewer verificou por leitura direta e greps próprios, e tratou o run real do validador como evidência de instrumento.

### 4.6 Fechamento

O fechamento é este documento, mais o que ele registra: as duas notas da revisão no ledger (cinco no total), a linha da rodada de revisão no round-record com o veredito e a hash da rúbrica, as duas notas abertas em `open-notes.json`, e o registro da instância no corpus do método (seção 8). O guia não é editado depois da aceitação — disciplina de uma rodada; a nota low fica aberta por isso.

## 5. O que os gates mediram

O run real do binário, executado pelo orquestrador da raiz da célula, terminou com código de saída 0 e o modo determinismo pass (sha256 do relatório igual em duas execuções). Os resultados por gate, no relatório em `08-validator/report.md`:

| Gate | Resultado do run real |
| --- | --- |
| `p-size` do guia | 1054 palavras, na faixa de 900 a 1400 — pass |
| `p-prior` do guia | 1 marca registrada, 0 números não verificados — pass |
| `p-prior-pin` | prior executado citado, pin igual ao registrado — pass |
| `p-anonymity` do guia | 0 ocorrências — pass |
| `p-frozen-rubric` | equal — pass |
| gates de forma, termos e contrato | todos os declarados — pass |
| `p-sensitivity` | pendente no instrumento real — ver abaixo |

O estado final, dito com precisão: os gates declarados na célula passaram; um gate global do instrumento ficou pendente. A causa: o validador procura o registro de sensibilidade num caminho fixo, derivado da pasta do próprio binário, que ignora o `--layout` da célula — a constante `SENSITIVITY_FILE` aponta para `80-validator/sensitivity.md`, e o arquivo da célula está em `08-validator/sensitivity.md`. No corpus o caminho é o correto; o defeito só se manifesta em células que usam outra pasta para o instrumento. É um defeito do corpus, não da célula, e seguiu upstream como nota aberta ao dono dele; o registro de sensibilidade da célula é da replicação, rotulado como tal em três lugares.

O que as ondas mediram antes do run real foi replicação, e está rotulado como tal nos relatórios de onda. O run real fechou o que a replicação tinha como pendente (`p-prior` dos números, `p-prior-pin`, o autoteste e o determinismo) e revelou o terceiro pendente que nenhum relatório tinha previsto — a causa está registrada no finding medium da revisão, em `review/round-1-notes.md`.

## 6. Notas do ledger e notas abertas

Cinco notas no ledger, todas no contrato de seis campos: duas low de redação da onda 1, endereçadas na onda 2; uma medium de instrumento da onda 1 (re-execução do binário), endereçada pelo orquestrador com o run real; uma low de terminologia da revisão ("contratos" no guia), aberta — o guia não se edita pós-aceitação; e uma medium de instrumento da revisão (a sensibilidade pendente), aberta com encaminhamento upstream ao dono do corpus. As duas abertas moram em `open-notes.json` com causa e caminho; nada foi fechado sem registro.

## 7. Desvios do recipe

- O scaffold não executou (dispatch sem shell): a célula foi escrita diretamente pelo contrato dele, e a cópia do validador foi manual, pelo orquestrador, no lugar do passo automático.
- As medições das ondas vieram de replicação mecânica, não do binário — rotulado em cada relatório; o run real veio antes da revisão.
- O registro verbatim da revisão está em `review/round-1-notes.md`; o artefato `round-report` do grafo tinha caminho proposto diferente e ficou proposto — o registro real tem nome de rodada.
- `open-notes.json` permaneceu vazio durante as ondas: não é artefato declarado no grafo, e a nota em aberto vivia no ledger e nos relatórios; o fechamento o preenche com as duas notas abertas.

## 8. O registro desta instância

Ao fechar, esta produção se registra no corpus do método como a instância 004: status executada, documento de método este arquivo, sha256 do documento e localizador no registro de instâncias do corpus — a hash não mora aqui, e sim no registro que a torna conferível; o documento não se pina a si mesmo. Com o registro, a prosa viva do corpus passa a contar duas execuções em vez de uma, e a hipótese de trabalho dele se apoia num degrau a mais: a primeira execução real da versão 0.2 do método, que exercitou o recipe de ponta a ponta — scaffold replicado, rúbrica congelada antes de produzir, ondas medidas, revisão em despacho separado e sem o raciocínio do produtor, com veredito mecânico (pelo mesmo modelo por outra rota, não por outra família, como registra a correção da seção 3) — e devolveu ao corpus um defeito de instrumento que só uma célula de verdade revelava.
