# Aprendizados — AWS Data Engineering Lab (DEA-C01)

> **Objetivo:** registrar não apenas os comandos usados, mas **por que cada escolha foi feita**, como verificar seu efeito no Console da AWS e o que pode cair no exame **AWS Certified Data Engineer – Associate (DEA-C01)**.

>
> **Fonte de referência:** **AWS Certified Data Engineer Associate — The Complete Exam Revision Guide** (Johnny Chivers / Knowza, 2026). Quando uma observação vem da prática do laboratório, ela é identificada como tal. A documentação oficial AWS/Terraform prevalece em caso de mudanças de serviço, preço ou interface.

> **Como usar este arquivo:** as seções 1 a 6 reúnem os conceitos fundamentais e o estado de referência do início do projeto. **Toda nova etapa deve ser acrescentada ao final da seção 8**, sem criar novos tópicos acima ou editar registros antigos. Assim, o histórico permanece cronológico e fácil de acompanhar.
>
> **Regra de atualização:** só marcar um recurso como implantado ou validado após conferir o resultado. Informações pendentes devem permanecer como **não confirmadas**.

## 1. Contexto e método de estudo

**Caso de uso:** Data Lake de e-commerce com fontes fictícias de clientes, produtos, pedidos e pagamentos. A arquitetura será incrementada: ingestão batch → transformação → consultas analíticas → streaming → orquestração → observabilidade → governança.

**Fluxo de trabalho adotado:**

1. Declarar recursos em **Terraform** e versionar o código no GitHub.

2. Executar `terraform fmt`, `terraform validate` e `terraform plan`.

3. Revisar o plano **antes** do `terraform apply`.

4. Abrir o **Console AWS** depois do deploy para inspecionar configurações, estados, custos e resultados.

5. Registrar evidências (sem contas, tokens, IDs sensíveis nem dados privados) e uma reflexão sobre **trade-offs** e cenários de prova.

6. Remover recursos de laboratório quando não forem mais necessários.

**Ambiente local verificado em 21/11/2026:** Windows 11, terminal **Git Bash (UCRT64)**, AWS CLI `2.42.1`, perfil `dea-lab` autenticado como usuário IAM `terraform-dea-lab` por `aws sts get-caller-identity`. Não foi confirmada a execução bem-sucedida de `terraform apply`.

## 2. Terraform e AWS CLI

### 2.1 Conceitos
| Termo | Significado prático |
|---|---|
| Terraform CLI | Lê configuração HCL, calcula mudanças e as aplica via providers. |
| Provider AWS | Plugin que implementa a comunicação com APIs da AWS. |
| `resource` | Objeto de infraestrutura gerenciado pelo Terraform. |
| `variable` | Entrada parametrizável (ex.: nome do bucket e região). |
| `output` | Valor exposto após o deploy (ex.: ARN). |
| State (`terraform.tfstate`) | Mapeamento local entre configuração e recursos remotos; **pode conter segredos**. |
| `.terraform.lock.hcl` | Arquivo versionável que fixa as versões resolvidas dos providers. |
| `terraform plan` | Prévia de mudanças; não executa deploy. |
| `terraform apply` | Executa as mudanças aprovadas. |

**Ponto para portfólio:** o Terraform torna a configuração auditável e reproduzível, mas não substitui o monitoramento nem a revisão humana do plano.

### 2.2 Git Bash versus PowerShell

```bash

# Git Bash (sessão atual)

export AWS_PROFILE=dea-lab

export AWS_DEFAULT_REGION=us-east-1

aws sts get-caller-identity

```

No PowerShell, a sintaxe equivalente é `$env:AWS_PROFILE = "dea-lab"`. O erro `bash: :AWS_PROFILE: command not found` ocorreu porque foi utilizada sintaxe de PowerShell no Git Bash.

### 2.3 Autenticação e menor privilégio

- O IAM Identity Center não estava habilitado. Optamos **por não alterar a configuração organizacional da conta Free Plan** apenas para este laboratório.

