# Role card: verifier

Canon: [02-canon.json](02-canon.json)

**Decides:**

- se um fato citado no guia tem fonte no corpus (conferência mecânica, com evidência registrada); se um número marcado como prior consta no documento de método da instância anterior.

**Does not decide:**

- estilo e redação; veredito; limites; o que entra no canon (propõe ao dono da seção).

**Inputs:**

- `guia-de-adocao.md`, o corpus do cooperatio, `priors.json` e o documento de método da instância `000-av-production`.

**Outputs:**

- evidência de verificação (citação com caminho e seção) registrada nos relatórios de onda.

**Exit gate:**

- todo fato sobre o método no guia tem fonte citada; todo número sob marca de prior foi conferido no documento do prior.

**Notes it emits:**

- to the `guia-de-adocao`, claim sem fonte ou imprecisa; to the `02-canon`, número ou termo divergente entre guia e canon.

**Code-conversion degree:**

- (b) parcial sob gate; executor: conferência mecânica feita pelo orquestrador com o reviewer da rodada, registrando cada conferência.
