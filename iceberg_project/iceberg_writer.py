
from pyspark.sql import DataFrame

def create_iceberg_table(spark, table_name: str, schema: str, partition_by: str):
    """
    Creates an Iceberg table if it doesn't exist.

    :param spark: The Spark session.
    :param table_name: The full name of the table (e.g., 'nessie.logs').
    :param schema: The table schema definition.
    :param partition_by: The column to partition the table by.
    """
    print(f"Creating Iceberg table '{table_name}' if it does not exist...")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
          {schema}
        )
        PARTITIONED BY ({partition_by})
    """)
    print(f"Table '{table_name}' is ready.")

def write_to_iceberg(df: DataFrame, table_name: str):
    """
    Writes a DataFrame to a specified Iceberg table.

    :param df: The DataFrame to write.
    :param table_name: The full name of the Iceberg table.
    """
    print(f"Writing data to Iceberg table: {table_name}...")
    df.write.format("iceberg").mode("append").save(table_name)
    print("Data written successfully.")

def verify_iceberg_data(spark, table_name: str):
    """
    Reads and displays data from an Iceberg table for verification.

    :param spark: The Spark session.
    :param table_name: The full name of the table to verify.
    """
    print(f"Verifying data in Iceberg table: {table_name}")
    iceberg_df = spark.table(table_name)
    iceberg_df.show()
