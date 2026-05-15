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

exec airflow standalone