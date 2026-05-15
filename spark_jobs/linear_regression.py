from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
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

# read data from clickhouse
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:clickhouse://clickhouse:8123/default") \
    .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
    .option("user", "user") \
    .option("password", "password") \
    .option("query", "SELECT x1, x2, y FROM demo_data") \
    .load()

logger.info(f"Lines loaded: {df.count()}")

# prepare data
assembler = VectorAssembler(inputCols=["x1", "x2"], outputCol="features")
data = assembler.transform(df)

# train model
lr = LinearRegression(featuresCol="features", labelCol="y", maxIter=10)
model = lr.fit(data)

coefficients = model.coefficients
intercept = model.intercept

logger.info(f"Coefficients: x1 = {coefficients[0]:.4f}, x2 = {coefficients[1]:.4f}")
logger.info(f"Intercept = {intercept:.4f}")

# save result ClickHouse
result_df = spark.createDataFrame([(
    float(coefficients[0]),
    float(coefficients[1]),
    float(intercept),
    "v1"
)], ["coef_x1", "coef_x2", "intercept", "model_version"])

result_df.write \
    .format("jdbc") \
    .option("url", "jdbc:clickhouse://clickhouse:8123/default") \
    .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
    .option("user", "user") \
    .option("password", "password") \
    .option("dbtable", "model_coefficients") \
    .mode("append") \
    .save()

logger.info("Coefficients saved to ClickHouse")

spark.stop()
