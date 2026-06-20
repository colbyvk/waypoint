# Intentionally insecure Terraform -- Waypoint Trivy misconfig fixture. Do not deploy.
# Classic AWS IaC misconfigurations for Trivy's misconfig scanner to catch. No
# custom Semgrep rule targets this file; it exists purely as Trivy/checkov bait.

provider "aws" {
  region = "us-east-1"
}

# trivy plant: public S3 bucket via public-read ACL (AVD-AWS-0091 / S3 public ACL)
resource "aws_s3_bucket" "public_data" {
  bucket = "waypoint-public-data"
}

resource "aws_s3_bucket_acl" "public_data_acl" {
  bucket = aws_s3_bucket.public_data.id
  acl    = "public-read"
}

# trivy plant: S3 bucket with no server-side encryption configuration
# (AVD-AWS-0088 — bucket lacks SSE / no aws_s3_bucket_server_side_encryption_configuration)
resource "aws_s3_bucket" "unencrypted_data" {
  bucket = "waypoint-unencrypted-data"
}

# trivy plant: security group ingress open to 0.0.0.0/0 on port 22
# (AVD-AWS-0107 — SSH open to the internet)
resource "aws_security_group" "open_ssh" {
  name        = "open-ssh"
  description = "allows ssh from anywhere"

  ingress {
    description = "ssh from the world"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# trivy plant: unencrypted RDS instance (AVD-AWS-0080 — storage_encrypted not set / false)
resource "aws_db_instance" "analytics" {
  identifier           = "waypoint-analytics"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  username             = "admin"
  password             = "changeme123"
  storage_encrypted    = false
  publicly_accessible  = true
  skip_final_snapshot  = true
}