- O usuário IAM `terraform-dea-lab` foi configurado e a identidade foi confirmada pelo STS.

- Nunca usar chaves do **root** nem versionar access keys, tokens, `.env` ou state.

- Autenticar com credenciais temporárias quando possível; conferir expiração/sessão antes de executar o Terraform.

- **Atenção:** `sts:GetCallerIdentity` confirmar a identidade **não comprova** permissões para criar S3. Tratar eventuais `AccessDenied` com a política mínima exigida.

## 3. Amazon S3: decisões de arquitetura

### 3.1 Por que S3 é o ponto de partida?

O S3 é um armazenamento de objetos que recebe dados estruturados e semiestruturados sem exigir servidor ou schema na entrada. É apropriado como base de um Data Lake e se integra a Glue e Athena (guia: domínio 2).

**Nossa organização proposta:**

```text

s3://<bucket>/

├── raw/       # Entrada original; preservar para rastreabilidade e reprocessamento

├── trusted/   # Dados tipados, limpos e validados

└── delivery/  # Tabelas analíticas prontas para consumo

```

**Atenção:** “pastas” no S3 são **prefixos de chave**, não diretórios reais. Os objetos e as partições aparecerão ao longo do projeto.

### 3.2 Bloqueio de acesso público

Recurso Terraform: `aws_s3_bucket_public_access_block` com as quatro opções em `true`.
| Configuração | Intenção |
|---|---|
| `block_public_acls` | Impede adicionar novas ACLs públicas. |
| `ignore_public_acls` | Desconsidera ACLs públicas existentes ao avaliar acesso. |
| `block_public_policy` | Impede configurar novas bucket policies que concedam acesso público. |
| `restrict_public_buckets` | Restringe acesso decorrente de políticas públicas. |

**Ponto importante para a certificação:** bloquear acesso **público** não é o mesmo que conceder acesso a uma aplicação. O acesso legítimo ainda deve ser controlado por **IAM policies**, bucket policies e, em etapas futuras, pelo **Lake Formation** para permissões mais granulares.

**Como verificar no Console:** S3 → bucket → **Permissions** → **Block public access (bucket settings)**.

### 3.3 SSE-S3 versus SSE-KMS

Recurso Terraform: `aws_s3_bucket_server_side_encryption_configuration` com `sse_algorithm = "AES256"`.

- **SSE-S3:** o S3 gerencia as chaves de criptografia; boa opção de baixo atrito e custo para o laboratório. O S3 já criptografa novos objetos por padrão.

- **SSE-KMS:** usa AWS KMS; traz controle de políticas/chaves e trilhas de auditoria mais específicas, mas pode gerar custos adicionais de chave e requisições.

- **TLS:** criptografia **em trânsito** é diferente de criptografia **em repouso**. Uma não substitui a outra.

**Ponto importante para a certificação:** se o cenário exige controle do ciclo de vida da chave, permissões sobre a chave ou requisitos regulatórios específicos, avaliar **SSE-KMS com chave gerenciada pelo cliente**. Para um laboratório simples, SSE-S3 é suficiente.

**Como verificar no Console:** S3 → bucket → **Properties** → **Default encryption**.

### 3.4 Object Ownership e ACLs

Recurso Terraform: `aws_s3_bucket_ownership_controls` com `BucketOwnerEnforced`.

Isso desabilita ACLs e centraliza o controle de acesso em políticas. Evita a complexidade de administrar permissões ACL por objeto.

**Ponto importante para a certificação:** distinguir **IAM identity policies**, **S3 bucket policies**, **ACLs legadas** e **Lake Formation** (que controla o acesso analítico a bancos, tabelas e, conforme integração, colunas/linhas).

**Como verificar no Console:** S3 → bucket → **Permissions** → **Object Ownership**.

### 3.5 Exclusão e versionamento

