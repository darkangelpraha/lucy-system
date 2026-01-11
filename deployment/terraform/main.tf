# Lucy AI Assistant - GCP Infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "lucy-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev/staging/production)"
  type        = string
  default     = "production"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])
  
  service            = each.value
  disable_on_destroy = false
}

# Secret Manager - API Keys
resource "google_secret_manager_secret" "anthropic_api_key" {
  secret_id = "anthropic-api-key"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "mem0_api_key" {
  secret_id = "mem0-api-key"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "qdrant_host" {
  secret_id = "qdrant-host"
  
  replication {
    auto {}
  }
}

# Service Account for Lucy
resource "google_service_account" "lucy_sa" {
  account_id   = "lucy-assistant-sa"
  display_name = "Lucy AI Assistant Service Account"
  description  = "Service account for Lucy AI Assistant"
}

# IAM Bindings for Secret Access
resource "google_secret_manager_secret_iam_member" "lucy_secret_access" {
  for_each = toset([
    google_secret_manager_secret.anthropic_api_key.id,
    google_secret_manager_secret.openai_api_key.id,
    google_secret_manager_secret.mem0_api_key.id,
    google_secret_manager_secret.qdrant_host.id,
  ])
  
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.lucy_sa.email}"
}

# Cloud Storage bucket for Lucy data
resource "google_storage_bucket" "lucy_data" {
  name          = "${var.project_id}-lucy-data"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Cloud Storage bucket for Lucy logs
resource "google_storage_bucket" "lucy_logs" {
  name          = "${var.project_id}-lucy-logs"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# IAM for bucket access
resource "google_storage_bucket_iam_member" "lucy_data_access" {
  bucket = google_storage_bucket.lucy_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.lucy_sa.email}"
}

resource "google_storage_bucket_iam_member" "lucy_logs_access" {
  bucket = google_storage_bucket.lucy_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.lucy_sa.email}"
}

# Cloud Run Service - Orchestrator
resource "google_cloud_run_service" "lucy_orchestrator" {
  name     = "lucy-orchestrator"
  location = var.region
  
  template {
    spec {
      service_account_name = google_service_account.lucy_sa.email
      
      containers {
        image = "gcr.io/${var.project_id}/lucy-assistant:latest"
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
        }
        
        env {
          name  = "LUCY_ENV"
          value = var.environment
        }
        
        env {
          name  = "LUCY_MODE"
          value = "orchestrator"
        }
        
        env {
          name = "ANTHROPIC_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.anthropic_api_key.secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "OPENAI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.openai_api_key.secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "MEM0_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.mem0_api_key.secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name = "QDRANT_HOST"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.qdrant_host.secret_id
              key  = "latest"
            }
          }
        }
      }
      
      container_concurrency = 80
      timeout_seconds       = 300
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.required_apis]
}

# Allow public access to orchestrator
resource "google_cloud_run_service_iam_member" "orchestrator_public" {
  service  = google_cloud_run_service.lucy_orchestrator.name
  location = google_cloud_run_service.lucy_orchestrator.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "orchestrator_url" {
  description = "URL of Lucy Orchestrator"
  value       = google_cloud_run_service.lucy_orchestrator.status[0].url
}

output "service_account_email" {
  description = "Lucy service account email"
  value       = google_service_account.lucy_sa.email
}

output "lucy_data_bucket" {
  description = "Lucy data storage bucket"
  value       = google_storage_bucket.lucy_data.name
}

output "lucy_logs_bucket" {
  description = "Lucy logs storage bucket"
  value       = google_storage_bucket.lucy_logs.name
}
