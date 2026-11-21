# Plano mestre — AWS Data Engineering Lab (DEA-C01)

> **Documento de continuidade:** mantenha este arquivo no GitHub como fonte de verdade do escopo, decisões, progresso, comandos, restrições de custo e próximos passos. Ao retomar o projeto em outra conversa, compartilhe este arquivo e o `LEARNINGS.md`.
>
> **Data-base:** 21/11/2026. **Status:** preparação inicial do primeiro deploy S3. O `terraform apply` **ainda não foi confirmado**.

## 1. Objetivo e critérios de sucesso

**Objetivo principal:** construir uma plataforma de dados de e-commerce sobre a AWS, evoluindo um Data Lake em laboratório prático para a certificação **AWS Certified Data Engineer – Associate (DEA-C01)** e para um **portfólio público**.

**Metodologia obrigatória:**

- **Terraform-first:** infraestrutura declarada em HCL; não criar recursos manualmente no Console salvo exceção justificada.
- **Console como validação:** depois de cada `terraform apply`, abrir o serviço AWS e verificar recursos e configurações, registrando aprendizados.
- **Tutorial passo a passo:** explicar o propósito, o código essencial, comandos, o plano e a validação; não avançar vários serviços de uma vez.
- **Comentários nos códigos:** **pontuais e úteis**, principalmente sobre decisões arquiteturais e comportamento não óbvio; evitar comentar toda linha. Esse padrão vale também para Python/SQL e outros códigos futuros.
- **Exame + portfólio:** associar cada implementação a situações de prova e documentar arquitetura, trade-offs, evidências e custos.
- **Controle financeiro:** consultar crédito/uso e orçamento antes de serviços de cobrança contínua; remover recursos quando não forem usados.

**Critérios de conclusão do projeto:** infraestrutura reproduzível, ingestão batch e streaming simuladas, dados catalogados e consultáveis, transformação incremental com qualidade, segurança e monitoramento, documentação atualizada, custos explicados e limpeza final ensaiada.

## 2. Contexto técnico confirmado

| Item | Informação |
|---|---|
| Máquina | Windows 11 |
| Terminal | Git Bash (`UCRT64`), **não** PowerShell |
| Repositório | `aws-data-engineering-lab` (criado pelo usuário; URL não fornecida) |
| Diretório do repo | `D:/github/aws-data-engineering-lab` |
| Projeto | `projects/01-ecommerce-data-lake/` |
| Terraform | Diretório `projects/01-ecommerce-data-lake/terraform/` |
| AWS CLI | `2.42.1` |
| Perfil AWS CLI | `dea-lab` |
| Identidade IAM | `terraform-dea-lab` (confirmada via STS) |
| Região do laboratório | `us-east-1` |
| Conta | Conta AWS com créditos gratuitos informados pelo usuário; verificar saldo e elegibilidade no Billing |
| Autenticação | IAM usuário; Identity Center não estava habilitado; não usar root ou segredos no GitHub |
| Provider AWS | `>= 6.23.0, < 7.0.0` proposto |
| Terraform CLI | `>= 1.6.0` proposto; versão instalada ainda não verificada aqui |

**Segurança:** não registrar números de conta, chaves, tokens, ARNs completos sensíveis ou dados reais no documento de portfólio. Os valores de nomes de recursos são exemplos e devem ser verificados no ambiente.

## 3. Estrutura-alvo do repositório

```text
aws-data-engineering-lab/
├── README.md                         # Visão geral e índice dos projetos
├── .gitignore                        # State, tfvars, segredos e artefatos locais
└── projects/
    └── 01-ecommerce-data-lake/
        ├── README.md                 # Objetivo, arquitetura, execução e resultados
        ├── terraform/
        │   ├── versions.tf
        │   ├── providers.tf
        │   ├── variables.tf
        │   ├── main.tf
        │   ├── outputs.tf
        │   └── terraform.tfvars        # Local; NÃO versionar
        ├── data/                     # Pequenos dados sintéticos
        ├── scripts/                  # Python, geradores, testes e SQL
        └── docs/
            ├── PROJECT_PLAN.md       # Este documento
            ├── LEARNINGS.md          # Registro cumulativo de aprendizados
            ├── architecture/         # Diagramas
            └── evidence/             # Capturas sem informações sensíveis
```

**Convenção:** scripts e dados pequenos podem ser versionados; datasets grandes, logs, estados, planos binários e credenciais ficam fora do repositório. A pasta `docs/` é a fonte documental de continuidade.

## 4. Arquitetura-alvo (construção progressiva)

