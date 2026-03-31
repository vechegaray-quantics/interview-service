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

variable "database_url_secret_id" {
  type = string
}

variable "database_url_secret_version" {
  type    = string
  default = "1"
}

variable "internal_service_token_secret_id" {
  type = string
}

variable "internal_service_token_secret_version" {
  type    = string
  default = "1"
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

variable "cors_allowed_origins" {
  type    = string
  default = "http://localhost:8000,http://127.0.0.1:8000,https://encuestas-interview.web.app,https://encuestas-interview.firebaseapp.com,https://encuestas-490902.web.app,https://encuestas-490902.firebaseapp.com"
}

variable "container_image_tag" {
  type    = string
  default = "dev"
}