from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pyspark import StorageLevel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

spark = SparkSession.builder \
    .appName("LinearRegression_ClickHouse_Demo") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.instances", "3") \
    .config("spark.executor.cores", "1") \
    .config("spark.executor.memory", "1g") \
    .getOrCreate()

logger.info("Spark Session started with 3 executors")

df = (
    spark.read
    .format("jdbc")
    .option(
        "url",
        "jdbc:clickhouse://clickhouse:8123/default"
    )
    .option(
        "driver",
        "com.clickhouse.jdbc.ClickHouseDriver"
    )
    .option("user", "user")
    .option("password", "password")
    .option("dbtable", "demo_data")

    .option("partitionColumn", "id")
    .option("lowerBound", "1")
    .option("upperBound", "1000000")
    .option("numPartitions", "12")

    .load()
)

logger.info(
    f"Partitions after JDBC read: {df.rdd.getNumPartitions()}"
)

df = df.repartition(12)

logger.info(
    f"Partitions after repartition: {df.rdd.getNumPartitions()}"
)

assembler = VectorAssembler(
    inputCols=["x1", "x2"],
    outputCol="features"
)

data = assembler.transform(df).select("features", "y")

data.persist(StorageLevel.MEMORY_AND_DISK)

logger.info(f"Rows loaded: {data.count()}")

lr = LinearRegression(
    featuresCol="features",
    labelCol="y",
    maxIter=50
)

model = lr.fit(data)

coefficients = model.coefficients
intercept = model.intercept

logger.info(
    f"Coefficients: x1={coefficients[0]:.4f}, "
    f"x2={coefficients[1]:.4f}"
)

logger.info(
    f"Intercept={intercept:.4f}"
)

result_df = spark.createDataFrame(
    [(
        float(coefficients[0]),
        float(coefficients[1]),
        float(intercept),
        "v1"
    )],
    [
        "coef_x1",
        "coef_x2",
        "intercept",
        "model_version"
    ]
)

(
    result_df.write
    .format("jdbc")
    .option(
        "url",
        "jdbc:clickhouse://clickhouse:8123/default"
    )
    .option(
        "driver",
        "com.clickhouse.jdbc.ClickHouseDriver"
    )
    .option("user", "user")
    .option("password", "password")
    .option("dbtable", "model_coefficients")
    .mode("append")
    .save()
)

spark.stop()