```text
Fontes sintéticas de e-commerce
    ├─ CSV / JSON (cargas batch)
    │      ↓
    │  Amazon S3 — raw
    │      ↓
    │  AWS Glue (Catalog, Crawler, ETL, Data Quality)
    │      ↓
    │  Amazon S3 — trusted (Parquet/partições)
    │      ↓
    │  Amazon S3 — delivery
    │      ↓
    │  Amazon Athena (consultas SQL)
    │
    └─ Eventos simulados de compras
           ↓
       Kinesis Data Streams / Lambda
           ↓
       DynamoDB e/ou S3

Controle de execução: EventBridge + Step Functions (+ SQS/SNS conforme cenário)
Observabilidade: CloudWatch + CloudTrail
Segurança/governança: IAM + S3 + Lake Formation
```

Isso é uma **visão final**, não uma lista de serviços a provisionar agora. Cada etapa só adicionará os recursos necessários.

## 5. Roadmap executável

O plano abaixo explicita dependências, entregáveis, validação no Console, conhecimento de prova e custo. Marque cada checklist **somente depois de confirmar a execução**.

### Fase 0 — Repositório, ambiente e controle financeiro

- [x] Criar repositório GitHub `aws-data-engineering-lab` (informado pelo usuário).
- [x] Criar identidade IAM e validar AWS CLI com `aws sts get-caller-identity`.
- [ ] Confirmar versão instalada de Terraform e funcionamento do provider com o método de autenticação.
- [ ] Confirmar perfil, região, saldo de créditos, tipo de plano e vencimento no Billing.
- [ ] Criar/verificar **AWS Budget** (sugestão: US$ 5/mês com alertas US$ 1 / US$ 3 / US$ 5); observar que orçamento **não interrompe recursos**.
- [ ] Confirmar `.gitignore` e não versionar state, `.tfvars`, tokens, arquivos de plano ou segredos.
- [ ] Registrar o primeiro commit com arquivos HCL e docs.

**Entrega:** repositório preparado e autenticação comprovada, sem provisionamento oneroso.

### Fase 1 — Fundamentos S3 por Terraform (etapa atual)

- [x] Definir arquivos `versions.tf`, `providers.tf`, `variables.tf`, `main.tf` e `outputs.tf` com comentários concisos (fornecidos na conversa; confirmar commit).
- [x] Definir bucket privado, bloqueio das quatro formas de acesso público, SSE-S3 e `BucketOwnerEnforced` no código (fornecido na conversa).
- [ ] Confirmar `terraform fmt`, `terraform validate` e saída completa de `terraform plan` (**esperado:** 4 a adicionar, 0 a alterar, 0 a destruir; sem garantir até revisar a saída).
- [ ] Confirmar permissões IAM necessárias e corrigir `AccessDenied` de modo restrito se ocorrer.
- [ ] Executar `terraform apply` somente após revisar o plano e o orçamento.
- [ ] No Console S3, confirmar bucket, região, criptografia, acesso público, propriedade dos objetos, tags e versionamento.
- [ ] Executar `terraform state list`, `terraform output`, `terraform plan` (esperado: **No changes**).
- [ ] Documentar screenshots e custos reais em `LEARNINGS.md`.

**Entrega:** um bucket gerenciado pelo Terraform, verificável no Console.

**Conceitos DEA-C01:** S3, políticas versus ACL, SSE-S3 versus SSE-KMS, segurança por padrão, versionamento, tags, conceitos de infraestrutura.

### Fase 2 — Ingestão batch, camadas e dados fictícios

- [ ] Criar prefixos `raw/`, `trusted/` e `delivery/` via Terraform ou pela gravação dos primeiros objetos (decidir e documentar; prefixos S3 não são diretórios reais).
- [ ] Definir dataset sintético: `clientes`, `produtos`, `pedidos`, `pagamentos` (CSV/JSON). Arquivos pequenos e reproduzíveis.
- [ ] Construir script Python para gerar/enviar dados de teste com segurança e idempotência.
- [ ] Organizar objetos por entidade e, quando fizer sentido, por data de ingestão.
- [ ] Inspecionar objetos, prefixos, tipos e tamanho no Console S3.

**Entrega:** datasets brutos disponíveis no S3 com origem/documentação rastreáveis.

**Conceitos DEA-C01:** batch ingestion, formatos, schema-on-read, S3 prefix/partition e políticas de ciclo de vida.

### Fase 3 — Catálogo e consultas SQL

