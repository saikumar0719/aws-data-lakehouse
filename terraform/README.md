# Terraform — AWS production path (code only, NOT applied)

This folder creates, if ever applied: versioned S3 buckets for raw,
curated, and gold data, an Athena results bucket, a Glue catalog
database, an Athena workgroup with its results in S3, a lifecycle
rule moving raw data to Standard-IA after 30 days, and a
least-privilege IAM pipeline role.

Do NOT run `terraform apply` unless you intend to create real AWS
resources and pay for them. The local pipeline in the repo root
needs no AWS at all.
