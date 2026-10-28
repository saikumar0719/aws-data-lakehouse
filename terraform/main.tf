# AWS data lakehouse infrastructure — code only, NOT applied.
# Applying this creates real AWS resources and may incur charges.
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  prefix = "${var.project}-${var.environment}"
}

resource "aws_s3_bucket" "raw" {
  bucket = "${local.prefix}-raw"
}

resource "aws_s3_bucket" "curated" {
  bucket = "${local.prefix}-curated"
}

resource "aws_s3_bucket" "gold" {
  bucket = "${local.prefix}-gold"
}

resource "aws_s3_bucket" "athena_results" {
  bucket = "${local.prefix}-athena-results"
}

resource "aws_s3_bucket_versioning" "raw" {
  bucket = aws_s3_bucket.raw.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_versioning" "curated" {
  bucket = aws_s3_bucket.curated.id
  versioning_configuration { status = "Enabled" }
}

# Cost control: raw data moves to Standard-IA after 30 days.
resource "aws_s3_bucket_lifecycle_configuration" "raw" {
  bucket = aws_s3_bucket.raw.id
  rule {
    id     = "to-standard-ia"
    status = "Enabled"
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_glue_catalog_database" "lakehouse" {
  name = replace(local.prefix, "-", "_")
}

resource "aws_athena_workgroup" "lakehouse" {
  name = "${local.prefix}-workgroup"
  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/results/"
    }
    enforce_workgroup_configuration = true
  }
}

# Least-privilege role: read raw, write curated/gold, nothing else.
resource "aws_iam_role" "pipeline" {
  name = "${local.prefix}-pipeline-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "glue.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}
