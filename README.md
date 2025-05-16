# 🚀 Apache Spark Cluster + Jupyterlab with Docker Compose

This repository contains a Docker Compose configuration for setting up a Spark Cluster with the following services:

- **Spark Master**
- **Spark Workers**
- **Spark History Server**
- **JupyterLab (for Accessing Spark Cluster via Notebooks)**

## 📦 Services Overview

The project includes several services, which are defined in the `docker-compose.yml` file:

- **spark-master**: Spark master node
- **spark-worker-1 & spark-worker-2**: Spark worker nodes
- **spark-history-server**: Spark history server to view Spark job logs
- **jupyterlab**: JupyterLab with PySpark setup for notebooks

Each service uses the `bitnami/spark:3.5.0` Docker image (except for JupyterLab)

| Service              | Hostname            | Ports                   | Description                          |
|----------------------|---------------------|--------------------------|--------------------------------------|
| `spark-master`       | `spark-master`      | 9190 (UI), 7077 (comm)   | Central Spark Master node            |
| `spark-worker-1`     | `spark-worker-1`    | 9191 (UI), 7001          | Spark worker node                    |
| `spark-worker-2`     | `spark-worker-2`    | 9192 (UI), 7002          | Spark worker node                    |
| `spark-history-server` | `spark-history-server` | 18080               | Spark application logs viewer        |
| `jupyterlab`         | `jupyterlab`        | 8888, 4040-4042          | JupyterLab with PySpark integration  |


## 🗂️ Folder Structure

```text
.
├── docker-compose.yml
├── Dockerfile
├── notebooks/             # Jupyter notebooks
└── spark/
    ├── apps/              # Spark applications
    ├── data/              # Input/output data
    ├── conf/              # Spark config (e.g., spark-defaults.conf)
    └── spark-events/      # Logs for history server
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/fajarafriad1/Spark-Cluster-in-Docker.git
cd Spark-Cluster-in-Docker
```

### 2. Build the Cluster
```bash
docker-compose up -d --build
```
Docker will:

1. **Build Docker images** for `spark-master`, `spark-worker-1`, `spark-worker-2`, `spark-history-server`, and `jupyterlab`.
2. **Start `spark-master`**: Expose UI on port `9190`, communication on `7077`, and mount volumes.
3. **Start workers (`spark-worker-1`, `spark-worker-2`)**: Connect to `spark-master`, expose UIs on ports `9191` and `9192`, configure resources.
4. **Start `spark-history-server`**: Expose UI on port `18080` for job logs.
5. **Start `jupyterlab`**: Integrate with Spark, expose UI on port `8888`, and Spark UI on ports `4040-4042`.
6. **Networking**: Containers on a shared bridge network with static IPs.
7. **Dependencies**: Workers and history server depend on `spark-master`; JupyterLab requires `spark-master` for jobs.

### 3. Test the Spark Cluster

#### 1. Test via CLI

```bash
docker exec -it spark-master bash

# Run a test job
spark-submit --class org.apache.spark.examples.SparkPi \
  --master spark://spark-master:7077 \
  examples/jars/spark-examples*.jar \
  10
```

#### 2. Test via Jupyterlab Notebook

```python
from pyspark.sql import SparkSession
# Connect to the Spark cluster master node
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("TestSparkFromJupyter") \
    .config("spark.executor.memory", "1g") \
    .config("spark.cores.max", "2") \
    .config("spark.driver.memory", "1g") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.eventLog.enabled", "true") \
    .config("spark.eventLog.dir", "file:///opt/bitnami/spark/spark-events") \
    .getOrCreate()

# Test cluster connection by creating a DataFrame and showing it
data = [("John", 30), ("Jane", 25), ("Mike", 35)]
columns = ["Name", "Age"]
df = spark.createDataFrame(data, columns)
df.show()
spark.stop()
```

Checkout the spark job events log via spark history server at http://localhost:18080/.


## ⚙️ Configuration Details

### Spark Master

- **Image:** `docker.io/bitnami/spark:3.5.0`
- **Ports:**
  - Web UI: `9190 → 8080`
  - RPC: `7077 → 7077`
- **Volumes:**
  ```yaml
  ./spark/apps:/opt/spark-apps
  ./spark/data:/opt/spark-data
  ./spark/spark-events:/opt/bitnami/spark/spark-events
  ./spark/conf/:/opt/bitnami/spark/conf/
  ```
- **Environment Variables:**

  ```yaml
  SPARK_MODE: master
  SPARK_LOCAL_IP: spark-master
  SPARK_RPC_AUTHENTICATION_ENABLED: "no"
  SPARK_RPC_ENCRYPTION_ENABLED: "no"
  SPARK_EVENTLOG_ENABLED: "true"
  ```
### Spark Workers

#### Common Settings (Worker 1 & Worker 2)

- **Image:** `docker.io/bitnami/spark:3.5.0`

- **Ports:**
  - **Worker 1:**
    - `9191 → 8080`
    - `7001 → 7000`
  - **Worker 2:**
    - `9192 → 8080`
    - `7002 → 7000`

- **Volumes:**
  ```yaml
  ./spark/apps:/opt/spark-apps
  ./spark/data:/opt/spark-data
  ./spark/spark-events:/opt/bitnami/spark/spark-events
  ./spark/conf/:/opt/bitnami/spark/conf/
  ```

- **Environment Variables:**
  ```yaml
  SPARK_MODE: worker
  SPARK_MASTER_URL: spark://spark-master:7077
  SPARK_WORKER_CORES: 1
  SPARK_WORKER_MEMORY: 1G
  SPARK_DRIVER_MEMORY: 1G
  SPARK_EXECUTOR_MEMORY: 1G
  SPARK_EVENTLOG_ENABLED: "true"
  SPARK_LOCAL_IP: spark-worker-[1|2]
  ```

### Spark History Server

- **Image:** `docker.io/bitnami/spark:3.5.0`

- **Command:**
  ```bash
  bin/spark-class org.apache.spark.deploy.history.HistoryServer
  ```
- **Ports:**

  - UI: `18080 → 18080`

- **Volumes:**
  ```yaml
  ./spark/data:/opt/bitnami/spark/custom_data
  ./spark/src:/opt/bitnami/spark/src
  ./spark/jars:/opt/bitnami/spark/connectors/jars
  ./spark/spark-events:/opt/bitnami/spark/spark-events
  ./spark/conf/:/opt/bitnami/spark/conf/
  ```

- **Environment Variables:**
  ```yaml
  SPARK_DAEMON_JAVA_OPTS: -Dspark.history.fs.logDirectory=/opt/bitnami/spark/spark-events
  ```

### JupyterLab

- **Image:** `jupyter/pyspark-notebook:latest`

- **Ports:**
  - **Notebook UI:** `8888 → 8888`
  - **Spark UIs:** `4040–4042 → 4040–4042`

- **Volumes:**
  ```yaml
  ./notebooks:/home/jovyan/work
  ./spark/spark-events:/opt/bitnami/spark/spark-events
  ```

- **Environment Variables:**
  ```yaml
  JUPYTER_ENABLE_LAB: "yes"
  SPARK_MASTER_URL: spark://spark-master:7077
  ```

- **Command:**
  ```yaml
  bash -c "umask 000 && start-notebook.sh --NotebookApp.token='' --NotebookApp.password"
  ```





