
# Prefixos que representam as camadas e entidades do Data Lake.
locals {
  s3_prefixes = [
    "raw/clientes/",
    "raw/produtos/",
    "raw/pedidos/",
    "raw/pagamentos/",
    "trusted/clientes/",
    "trusted/produtos/",
    "trusted/pedidos/",
    "trusted/pagamentos/",
    "delivery/vendas_diarias/",
    "delivery/vendas_por_categoria/"
  ]
}

# Cria objetos vazios que representam pastas no Console do S3.
resource "aws_s3_object" "data_lake_folders" {
  for_each = toset(local.s3_prefixes)

  bucket  = aws_s3_bucket.data_lake.id
  key     = each.value
  content = ""
}
