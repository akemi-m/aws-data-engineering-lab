
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source = "hashicorp/aws"

      # Mantem o provider na versao 6, evitando mudancas de uma major version.
      version = ">= 6.23.0, < 7.0.0"
    }
  }
}