- [ ] Provisionar Glue Data Catalog e tabelas (comparar definição manual via DDL/Terraform com Crawler).
- [ ] Se executar Crawler, limitar escopo e número de execuções; conferir preço e permissões.
- [ ] Configurar local de resultados de consultas Athena e limites adequados.
- [ ] Consultar CSV com Athena: `SELECT`, filtros, joins, agregações e CTEs.
- [ ] Medir bytes escaneados, custo estimado e registrar resultados.
- [ ] Explorar no Console Glue (database/table/schema) e Athena (queries/results).

**Entrega:** dados brutos catalogados e consultáveis.

**Conceitos DEA-C01:** Glue Catalog, Crawlers, Athena e schema-on-read.

### Fase 4 — ETL, Parquet, partições e incremental

- [ ] Construir ETL para limpar, tipar, deduplicar e combinar entidades.
- [ ] Comparar execução local/Python com Glue para discutir trade-offs antes de pagar por Spark.
- [ ] Gravar TRUSTED em Parquet particionado e DELIVERY com indicadores: vendas por dia, por categoria e ticket médio.
- [ ] Comparar CSV versus Parquet e partições pelo volume escaneado no Athena.
- [ ] Simular segunda carga, novas linhas e testes de reprocessamento.
- [ ] Implementar **Glue Job Bookmarks** se o laboratório usar Glue job compatível, conferindo comportamento e limitações.
- [ ] Criar verificações de qualidade (nulos, duplicidade, integridade, valores inválidos) e avaliar Glue Data Quality.

**Entrega:** pipeline batch incremental, mensurável e testado.

**Conceitos DEA-C01:** ETL/ELT, PySpark, DynamicFrame/DataFrame, Parquet, partition pruning, bookmarks, qualidade.

### Fase 5 — Streaming de eventos

- [ ] Criar produtor Python de eventos de compra fictícios.
- [ ] Testar Kinesis Data Streams → Lambda, com batch pequeno e retenção mínima adequada.
- [ ] Persistir resultados em S3 ou DynamoDB com idempotência e tratamento de falhas.
- [ ] Comparar Streams vs Data Firehose vs MSK no papel, com uma implementação controlada.
- [ ] Conferir métricas e consumidores no Console; apagar streams e recursos no fim da prática.

**Entrega:** demonstração de eventos em tempo real e comparação de serviços.

**Conceitos DEA-C01:** shards, partition key, consumidores, near-real-time e alternativas AWS.

### Fase 6 — Orquestração e operação

- [ ] Acionar pipeline por EventBridge (horário ou evento).
- [ ] Orquestrar tarefas com Step Functions, retries, `Catch` e caminhos de falha.
- [ ] Considerar SQS/DLQ e SNS para desacoplamento e notificação se necessários ao cenário.
- [ ] Criar logs, métricas, alarmes e dashboards mínimos no CloudWatch.
- [ ] Diferenciar CloudWatch (**observabilidade**) e CloudTrail (**ações de API/auditoria**).
- [ ] Simular falhas e verificar reprocessamento e tratamento de erros.

**Entrega:** pipeline orquestrado, monitorado e recuperável.

**Conceitos DEA-C01:** Step Functions vs Glue Workflows vs MWAA; EventBridge; SQS/SNS; operações e suporte.

### Fase 7 — Segurança e governança

- [ ] Revisar IAM least privilege por recurso/serviço.
- [ ] Comparar IAM policy, bucket policy, ACLs e controles do Lake Formation.
- [ ] Testar permissões de leitura analítica de tabelas/colunas com Lake Formation, caso permitido pelo plano e custo.
- [ ] Revisar TLS, SSE-S3/SSE-KMS, logs de auditoria e cuidados com dados sensíveis.
- [ ] Preparar uma matriz de quem pode ler/gravar RAW, TRUSTED e DELIVERY.

**Entrega:** matriz de permissões e testes de acesso documentados.

**Conceitos DEA-C01:** IAM, Lake Formation, encryption, governance, lineage, compliance.

### Fase 8 — Laboratórios complementares (curtos e opcionais)

- [ ] **DynamoDB:** partition/sort key, GSI/LSI, modos On-Demand/provisionado, Streams.
- [ ] **Redshift:** COPY/UNLOAD, distribution styles, sort keys, Spectrum (testar brevemente apenas se custo/plano permitirem).
- [ ] **CDC/DMS:** explicar full load vs CDC e simular mudanças com PostgreSQL local; provisionar DMS apenas com teto explícito de gasto e elegibilidade verificada.
- [ ] **EMR/MSK/QuickSight:** revisar arquitetura e cenários de prova sem criar clusters/assinaturas persistentes desnecessárias.

**Entrega:** matriz de escolha de serviços e evidências de experimentos relevantes.

### Fase 9 — Fechamento do portfólio e exame

