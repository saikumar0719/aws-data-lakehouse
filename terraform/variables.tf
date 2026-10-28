variable "aws_region" {
  description = "AWS region for the lakehouse"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project prefix for bucket and resource names"
  type        = string
  default     = "aws-data-lakehouse"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}
