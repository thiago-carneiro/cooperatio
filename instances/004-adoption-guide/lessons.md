# Lessons: guia de adoção do cooperatio

What each round taught; what became code, contract or gate.

## Onda 1

- A prosa saiu dentro da faixa na primeira passada porque os seis itens do conteúdo mínimo do brief viraram a estrutura de seções antes de qualquer frase: escrever contra uma lista, não contra um rascunho.
- O tropo de quem escreve para quem leu o rascunho escapou a todos os gates: "as regras que agora lhe entrego" fala ao leitor interno. Pego no self-review, virou nota; um detector para esse defeito não existe — se a onda 2 mostrasse recorrência, seria candidato a gate.
- Sem shell no dispatch, a saída honesta foi replicar as regras por leitura integral do fonte do validador e registrar a re-execução do binário como pendência com o comando pronto — nunca claimar código de saída que não houve.
- O documento do prior tem 1210 linhas: embeber byte-exato para medir o pin sha256 seria arriscar falso pass; o caminho seguro foi conferir os números citados (18, 49) por leitura e deixar o pin pendente para a re-execução.

## Onda 2

- A replicação morde: o detector de caminho absoluto pegou um defeito no próprio relatório da onda 1 — um marcador de posição terminado em ">" colado numa barra virou "/02-reflexive..." e contou como caminho absoluto. Comandos de re-execução entram com caminho relativo desde a primeira passada, ou o relatório reprova o próprio gate de anonimato.
- A mesma regex de caminho absoluto tem lookbehind que protege colchetes e travessões de prefixo: entender POR QUE ela mordeu (o conjunto de caracteres protegidos no lookbehind) foi mais barato do que reformular o comando.
- O teste de sensibilidade na réplica pegou 10 de 10 defeitos injetados, incluindo os dois que a onda 1 não exercitou por não existirem ainda (identificador da lista externa, marca de prior não registrada). Instrumento que não foi testado contra defeito conhecido é gate de fé; o custo de testar em memória foi uma passada.
- A hash da rúbrica recalculada sobre a transcrição bateu byte a byte com a congelada — a transcrição do documento de gates ficou provada fiel pela própria hash que ela recalculou.

