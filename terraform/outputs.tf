output "raw_bucket" {
  value = aws_s3_bucket.raw.bucket
}

output "curated_bucket" {
  value = aws_s3_bucket.curated.bucket
}

output "gold_bucket" {
  value = aws_s3_bucket.gold.bucket
}

output "glue_database" {
  value = aws_glue_catalog_database.lakehouse.name
}

output "athena_workgroup" {
  value = aws_athena_workgroup.lakehouse.name
}
