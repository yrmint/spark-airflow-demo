#!/bin/bash

airflow db migrate

echo "Creating admin user if not exists..."

if airflow users list | grep -q "admin"; then
  echo "User 'admin' already exists. Skipping creation."
else
  echo "Creating user 'admin'..."
  airflow users create \
      --username admin \
      --password admin \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com || true
fi

set -e

echo "Configuring Spark connection..."

airflow connections delete spark_default || true

airflow connections add spark_default \
    --conn-type spark \
    --conn-host spark-master \
    --conn-port 7077 \
    --conn-extra '{"deploy_mode": "client"}'

echo "Spark connection configured."

exec airflow standalone