- [ ] Atualizar README principal e README do projeto, com objetivo, diagrama, pré-requisitos, comandos, segurança, custo e resultados.
- [ ] Registrar prints (sem identificadores ou segredos) de Console S3, Glue, Athena, CloudWatch e outros usados.
- [ ] Documentar métricas: tamanho da fonte, bytes lidos, execução, erros, custo observado.
- [ ] Fazer revisão por domínio (pesos do guia: 34%, 26%, 22%, 18%).
- [ ] Elaborar questões e cenários comparativos para consolidar decisões.
- [ ] Praticar limpeza com `terraform plan -destroy` e `terraform destroy`, respeitando dados e serviços adicionais.
- [ ] Confirmar recursos remanescentes e gastos após cleanup.

**Entrega:** projeto reproduzível, publicável e alinhado à DEA-C01.

## 6. Regra de orçamento e custo

**Crédito relatado:** US$ 100 iniciais (conferir saldo vigente e condições específicas no Billing; não assumir que todos os serviços estão disponíveis no Free Plan).

**Planejamento inicial sugerido, não previsão de cobrança:**

| Área | Teto reservado |
|---|---:|
| S3 + Athena + catálogo | US$ 15 |
| Glue e Spark | US$ 30 |
| Streaming/Kinesis | US$ 20 |
| Redshift/experimentos | US$ 10 |
| Observabilidade e segurança | US$ 10 |
| Reserva para testes e erros | US$ 15 |
| **Total** | **US$ 100** |

**Regras:**

1. Antes de cada serviço novo, conferir preço e se é permitido no plano da conta.
2. Estimar duração/volume, criar critério de parada e limite de experimentos.
3. Evitar recursos persistentes caros (ex.: clusters, streams, endpoints, NAT gateways).
4. Conferir Billing e Cost Explorer periodicamente; **Budgets alerta, mas não é hard cap**.
5. Registrar custo estimado e custo observado no diário.
6. Preferir `terraform destroy` para infraestrutura transitória, com revisão de proteção de dados e dependências.

## 7. Comandos operacionais padronizados (Git Bash)

```bash
# Partindo da raiz do repositório
cd projects/01-ecommerce-data-lake/terraform

# Autenticação da sessão Git Bash
export AWS_PROFILE=dea-lab
export AWS_DEFAULT_REGION=us-east-1
aws sts get-caller-identity

# Ciclo seguro de infraestrutura
terraform init
terraform fmt
terraform validate
terraform plan
# Revisar o plano antes de executar:
terraform apply

# Inspeção e conferência
terraform state list
terraform output
terraform plan

# Limpeza — executar apenas quando desejar realmente remover recursos
terraform plan -destroy
terraform destroy
```

**Importante:** se usar `aws login`, reautenticar conforme expiração das credenciais temporárias. Nunca rodar `terraform destroy` às cegas: o bucket está configurado com `force_destroy = false` e exige estar vazio para exclusão.

## 8. Próxima ação exata (ponto de retomada)

**Não presumir que o bucket já existe.** O último pedido ao usuário foi: executar `terraform apply` e compartilhar a saída, mas ainda não houve confirmação do resultado.

1. Confirmar a saída real de `terraform -version`, `terraform validate` e `terraform plan` (principalmente recursos e destruições).
2. Verificar se os alertas/controle de gastos foram ativados no Billing.
3. Confirmar se `terraform apply` já foi executado; se não, revisar permissões e o plano antes de aplicar.
4. Abrir Console S3 e inspecionar **Permissions**, **Properties** e **Tags**.
5. Atualizar status desta fase e registrar aprendizados no `LEARNINGS.md`.
6. Fazer commit dos arquivos de documentação (não versionar `terraform.tfstate` nem `terraform.tfvars`).
7. Só então avançar para a **Fase 2: dados fictícios + ingestão batch**.

## 9. Como manter os documentos úteis ao longo das conversas

Ao fim de cada interação de implementação:

- Atualizar checkboxes da fase pertinente e a data-base.
- Registrar novo recurso, motivo da escolha, alternativas consideradas, comandos, custo e resultado no Console.
- Anotar erros reais e resolução, sem expor credenciais.
- Atualizar o bloco **Próxima ação exata** para o verdadeiro ponto de retomada.
- Criar commit com mensagem objetiva (ex.: `docs: registrar aprendizado sobre seguranca S3`).

**Referência principal:** *AWS Certified Data Engineer Associate — The Complete Exam Revision Guide* (2026). Domínios e pesos citados acima são do guia enviado; verifique o exam guide oficial antes de agendar a prova, pois o conteúdo poderá mudar.
