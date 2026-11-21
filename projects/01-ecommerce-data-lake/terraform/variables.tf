
variable "aws_region" {
  description = "Regiao AWS utilizada no laboratorio"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Nome globalmente unico do bucket S3"
  type        = string

  # Exige que o nome do bucket seja informado pelo usuario.
}
