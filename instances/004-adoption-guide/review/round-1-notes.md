# Registro da rodada de revisão 1: guia de adoção do cooperatio

## Proveniência do instrumento

Executor distinto do produtor e de outra família, conforme declara o cartão de papel, em despacho separado, sem acesso ao raciocínio do produtor — somente aos artefatos da célula, ao corpus do método e ao documento de método da instância anterior. Nenhum código de saída de binário é claimado por esta rodada. O que esta rodada executou de própria mão: leitura direta do corpus (`README.md`, `01-principle.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`, `instances/registry.json`, `skills/cooperatio-teamwork/SKILL.md`, `02-reflexive-application/01-canon.md`, `02-reflexive-application/10-generic-recipe.md`) e do documento do prior; greps próprios no deliverable (identificadores proibidos, termos a evitar, tag HTML, caminho absoluto); contagem de palavras com a mesma semântica do validador (divisão em espaços); sha256 da seção "Rubric" de `06-gates.md` recalculado com implementação própria, autotestada contra três vetores conhecidos. O run real do validador (relatório em `08-validator/report.md`, executado pelo orquestrador, código de saída 0, modo determinismo pass) entra nesta rodada como evidência de instrumento — não re-executado aqui.

## Veredito

accepted — pela regra mecânica da rúbrica congelada: nenhum finding blocking, nenhuma dimensão com nota ≤ 2 (menor nota: 4), nenhum finding high, toda dimensão ≥ 4.

## Notas por dimensão

| Dimensão | Nota | Fundamento |
| --- | --- | --- |
| D1 cobertura do mínimo | 5 | os seis itens do brief presentes, completos e com peso proporcional |
| D2 honestidade da evidência | 5 | toda claim factual conferida no corpus por leitura direta; números do prior verificados no documento dele; claim auto-inclusiva honesta; limites declarados como limites |
| D3 clareza para o adotante | 4 | o todo se entende e o próximo passo é claro; tropeço pontual: "contrato" entra sem definição e muda de sentido no texto |
| D4 forma | 5 | 1054 palavras (contagem própria), na faixa de 900 a 1400; markdown plano, cercas marcadas text, sem tag HTML |
| D5 anonimato e tom | 5 | zero identificador da lista proibida (grep próprio), sem caminho absoluto nem data; neutro, sem tom de venda |
| D6 terminologia do método | 4 | um deslize pontual ("contratos" como guarda-chuva para os documentos fundadores); o restante do vocabulário conforme o canon |

## Findings por severidade

0 blocking, 0 high, 1 medium, 1 low.

**medium** (alvo: wave-reports): o run real do validador deixou `p-sensitivity` pendente — o binário procura `80-validator/sensitivity.md`, caminho da constante `SENSITIVITY_FILE` (derivada de `VALIDATOR_DIR` hardcoded), que não passa pelo `--layout`; o arquivo da célula está em `08-validator/sensitivity.md`. O relatório da onda 2 previu "os dois únicos pendentes" (`p-prior`, `p-prior-pin`) e o run real revelou um terceiro. O fechamento da produção deve registrar o estado final real (p-sensitivity pendente no instrumento real, não pass) e a causa como nota aberta upstream ao corpus; resumos da rodada não devem claimar "todos os gates pass" — os gates declarados na célula passaram; um gate global do instrumento ficou pendente.

**low** (alvo: guia-de-adocao): "preencha os contratos" usa "contratos" como guarda-chuva para os documentos fundadores (brief, fontes de verdade, canon, lista de artefatos, cartões de papel, gates); o corpus reserva "contrato" para o esquema que valida um artefato — sentido que o próprio guia usa em "dono único, contrato e gate mensurável" — e o termo entra sem definição na primeira uso. Um termo, dois sentidos. Trocar por "preencha os documentos da célula", ou definir "contrato" na anatomia e reservar a palavra para o esquema.

## Verificado e correto

