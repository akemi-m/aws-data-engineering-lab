
# Nome do bucket criado no Amazon S3.
output "bucket_name" {
  value = aws_s3_bucket.data_lake.id
}

# ARN utilizado para referenciar o bucket em politicas IAM e integracoes.
output "bucket_arn" {
  value = aws_s3_bucket.data_lake.arn
}

output "aws_region" {
  value = var.aws_region
}