- `force_destroy = false`: o Terraform **não excluirá automaticamente** um bucket que contenha objetos. É uma proteção contra perda de dados e exige limpeza antes de um `destroy` definitivo.

- **Bucket versioning** não foi declarado no código inicial: o estado padrão esperado para um bucket novo é **Disabled**. Se desejarmos gerenciá-lo de forma explícita, adicionaremos um recurso apropriado.

- Versioning aumenta resiliência contra sobrescritas/exclusões, mas mantém versões que podem gerar custos de armazenamento.

**Como verificar no Console:** S3 → bucket → **Properties** → **Bucket Versioning**.

### 3.6 Tags e custos

No provider, `default_tags` aplica `Project`, `Environment` e `ManagedBy` aos recursos compatíveis. Tags facilitam identificação e governança. Para analisar custos por tag no Cost Explorer, pode ser necessário **ativar a tag como cost allocation tag** no Billing.

**Como verificar no Console:** S3 → bucket → **Properties** → **Tags**; Billing → Cost allocation tags (quando aplicável).

## 4. Custos e segurança operacional

- O laboratório tem **orçamento de referência de US$ 5 por mês**, alertas sugeridos de US$ 1, US$ 3 e US$ 5, e meta inicial de consumo bruto inferior a US$ 1. **A configuração real dos alertas ainda precisa ser confirmada.**

- **Budget é alerta, não bloqueio automático**: notificações e dados de faturamento podem sofrer atrasos.

- Preferir região `us-east-1` para o laboratório e evitar recursos ativos sem necessidade.

- Validar **Free Plan, créditos, saldo, serviço elegível e preço atual** antes de Glue, Kinesis, Redshift, DMS, EMR ou endpoints privados pagos.

- Evitar grandes volumes e deixar serviços provisionados por horas/dias. Planejar `terraform destroy` quando possível.

- O state local fica fora do GitHub. Uma migração futura para backend remoto exige estudo de segurança, bloqueio de state e custos.

## 5. Mapa de questões da certificação (baseado no guia)
| Domínio do guia | Peso informado | Decisões que precisamos praticar |
|---|---:|---|
| 1. Data Ingestion & Transformation | 34% | Glue vs Lambda vs EMR; batch vs streaming; Kinesis Streams vs Firehose; bookmarks; orquestração |
| 2. Data Store Management | 26% | S3 e classes de armazenamento; Redshift vs Athena; DynamoDB vs RDS; formatos e particionamento |
| 3. Data Operations & Support | 22% | Athena e custo por leitura; CloudWatch vs CloudTrail; data quality; alarmes e reprocessamento |
| 4. Data Security & Governance | 18% | IAM least privilege; Lake Formation; SSE-S3 vs SSE-KMS; governança e auditoria |

### Perguntas de revisão — Etapa S3

1. Por que armazenar dados brutos no S3 antes de transformá-los?

2. Qual é a diferença entre bloqueio de acesso público e permissões IAM?

3. Em qual cenário SSE-KMS seria preferível a SSE-S3?

4. O que `BucketOwnerEnforced` muda no uso de ACLs?

5. Por que `force_destroy = false` é adequado ao laboratório?

6. Como tags ajudam na governança? Por que não garantem, sozinhas, visibilidade de custos por projeto?

7. Por que `terraform plan` é obrigatório antes de `terraform apply`?

8. Qual a diferença entre `terraform.tfstate` e `.terraform.lock.hcl`?

## 6. Estado de referência antes dos próximos registros
| Item | Estado conhecido em 21/11/2026 | Evidência necessária |
|---|---|---|
| GitHub e estrutura do projeto | Informado como feito | Link/commit do repo |
| IAM `terraform-dea-lab` | **Validado** | `aws sts get-caller-identity` (omitir identificadores públicos em screenshots, se desejado) |
| Terraform CLI instalado | A confirmar | `terraform -version` |
| `terraform init / validate / plan` | Usuário informou “feito”; saída não revisada | Saída de `validate` e resumo do `plan` |
| `terraform apply` | **Não confirmado** | Saída de `apply` |
| Bucket S3 no Console | **Não confirmado** | Capturas de Permissions/Properties/Tags |
| Alertas de custos ativos | **Não confirmado** | Orçamento e notificações no Billing |

