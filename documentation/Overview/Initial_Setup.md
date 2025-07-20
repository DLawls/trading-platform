# Initial Setup Summary: Modular AI Trading Platform

## Current Environment
- **OS:** Windows 11
- **Development:** WSL2 (Ubuntu)
- **IDE:** Cursor (VSCode-based) with ChatGPT for planning
- **Version Control:** GitHub (SSH, repo: https://github.com/DLawls/trading-platform)
- **Docker:** Docker Desktop installed, configured for WSL2 backend
- **Project Location:** On WSL (ext4) filesystem for performance

## Repository Structure
- Using a **monorepo** for all microservices and modules
- Plan to organize code into subdirectories per service/module (e.g., `services/data_collector/`, `services/ai_engine/`)

## Development Tools & Practices
- **Python:** Poetry for dependency and environment management
- **C++ (if needed):** Conan for package management, pybind11 for Python bindings
- **Docker Compose:** For local development and orchestration
- **Multi-stage Dockerfiles:** For production builds
- **REST/gRPC:** For inter-service communication
- **Kafka/RabbitMQ/Redis:** For async data flows (as needed)
- **ML/MLOps:** Plan to use MLflow or Weights & Biases for experiment tracking, DVC for data/model versioning
- **Orchestration:** Airflow or Prefect for workflow scheduling
- **Monitoring:** Prometheus + Grafana for metrics, ELK/Loki for logs

## Recommendations
- **Keep all code and data on the WSL filesystem** (not Windows drives) for speed and reliability
- **Use VSCode Remote - WSL** (Cursor already supports this) for editing
- **Pin all dependency versions** (Poetry/Conan lock files)
- **Set up SSH keys** for GitHub access (already done)
- **Allocate sufficient resources to WSL2** (memory/CPU)
- **Use Docker Desktop with WSL2 backend**
- **Organize repo early**: Create subfolders for each planned module/service

## Next Steps
1. **Initialize Poetry** in the project root (and per service if needed)
2. **Create initial folder structure** for modules/services (start with `services/financial_data_collector/` for Module 1)
3. **Set up Docker Compose** with a basic service (e.g., a placeholder FastAPI app)
4. **Add a README** outlining the project structure and setup steps
5. **Configure .gitignore** for Python, Docker, and data artifacts
6. **Set up basic CI (optional)**: e.g., GitHub Actions for linting/tests
7. **Document environment setup** in `Docs/` for onboarding

## What I Need to Get Started
- Confirmation of the initial folder structure you want (e.g., `services/financial_data_collector/`)
- Preferred Python version (e.g., 3.10, 3.11)
- Any specific tech stack choices for Module 1 (e.g., FastAPI, Flask, data sources)
- Any team conventions or preferences (naming, code style, etc.)

---

Once you confirm or adjust the above, we can begin constructing Module 1: Financial Data Collector. 