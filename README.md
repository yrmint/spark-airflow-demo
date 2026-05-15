# Airflow + Spark + ClickHouse Demo

A simple demonstration project showing integration between **Apache Airflow**, **Apache Spark** (standalone cluster) and **ClickHouse**.

## Features

- Airflow DAG with 2 tasks:
  1. Spark job: Linear Regression on data from ClickHouse
  2. Task with random failures and retries (demonstrates retry mechanism)
- Spark cluster with 1 Master + 3 Workers
- Data reading from ClickHouse -> ML model training -> writing coefficients back to ClickHouse
- Fully containerized with Docker Compose

## Architecture

- **Airflow** (standalone mode) — orchestration
- **Spark** (standalone) — distributed processing (3 nodes)
- **ClickHouse** — data storage and source for ML

## Prerequisites

- Docker Engine
- Docker Compose v2
- At least 6–8 GB RAM recommended


## How to Install

### 1. Clone / Prepare project

```bash
git clone git@github.com:yrmint/spark-airflow-demo.git
cd spark-airflow-demo
```

### 2. Start all services
```bash
docker-compose up -d --build
```
First build may take some time (especially downloading Spark and building Airflow image).

### 3. Check that everything is running
```bash
docker-compose ps
```
You should see 6 containers:
- airflow
- clickhouse
- spark-master
- spark-worker-1
- spark-worker-2
- spark-worker-3

### 4. Setup Airflow connection

1. Access Airflow UI at http://localhost:8081
    - username: `admin`
    - password: `admin`
2. Go to Admin - Connections
3. Edit spark_default record:
    - `Connection Id`: `spark_default`
    - `Connection Type`: `Spark`
    - `Host`: `spark-master`
    - `Port`: `7077`
    - `Deploy mode`: `client`


## How to run
1. Open Airflow UI at http://localhost:8081
2. Find DAG spark_ml_clickhouse_demo
3. Enable the DAG (toggle on)
4. Click Trigger DAG
5. Monitor execution

You can:

- Kill one Spark worker during execution to test fault tolerance:
  ```bash
    docker stop spark-worker-1
  ```
- Check logs in Airflow and Spark UI
- Verify results in ClickHouse:
  ```sql
    SELECT * FROM model_coefficients ORDER BY created_at DESC;
  ```
  
## Useful commands
```bash
# View logs
docker logs airflow
docker logs spark-master
docker logs spark-worker-1

# Enter containers
docker exec -it airflow bash
docker exec -it clickhouse clickhouse-client

# Restart specific service
docker-compose restart airflow
```

## Stopping the project
```bash
docker-compose down
```
To also remove volumes (reset data):
```bash
docker-compose down -v
```