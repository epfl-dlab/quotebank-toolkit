from argparse import ArgumentParser
from pyspark.sql.functions import date_format
from utils import parse_config, start_spark

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-s', '--spark-config', help='Path to the file with the configuration for Spark.', default='config.ini')
    parser.add_argument('-j', '--json', help='Path to the file with Quotebank data in JSON format.')
    parser.add_argument('-p', '--parquet', help='Path where Quotebank will be saved in Parquet format.')

    args = parser.parse_args()

    json_path = args.json
    parquet_path = args.parquet
    config = parse_config(args.spark_config)
    spark = start_spark(config)

    df = spark.read.json(json_path)
    columns = df.columns

    if 'date' in columns:
        all_but_date = [c for c in columns if c != 'date']
        df = df.select(*all_but_date,
                       date_format('date', 'yyyy-MM-dd').alias('date'),
                       date_format('date', 'yyyy').alias('year'),
                       date_format('date', 'MM').alias('month'))
        
        df.repartition('year', 'month').write.mode('overwrite').partitionBy('year', 'month').parquet(parquet_path)
    else:
        df.write.mode('overwrite').parquet(parquet_path)