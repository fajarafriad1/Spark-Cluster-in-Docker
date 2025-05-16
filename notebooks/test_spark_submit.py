from pyspark.sql import SparkSession
# Connect to the Spark cluster master node
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("TestSparkFromJupyter") \
    .config("spark.executor.memory", "1g") \
    .config("spark.cores.max", "2") \
    .config("spark.driver.memory", "1g") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# Test cluster connection by creating a DataFrame and showing it
data = [("John", 30), ("Jane", 25), ("Mike", 35)]
columns = ["Name", "Age"]
df = spark.createDataFrame(data, columns)

df.show()

spark.stop()