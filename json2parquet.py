from argparse import ArgumentParser
from pyspark.sql.functions import date_format
from utils import parse_config, start_spark

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='Path to the config file. Default=config.ini', required=True, default='config.ini')
    args = parser.parse_args()

    config = parse_config(args.config)
    spark = start_spark(config)

    from_file = config['data']['quotes_json']
    to_file = config['data']['quotes_parquet']

    df = spark.read.json(from_file)
    columns = df.columns

    if 'date' in columns:
        all_but_date = [c for c in columns if c != 'date']
        df = df.select(*all_but_date,
                       date_format('date', 'yyyy-MM-dd').alias('date'),
                       date_format('date', 'yyyy').alias('year'),
                       date_format('date', 'MM').alias('month'))
        
        df.repartition('year', 'month').write.mode('overwrite').partitionBy('year', 'month').parquet(to_file)
    else:
        df.write.mode('overwrite').parquet(to_file)