# Pet project "Data-pipeline"
Data pipeline for reading data from the exchange-rate API and loading it into the Postgres database using Airflow.
# Contents
[docker-compose.yml](https://github.com/TofuDriver/data-pipeline/blob/main/docker-compose.yml) - Airflow cluster with Local executor
  Contains:
    Apache Airflow 2.5.2
    PostgreSQL 13
[Dockerfile](https://github.com/TofuDriver/data-pipeline/blob/main/airflow/Dockerfile) - Airflow build file
[currency-data-scraper.py](https://github.com/TofuDriver/data-pipeline/blob/main/airflow/dags/currency-data-scraper.py) - DAG for read-load data.
# Start and stop
To run Airflow cluster on Docker, use the following command:
```
docker-compose up
```
To break down containers press Ctrl+C or Command+C and the following command:
```
docker-compose down
```
To run scheduler, use the following command:
```
docker exec -it <container_name> bash -c "airflow scheduler"
```
Airflow Webserver: localhost:8080
