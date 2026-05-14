FROM apache/airflow:2.10.2

# install Spark client + JDBC driver ClickHouse
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install Spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

RUN curl -sL https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz -o spark.tgz \
    && mkdir -p $SPARK_HOME \
    && tar -xzf spark.tgz -C $SPARK_HOME --strip-components=1 \
    && rm spark.tgz

# JDBC driver ClickHouse
RUN mkdir -p $SPARK_HOME/jars \
    && curl -sL https://repo1.maven.org/maven2/com/clickhouse/clickhouse-jdbc/0.7.2/clickhouse-jdbc-0.7.2-all.jar \
       -o $SPARK_HOME/jars/clickhouse-jdbc.jar

# Python requirements
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
