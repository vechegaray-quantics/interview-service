variable "project_id" {
  type    = string
  default = "encuestas-490902"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "service_name" {
  type    = string
  default = "interview-service"
}

variable "artifact_registry_repository" {
  type    = string
  default = "interview-service"
}

variable "cloud_sql_instance_connection_name" {
  type    = string
  default = "encuestas-490902:us-central1:campaign-service-dev-db"
}

variable "database_url" {
  type      = string
  sensitive = true
}

variable "internal_service_token" {
  type      = string
  sensitive = true
}

variable "campaign_service_base_url" {
  type = string
}

variable "invitation_service_base_url" {
  type = string
}

variable "openai_model" {
  type    = string
  default = "gpt-5-mini"
}

variable "container_image_tag" {
  type    = string
  default = "dev"
}