## 7. Padrão para registrar as próximas etapas

O conteúdo desta seção é apenas um **modelo de consulta**, não uma etapa executada. Antes de cada commit, preencher um registro e **anexá-lo ao final deste arquivo, na seção 8**. Não é necessário reescrever seções anteriores.

```markdown
### AAAA-MM-DD — Etapa X: Título da atividade

**Status:** Concluída / Parcial / Pendente de validação

#### O que implementamos
- Descrever apenas o que foi realmente realizado.

#### Conceitos aprendidos
- Explicar os conceitos técnicos novos, com exemplos curtos.

#### Decisões de arquitetura
- Explicar as escolhas e, quando relevante, alternativas e trade-offs.

#### Ponto importante para a certificação DEA-C01
- Destacar o raciocínio por trás da escolha do serviço ou configuração.

#### Validação prática
- [ ] Terraform: fmt, validate e plan revisados
- [ ] Apply confirmado (quando aplicável)
- [ ] Console/CLI verificados (quando aplicável)

**Custo observado:** Não verificado / US$ ...
**Problemas e soluções:** Nenhum / ...
**Evidências:** caminho dos prints ou referência do commit (se disponível).

---
```

**Convenções:** manter títulos no mesmo nível (`###`), subtítulos com `####`, usar checklists apenas para validações verificáveis e colocar `---` **ao final de cada registro**, para separar claramente a próxima adição. Não registrar IDs de conta, chaves ou tokens.

## 8. Diário cronológico de aprendizagem

*Novos registros devem ser adicionados abaixo desta linha. Nunca colocar uma seção de encerramento ou “última atualização” depois do diário; o final do arquivo estará sempre livre para a próxima etapa.*

### 2026-11-21 — Etapa 4: Estrutura de prefixos do Data Lake

**Status:** Código proposto; aplicação e inspeção ainda não confirmadas.

#### O que implementamos
- Foi definido o arquivo `s3_structure.tf` para criar marcadores de pastas no S3 com Terraform.
- Os caminhos previstos abrangem `raw/`, `trusted/` e `delivery/` e suas entidades.
- **Não há confirmação da execução do `terraform apply` para esses objetos.**

#### Conceitos aprendidos
- O S3 armazena objetos com chaves; “pastas” no Console são representações de prefixos.
- `locals` permite declarar valores internos reutilizáveis em Terraform.
- `for_each` cria instâncias por elemento; `toset()` elimina duplicatas da coleção.
- `aws_s3_bucket.data_lake.id` cria referência e dependência implícita entre recursos.

#### Decisões de arquitetura
- Usar um único bucket com prefixos para reduzir complexidade e facilitar o aprendizado.
- Usar objetos vazios como marcadores de pastas para visualizar a estrutura antes da ingestão. Os marcadores não são necessários para gravar arquivos com aqueles prefixos.

#### Ponto importante para a certificação DEA-C01
- **Prefixos do S3 não são automaticamente partições do Athena ou do Glue Catalog.** O layout e os metadados das partições precisam ser reconhecidos pelo mecanismo de consulta.
- **RAW, TRUSTED e DELIVERY são convenções de arquitetura**, e não camadas nativas obrigatórias do S3.

#### Validação prática
- [ ] `terraform fmt` e `terraform validate` executados após adicionar `s3_structure.tf`.
- [ ] `terraform plan` revisado para os 10 objetos esperados.
- [ ] `terraform apply` concluído com sucesso.
- [ ] Os prefixos foram inspecionados no Console do S3.
- [ ] `terraform plan` final não indica mudanças pendentes.

**Custo observado:** Não verificado.
**Problemas e soluções:** Nenhum registrado até o momento.
**Evidências:** Pendentes.

---
