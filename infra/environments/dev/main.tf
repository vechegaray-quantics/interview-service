resource "google_project_service" "artifactregistry" {
  project            = var.project_id
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "sqladmin" {
  project            = var.project_id
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam" {
  project            = var.project_id
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

resource "google_service_account" "interview_service" {
  project      = var.project_id
  account_id   = "interview-service-dev"
  display_name = "Interview Service Dev"

  depends_on = [
    google_project_service.iam,
  ]
}

resource "google_project_iam_member" "interview_service_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.interview_service.email}"
}

resource "google_project_iam_member" "interview_service_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.interview_service.email}"
}

resource "google_artifact_registry_repository" "interview_service" {
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Docker repository for interview-service"
  format        = "DOCKER"

  depends_on = [
    google_project_service.artifactregistry,
  ]
}

resource "google_cloud_run_v2_service" "interview_service" {
  name                 = var.service_name
  location             = var.region
  project              = var.project_id
  ingress              = "INGRESS_TRAFFIC_ALL"
  invoker_iam_disabled = true

  template {
    service_account = google_service_account.interview_service.email
    timeout         = "300s"

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }

    volumes {
      name = "cloudsql"

      cloud_sql_instance {
        instances = [var.cloud_sql_instance_connection_name]
      }
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}/interview-service:${var.container_image_tag}"

      ports {
        container_port = 8080
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      env {
        name  = "APP_ENV"
        value = "dev"
      }

      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }

      env {
        name  = "INTERNAL_SERVICE_TOKEN"
        value = var.internal_service_token
      }

      env {
        name  = "CAMPAIGN_SERVICE_BASE_URL"
        value = var.campaign_service_base_url
      }

      env {
        name  = "INVITATION_SERVICE_BASE_URL"
        value = var.invitation_service_base_url
      }

      env {
        name  = "OPENAI_MODEL"
        value = var.openai_model
      }
      env {
        name  = "CORS_ALLOWED_ORIGINS"
        value = "http://localhost:8000,http://127.0.0.1:8000,https://encuestas-interview.web.app,https://encuestas-interview.firebaseapp.com,https://encuestas-490902.web.app,https://encuestas-490902.firebaseapp.com"
      }
    }
  }

  depends_on = [
    google_project_service.run,
    google_project_service.secretmanager,
    google_project_service.sqladmin,
    google_project_iam_member.interview_service_cloudsql_client,
    google_project_iam_member.interview_service_secret_accessor,
    google_artifact_registry_repository.interview_service,
  ]
}

output "interview_service_url" {
  value = google_cloud_run_v2_service.interview_service.uri
}