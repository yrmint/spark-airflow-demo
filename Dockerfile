FROM apache/spark:4.1.1-python3 AS spark

FROM apache/airflow:2.10.2-python3.10

# install Spark client + JDBC driver ClickHouse
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install Spark
COPY --from=spark /opt/spark /opt/spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# JDBC driver ClickHouse
RUN mkdir -p $SPARK_HOME/jars \
    && curl -sL https://repo1.maven.org/maven2/com/clickhouse/clickhouse-jdbc/0.7.2/clickhouse-jdbc-0.7.2-all.jar \
       -o $SPARK_HOME/jars/clickhouse-jdbc.jar

# Python requirements
ENV AIRFLOW_HOME=/opt/airflow
ENV PATH=/home/airflow/.local/bin:$PATH
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt

USER airflow