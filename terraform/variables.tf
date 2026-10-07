variable "region" {
  type        = string
  description = "AWS region for the platform."
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment."
  default     = "dev"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name."
  default     = "ci-platform-dev"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR range."
  default     = "10.0.0.0/16"
}
