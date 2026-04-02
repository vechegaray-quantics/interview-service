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

variable "openai_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "openai_model" {
  type    = string
  default = "gpt-4o-mini"
}

variable "llm_max_followups_per_question" {
  type    = number
  default = 1
}

variable "llm_followup_temperature" {
  type    = number
  default = 0.2
}

variable "llm_followup_timeout_seconds" {
  type    = number
  default = 20
}

variable "container_image_tag" {
  type    = string
  default = "dev"
}