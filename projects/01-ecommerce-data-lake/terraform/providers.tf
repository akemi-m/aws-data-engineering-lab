
provider "aws" {
  region = var.aws_region

  # Tags padrao para identificar e acompanhar os recursos do laboratorio.
  default_tags {
    tags = {
      Project     = "dea-c01-ecommerce"
      Environment = "lab"
      ManagedBy   = "terraform"
    }
  }
}
