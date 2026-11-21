
# Bucket principal do Data Lake.
resource "aws_s3_bucket" "data_lake" {
  bucket        = var.bucket_name
  force_destroy = false # Impede excluir o bucket enquanto houver objetos.
}

# Bloqueia todas as formas de acesso publico ao bucket.
resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Define criptografia automatica SSE-S3 para novos objetos.
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Desabilita ACLs e centraliza o controle de acesso em politicas.
resource "aws_s3_bucket_ownership_controls" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
