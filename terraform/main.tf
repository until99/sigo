terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = "ghm-data-dev"
  region  = "southamerica-east1"
}

provider "google-beta" {
  project = "ghm-data-dev"
  region  = "southamerica-east1"
}

# --- 1. Service Account e Identidades ---

resource "google_service_account" "composer_sa" {
  account_id   = "composer-env-sa"
  display_name = "Service Account para o Composer Environment"
}

# Identidade do Agente de Serviço do Composer
resource "google_project_service_identity" "composer_agent" {
  provider = google-beta
  project  = "ghm-data-dev"
  service  = "composer.googleapis.com"
}

# --- 2. Permissões IAM ---

# Permissão 1: O papel de Worker para sua Service Account
resource "google_project_iam_member" "composer_worker" {
  project = "ghm-data-dev"
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.composer_sa.email}"
}

# Permissão 2: Deixa o Agente do Composer "atuar como" sua Service Account
resource "google_service_account_iam_member" "composer_agent_auth" {
  provider           = google-beta
  service_account_id = google_service_account.composer_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_project_service_identity.composer_agent.email}"
}

# --- 3. Bucket de Armazenamento ---

resource "google_storage_bucket" "composer_bucket" {
  name                        = "ghm-data-dev-composer-bucket-001"
  location                    = "us-central1" # Deve ser a mesma região do Composer
  force_destroy               = true          # CUIDADO: Permite deletar bucket com arquivos
  uniform_bucket_level_access = true
}

# --- 4. O Ambiente Cloud Composer 3 ---

resource "google_composer_environment" "airflow_composer_3" {
  name    = "ghm-composer-env-3"
  region  = "us-central1"
  project = "ghm-data-dev"

  storage_config {
    bucket = google_storage_bucket.composer_bucket.name
  }

  config {
    software_config {
      image_version = "composer-3-airflow-2.10.2"
    }

    node_config {
      service_account = google_service_account.composer_sa.email
    }

    workloads_config {
      scheduler {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        count      = 1
      }
      web_server {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
      }
      worker {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        min_count  = 1
        max_count  = 3
      }
    }
  }

  # Dependências explícitas para evitar erros de ordem de criação
  depends_on = [
    google_project_iam_member.composer_worker,
    google_service_account_iam_member.composer_agent_auth,
    google_storage_bucket.composer_bucket
  ]
}