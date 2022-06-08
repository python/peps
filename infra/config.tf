terraform {
  required_providers {
    fastly = {
      source  = "fastly/fastly"
      version = "1.1.2"
    }
  }
  required_version = ">= 1.1.8"
  cloud {
    organization = "psf"
    workspaces {
      name = "peps"
    }
  }
}
variable "fastly_token" {
  type      = string
  sensitive = true
}
provider "fastly" {
  api_key = var.fastly_token
}
