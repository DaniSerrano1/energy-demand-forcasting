# Energy Demand Forecasting - Setup Instructions

## Prerequisites
- Docker and Docker Compose installed
- At least 8GB of RAM available for Docker
- Ports 5432, 6379, 8080, and 8888 available

## Quick Start

1. **Clone the repository and navigate to the project directory**
   ```bash
   cd energy-demand-forcasting
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Create required directories**
   ```bash
   mkdir -p dags logs plugins data notebooks scripts
   ```

4. **Build and start all services**
   ```bash
   docker-compose up -d
   ```

5. **Wait for services to initialize** (first time may take 2-3 minutes)
   ```bash
   docker-compose logs -f airflow-init
   ```

6. **Access the services**
   - **Airflow Web UI**: http://localhost:8080
     - Username: `admin`
     - Password: `admin`
   
   - **Jupyter Lab**: http://localhost:8888
     - No password required (configured for development)
   
   - **PostgreSQL**: localhost:5432
     - Username: `airflow`
     - Password: `airflow`
     - Databases: `airflow` (Airflow metadata), `energy_data` (your data)

## Services Overview

### Airflow (Port 8080)
- Orchestrates ETL pipelines and scheduled jobs
- Components: Webserver, Scheduler, Worker, Redis, PostgreSQL
- DAGs are located in `./dags/` directory
- Logs are stored in `./logs/` directory

### Jupyter Lab (Port 8888)
- Interactive development environment for:
  - ETL development and testing
  - API calls and data extraction
  - Data transformation and normalization
  - Database operations and queries
- Notebooks are saved in `./notebooks/` directory
- Shared data in `./data/` directory

### PostgreSQL (Port 5432)
- Two databases:
  - `airflow`: Airflow metadata
  - `energy_data`: Your normalized energy data
- Schemas in `energy_data`:
  - `raw`: Raw API responses
  - `staging`: Intermediate processing
  - `production`: Clean, normalized data

## Database Schema

The `energy_data` database contains:

- `production.energy_demand`: Electricity demand data
- `production.weather_data`: Weather information
- `production.calendar_features`: Calendar and holiday data
- `production.forecasts`: Model predictions
- `production.anomalies`: Detected anomalies
- `raw.api_responses`: Raw API data

## Development Workflow

### Creating a new DAG

1. Create a Python file in `./dags/` directory
2. The DAG will automatically appear in Airflow UI
3. Example DAG is provided: `energy_demand_etl.py`

### Working with Jupyter

1. Open Jupyter Lab at http://localhost:8888
2. Create notebooks in the `work/` directory
3. Connect to PostgreSQL using:
   ```python
   import psycopg2
   
   conn = psycopg2.connect(
       host="postgres",
       database="energy_data",
       user="airflow",
       password="airflow"
   )
   ```

### Adding Python dependencies

- For Airflow: Edit `requirements-airflow.txt` and rebuild
- For Jupyter: Edit `requirements-jupyter.txt` and rebuild

```bash
docker-compose up -d --build
```

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f jupyter
```

### Restart services
```bash
docker-compose restart
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove all data
```bash
docker-compose down -v
```

### Access PostgreSQL CLI
```bash
docker exec -it energy_postgres psql -U airflow -d energy_data
```

### Access Jupyter container shell
```bash
docker exec -it energy_jupyter /bin/bash
```

### Rebuild after changes
```bash
docker-compose up -d --build
```

## Troubleshooting

### Airflow webserver not starting
- Check if port 8080 is available
- Wait 2-3 minutes for initialization
- Check logs: `docker-compose logs airflow-webserver`

### Database connection errors
- Ensure PostgreSQL is healthy: `docker-compose ps`
- Verify credentials in `.env` file
- Check database exists: `docker exec -it energy_postgres psql -U airflow -l`

### Out of memory errors
- Increase Docker memory allocation to at least 8GB
- Reduce number of Celery workers if needed

## Next Steps

1. Add your API keys to `.env` file
2. Customize the example DAG in `dags/energy_demand_etl.py`
3. Create Jupyter notebooks for data exploration
4. Build your forecasting models
5. Set up monitoring and alerting

## Project Structure
```
energy-demand-forcasting/
├── dags/                      # Airflow DAGs
├── notebooks/                 # Jupyter notebooks
├── plugins/                   # Airflow plugins
├── scripts/                   # Utility scripts
├── data/                      # Data files
├── logs/                      # Airflow logs
├── init-scripts/              # Database initialization
├── docker-compose.yml         # Docker orchestration
├── Dockerfile.airflow         # Airflow container
├── Dockerfile.jupyter         # Jupyter container
├── requirements-airflow.txt   # Airflow dependencies
├── requirements-jupyter.txt   # Jupyter dependencies
└── .env                       # Environment variables
```