- As quatro condições de aplicação e a degradação para "revisão por pares com rúbrica… não é compilação": `01-principle.md` (abertura; seções 9 e 10).
- Os três casos de "não use" (rascunho descartável; serviço contínuo — "serviço se roda, não se compila"; alvo exploratório — "laço, não grafo") e o custo por rodada: `01-principle.md`, seções 9 e 10.
- Anatomia, item a item: canon e "o que dois papéis poderiam escrever diferente mora aqui" (`10-generic-recipe.md`, passo 3); artefato tipado e grafo acíclico (passo 4); cartão de sete campos e "papel sem gate e sem nota é passo, não papel" (`skills/cooperatio-teamwork/SKILL.md`, passo 7; `01-principle.md`, seção 4); gate com magnitude e "'maior que zero' deixa instrumento quebrado passar" (`01-principle.md`, seção 4); nota de seis campos que mira a origem (`02-reflexive-application/01-canon.md`, termo "note"); validador com relatório determinístico (`01-canon.md`, "validator"; `10-generic-recipe.md`, passo 9); rúbrica congelada com hash antes da primeira produção (passo 8); priors pinados por sha256 com marca (`instances/registry.json`; `01-principle.md`, seção 9).
- Comando do scaffold (forma e bandeiras) e autoteste do validador sem entrada: `README.md` ("Using the skill"; "Running the validator").
- O caminho da produção (documentos fundadores → congelar rúbrica → onda 1 medida, não boa → validador → notas no registro de notas → onda 2 na origem, gate novo para regressão, instrumento consertado para falso positivo → rodada de revisão com executor distinto e três vereditos → documento de método e registro com status, documento e sha256): `10-generic-recipe.md`, passos 1 a 14; `01-principle.md`, seção 7.
- Estado do registro de instâncias: uma executada (`000-av-production`) e três desenhadas, não executadas (`001-car`, `002-text-2027`, `003-hpc`): `instances/registry.json`, por leitura direta.
- Claim auto-inclusiva ("este guia é a segunda execução — a instância 004, que se registra ao fechar a produção dele"): verdadeira no momento do registro e honesta na formulação — separa o estado atual do registro do ato futuro de registro; a numeração segue a do registro (000 a 003 registradas); o brief declara o registro como decisão de dono pendente, fase posterior a esta rodada.
- Números do prior sob a marca `[prior:000-av-production]` — "18 papéis" e "49 artefatos declarados no grafo": conferidos por leitura direta do documento de método da instância 000 (`4-comunicacao/7-producao/estudio/metodo-de-producao.md`, citado relativo à raiz do repositório dele): seção 1.1, "O método separa o trabalho em 18 papéis"; seção 2.1, "tem 49 artefatos". A caracterização "uma produção audiovisual em português do Brasil" confere ao documento. O run real confirma: `p-prior` com os três números da unidade marcada conferidos globalmente, 0 não verificados.
- "o método dela é o prior de onde o cooperatio extraiu as regras que este guia apresenta": `01-principle.md`, abertura ("every rule below was born from an error that cost a round").
- Limites declarados como limites (deriva entre dias; vários modelos não criam independência por si — família compartilha pontos cegos, quem vê o raciocínio herda; agente só, separação fraca, rúbrica e revisão de fora): `01-principle.md`, seção 9, correspondência de substância.
- Licença e obtenção: Apache License 2.0 (`LICENSE`); pasta autossuficiente; `README.md` por onde começar; `01-principle.md` com ideia, fórmula, onze componentes (contados na seção 4) e dez regras de ouro (contadas na seção 5); `02-reflexive-application/` com o recipe genérico de quinze passos, instâncias desenhadas e o validador; `CHANGELOG.md`; `instances/registry.json`; skill `skills/cooperatio-teamwork/` funcionando copiada sozinha, com scripts e referências (`SKILL.md`).
- Tamanho: 1054 palavras, contagem própria com a semântica do validador — igual ao run real e ao relatório da onda 2.
- Congelamento da rúbrica: sha256 da seção "Rubric" de `06-gates.md` recalculado por esta rodada (implementação própria autotestada em três vetores conhecidos) = `ba88324b5536e027c4d2b671c4bbc4433c8d195e2c79f7ba2f1b89bf2661f67f`, igual a `07-rubric.sha256` e às duas linhas do round-record; o run real confirma (`p-frozen-rubric`, equal).
- Anonimato do deliverable: grep próprio contra os 14 identificadores de `state/forbidden.txt` — zero ocorrências; sem caminho absoluto, sem data, sem nome de máquina ou de usuário; blocos de comando com caminhos relativos.
- Termos a evitar (17 termos do canon da célula) e tag HTML: zero ocorrências no deliverable, greps próprios.
- Auditoria da produção: as três notas da onda 1 estão no ledger (`state/notes.jsonl`) no contrato de seis campos; as duas de redação estão endereçadas no guia atual ("o prior de onde o cooperatio extraiu as regras que este guia apresenta"; "os achados viram notas no registro de notas") — item a item na tabela da onda 2, conferido no texto; a nota medium (re-execução do binário) foi endereçada pelo orquestrador com o run real; `state/round-record.jsonl` com duas linhas válidas contra o esquema (run real: `p-contract-shape`, 0 violações), `method_version` 0.2.2 = `VERSION`, `rubric_hash` igual à congelada nas duas linhas; `lessons.md` com entrada por onda; `09-engine/README.md` declara a decisão de não haver motor separado nesta escala.
- O caveat da sensibilidade (`08-validator/sensitivity.md`): registro de replicação mecânica das regras do fonte, rotulado como tal em três lugares (o próprio arquivo; a proveniência dos dois relatórios de onda; a nota medium do ledger), sem claim de código de saída. Julgamento pela rúbrica e pelo recipe: registro honesto e aceitável — a pendência da re-execução estava declarada onde a decisão acontece, e o run real a fechou para `p-prior`, `p-prior-pin` e o modo determinismo. O resíduo que o run real deixou é o finding medium acima.

## Não verificado

