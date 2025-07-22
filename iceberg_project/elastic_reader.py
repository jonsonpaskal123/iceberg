

from pyspark.sql import SparkSession, DataFrame

def read_from_elastic(spark: SparkSession, es_resource: str) -> DataFrame:
    """
    Reads data from a specified Elasticsearch resource.

    :param spark: The Spark session.
    :param es_resource: The Elasticsearch index to read from (e.g., 'app_logs').
    :return: A Spark DataFrame containing the data.
    """
    print(f"Reading data from Elasticsearch resource: {es_resource}...")
    df = spark.read.format("org.elasticsearch.spark.sql")         .option("es.nodes", "elasticsearch")         .option("es.port", "9200")         .option("es.resource", es_resource)         .load()
    print("Data read successfully.")
    df.show()
    return df

