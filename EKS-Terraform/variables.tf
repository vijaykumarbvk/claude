variable "aws_region" {
  description = "AWS region for every resource"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "venus-hospital"
}

variable "cluster_version" {
  description = "Kubernetes control-plane version"
  type        = string
  default     = "1.31"
}

variable "node_instance_type" {
  description = "Worker node size. 5 Flask services + Streamlit + Kafka + EFK needs headroom."
  type        = string
  default     = "t3.large"
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "RDS master password. Pass via TF_VAR_db_password, never commit it."
  type        = string
  sensitive   = true
}

variable "project_tags" {
  type = map(string)
  default = {
    Project     = "venus-hospital"
    Environment = "dev"
    Owner       = "vijay"
    ManagedBy   = "terraform"
  }
}
