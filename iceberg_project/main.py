
from config import get_spark_session
from elastic_reader import read_from_elastic
from iceberg_writer import create_iceberg_table, write_to_iceberg, verify_iceberg_data

def main():
    """
    Main ETL pipeline to move data from Elasticsearch to Iceberg.
    """
    spark = None
    try:
        # 1. Get Spark Session
        spark = get_spark_session()
        print("Spark session created successfully.")

        # 2. Read data from Elasticsearch
        elastic_df = read_from_elastic(spark, "app_logs")

        # 3. Define Iceberg table properties
        table_name = "nessie.logs"
        schema = "ts TIMESTAMP, level STRING, message STRING"
        partition_by = "level"

        # 4. Create Iceberg table
        create_iceberg_table(spark, table_name, schema, partition_by)

        # 5. Write data to Iceberg
        write_to_iceberg(elastic_df, table_name)

        # 6. Verify the data
        verify_iceberg_data(spark, table_name)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if spark:
            print("Stopping Spark session.")
            spark.stop()

if __name__ == "__main__":
    main()
