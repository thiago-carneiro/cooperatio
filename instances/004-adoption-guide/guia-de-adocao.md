# Guia de adoção do cooperatio

O cooperatio é um método para organizar um time — pessoas, agentes de linguagem e código — em torno de um alvo complexo. Este guia é para quem quer adotá-lo: o que ele é, para quem serve (e para quem não), a anatomia de uma célula de produção, o caminho de uma produção do scaffold ao registro, e o que a evidência hoje sustenta. Toda afirmação de fato sobre o método aqui é conferível no material dele, citado por nome de arquivo.

## O que é o cooperatio

A ideia numa frase: produza o alvo compilando um grafo de artefatos tipados — cada um com dono único, contrato e gate mensurável — em que papéis separados conversam apenas por artefatos e notas; a qualidade é o que o sistema entregou, medido, e não o que foi pedido; toda revisão é independente e comparável entre rodadas; todo erro que escapa vira um gate novo; e a produção para num critério declarado antes da última rodada.

Em vez de "um agente muito capaz faz tudo", uma pequena organização com contratos explícitos: a inteligência é matéria-prima, e o código é a cola que compõe, confere e lembra. A qualidade não nasce da confiança no modelo; nasce dos contratos e dos gates. Um agente que escreve e confere o próprio trabalho compartilha os próprios pontos cegos — separar quem faz de quem mede é o que traz um segundo olhar que não os compartilha.

## Para quem serve — e para quem não

O método vale onde o alvo tem quatro condições: um brief que o dono consegue declarar, com critério de parada; um artefato discreto, montável a partir de partes; fontes de verdade separáveis por tipo de conteúdo; e dependências entre as partes que ficam acíclicas. Onde uma condição falta, o método degrada — para revisão por pares com rúbrica, que ainda é melhor que nada, mas não é compilação.

Não use para um rascunho descartável: o custo por rodada é uma produção inteira, uma revisão independente e a manutenção dos instrumentos, e isso só se paga quando errar é caro. Não use para um serviço contínuo, sem momento de pronto — serviço se roda, não se compila. E não use para um alvo exploratório, cuja próxima pergunta depende da resposta anterior: isso é um laço, não um grafo.

## Anatomia de uma célula de produção

A célula de produção é a organização montada para um alvo. O que há nela:

- **Canon** — a fonte única de números, nomes, termos a evitar, variantes aceitas e regras; cada seção com dono e versão. O que dois papéis poderiam escrever diferente mora aqui.
- **Artefatos e grafo** — cada saída intermediária é um arquivo tipado, com nome, dono único, caminhos, esquema, dependências e gates; o grafo é acíclico, e só o que ficou desatualizado é refeito.
- **Papéis e cartões** — cada papel tem um cartão de sete campos: decide, não decide, entradas, saídas, gate de saída, notas que emite, grau de conversão em código. Papel sem gate e sem nota é passo, não papel.
- **Gates com magnitude** — um gate devolve a medida, com limite justificado por rótulo de origem; "maior que zero" deixa instrumento quebrado passar.
- **Notas roteirizadas** — o único pedido de mudança entre papéis: alvo, severidade, texto, origem, evidência, rodada. A nota mira onde o defeito nasceu, não onde foi visto.
- **Validador** — código que lê os artefatos contra o canon e emite notas sozinho, com relatório determinístico.
- **Rúbrica congelada** — as dimensões, âncoras e a regra de veredito de toda revisão, com o hash gravado antes da primeira produção.
- **Priors** — o registro de instâncias anteriores, pinadas por sha256; toda afirmação sobre elas leva marca que a torna conferível.

## Como rodar uma produção

Primeiro, monte a célula com o scaffold do skill `cooperatio-teamwork`:

```text
python skills/cooperatio-teamwork/scripts/scaffold.py \
    --target "Meu alvo" --roles writer verifier reviewer \
    --out ./celula
```

Depois, em ordem: preencha os contratos — brief, fontes de verdade, canon, lista de artefatos, cartões de papel, gates. Congele a rúbrica antes de produzir. Faça a onda 1: a versão inteira, rapidamente — ela existe para ser medida, não para ser boa — e rode o validador; os achados viram notas no registro de notas. Na onda 2, enderece as notas na origem: crie gate para a regressão que escapou, conserte o instrumento para o falso positivo, e rode o validador de novo. Então vem a rodada de revisão: um executor distinto do produtor aplica a rúbrica congelada e dá o veredito — rejeitado, aceito com condições, ou aceito. Fecham a produção o documento de método da instância e o registro dela (status, documento, sha256) no registro de instâncias.

O validador traz um autoteste que roda sem nenhuma entrada:

```text
python 02-reflexive-application/80-validator/validator.py --self-test
```

## O que a evidência mostra

Com honestidade: o material se declara uma hipótese de trabalho. No registro de instâncias há uma execução concluída e três instâncias desenhadas, não executadas; este guia é a segunda execução — a instância 004, que se registra ao fechar a produção dele. A primeira instância executada, uma produção audiovisual em português do Brasil, organizou o trabalho em 18 papéis e 49 artefatos declarados no grafo [prior:000-av-production]; o método dela é o prior de onde o cooperatio extraiu as regras que este guia apresenta.

Os limites, declarados onde estão: papéis exercidos por modelos derivam entre dias — os contratos e os gates existem para absorver isso; usar vários modelos não cria independência por si (modelos da mesma família compartilham pontos cegos, e modelo que vê o raciocínio do produtor o herda); e com um agente só a separação é fraca — nesse caso, ao menos a rúbrica e a revisão têm que vir de fora.

## Licença e como obter o material

O material é distribuído sob a Apache License 2.0 (arquivo `LICENSE`), como uma pasta autossuficiente: o `README.md`, por onde começar; o `01-principle.md`, o método em si — ideia, fórmula, onze componentes, dez regras de ouro; o `02-reflexive-application/`, o método aplicado a si mesmo, com o recipe genérico de quinze passos, instâncias desenhadas e o validador; o `CHANGELOG.md`, o histórico de versões; e o `instances/registry.json`, o registro de instâncias. A pasta do skill `skills/cooperatio-teamwork/` funciona copiada sozinha, com scripts e referências próprios.
