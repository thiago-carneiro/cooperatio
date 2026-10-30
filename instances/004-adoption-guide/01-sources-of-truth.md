# Sources of truth: guia de adoção do cooperatio

One source per content type; the source that errs least, never the writer.

Canon: [02-canon.json](02-canon.json)

O corpus desta produção é o material do cooperatio, citado por caminho relativo à raiz dele; a raiz entra como variável de linha de comando, nunca escrita num artefato. O documento de método da instância registrada anterior fica fora deste material e é citado relativo à raiz do repositório dele.

| Content type | Source that errs least | Who consults it | Forbidden as a source |
| --- | --- | --- | --- |
| fato sobre o método | o corpus do cooperatio (`01-principle.md`, `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`) | verifier | o writer; um modelo generativo; a memória de qualquer papel |
| número sobre o método | o corpus (`01-principle.md`, seções 4, 5 e 7; `02-reflexive-application/10-generic-recipe.md`; `instances/registry.json`) somado ao canon desta célula | verifier | a prosa que o cita |
| número sobre a instância anterior | o documento de método da instância `000-av-production`, pinado por sha256 no registro | verifier | qualquer documento desta célula; lembrança de rodada |
| texto exato citado do corpus | o arquivo citado, entre aspas, com o caminho dele | verifier | paráfrase do writer |
| identificador local proibido | `state/forbidden.txt` | validator | o julgamento do writer |