- O pin sha256 do documento do prior (`02f61349c00de94d93c64abcbbdf401f64216a555071bdb86e7d4bea643d25a0`): verificado pelo run real (`p-prior-pin`, equal), não recalculado por esta rodada — reconstruir byte a byte um documento de 1210 linhas para recalcular o digest arriscaria resultado falso por erro de reconstrução (a lição da onda 1 registra a mesma decisão). Estado: verificado por instrumento, não por leitura própria.
- "Caught 10 of 10" da replicação de sensibilidade: medida da réplica do produtor (código que rodou em memória no dispatch do writer, sem artefato para re-executar), não do binário; o run real deixou `p-sensitivity` pendente (finding medium).
- A contagem de 1052 palavras da onda 1: refere-se à versão anterior do guia, que não existe mais como arquivo; a contagem da versão atual (1054) foi verificada por esta rodada.
- `m-determinism`: medido pelo run real (sha256 igual em duas execuções); não re-executado por esta rodada.

## Fora de escopo

- Registro da instância 004 no registro de instâncias do corpus, linha no CHANGELOG e documento de método da instância: decisões de dono pendentes, fase posterior a esta rodada (`00-brief.md`).
- Defeitos do próprio corpus: o caminho da sensibilidade hardcoded no validador (causa do finding medium; a constante está também no fonte original, `02-reflexive-application/80-validator/validator.py`, linhas 41 a 43 — no corpus o caminho é o correto, e o defeito só se manifesta em células que usam `08-validator/`); o gap de perturbações para os gates de pin e contract-shape (adiância já declarada no CHANGELOG 0.2.2); a mistura executada/desenhada no registro (C16). São do corpus, não da célula; a nota medium recomenda o encaminhamento upstream.
- Reescrever o guia: o reviewer decide veredito e severidade, não conteúdo (cartão de papel).
- A compressão do "Como rodar" (os quinze passos do recipe em um parágrafo; o passo dos esquemas em `05-contracts/` e o teste de sensibilidade dos gates não são nomeados): escolha editorial legítima num guia de 900 a 1400 palavras que mapeia o leitor ao recipe; nenhuma claim falsa decorre dela — observação, não finding.

## Notas emitidas (no contrato de seis campos)

```text
{
  "target_artifact": "guia-de-adocao",
  "severity": "low",
  "text": "'preencha os contratos' usa 'contratos' como guarda-chuva para os documentos fundadores (brief, fontes de verdade, canon, lista de artefatos, cartões de papel, gates); o corpus reserva 'contrato' para o esquema que valida um artefato — sentido que o próprio guia usa em 'dono único, contrato e gate mensurável' — e o termo entra sem definição na primeira uso; trocar por 'preencha os documentos da célula' ou definir 'contrato' na anatomia e reservar a palavra para o esquema",
  "origin": "rodada de revisão 1 (reviewer)",
  "evidence": "guia-de-adocao.md, seções 'A ideia numa frase' e 'Como rodar uma produção'; corpus, 02-reflexive-application/01-canon.md, termo 'contract'",
  "round": 1
}
```

```text
{
  "target_artifact": "wave-reports",
  "severity": "medium",
  "text": "o run real do validador deixou p-sensitivity pendente: o binário procura 80-validator/sensitivity.md (constante SENSITIVITY_FILE, derivada de VALIDATOR_DIR hardcoded, fora do --layout) e o arquivo da célula está em 08-validator/sensitivity.md; o relatório da onda 2 previu 'os dois únicos pendentes' e o run real revelou um terceiro — o fechamento deve registrar o estado final real (p-sensitivity pendente no instrumento real, não pass), levar a causa como nota aberta upstream ao corpus e não claimar 'todos os gates pass' (os gates declarados na célula passaram; um gate global do instrumento ficou pendente)",
  "origin": "rodada de revisão 1 (reviewer)",
  "evidence": "08-validator/report.md, linha p-sensitivity ('80-validator/sensitivity.md', not measured, pending); 08-validator/validator.py, linhas 41-43 e 1397-1401; review/wave-2-report.md, seção 'Pendências' ('os dois únicos pendentes')",
  "round": 1
}
```

## Pendências para o fechamento

- Registrar as duas notas acima no ledger (`state/notes.jsonl`), rodada 1, e gravar este registro no `review/` da célula.
- Gravar a linha da rodada de revisão no round-record (`05-contracts/round-record.schema.json`): `method_version` 0.2.2, identificador da rodada de revisão, modelos da rodada (reviewer), summary, `verdict` "accepted", `rubric_hash` `ba88324b5536e027c4d2b671c4bbc4433c8d195e2c79f7ba2f1b89bf2661f67f`.
- No fechamento: `open-notes.json` deve carregar a nota medium (p-sensitivity pendente no instrumento real, com a causa e o encaminhamento upstream ao corpus) e, se a nota low não for endereçada, ela também; o resumo do fechamento deve dizer que os gates declarados passaram e que um gate global do instrumento ficou pendente, com a causa.
- A nota upstream ao corpus (caminho da sensibilidade ignora o `--layout`) vai ao dono do corpus pelo canal dele; a célula não edita o corpus.
