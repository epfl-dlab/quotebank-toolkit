import string
from utils import start_spark, is_date, URLs2domain
from argparse import ArgumentParser
import pyspark.sql.types as t
import pyspark.sql.functions as f
from nltk.tokenize.treebank import TreebankWordTokenizer
import configparser

parser = ArgumentParser()
parser.add_argument('-s', '--spark-config',
                    help='Path to the file with the configuration for Spark.', required=False, default='config.ini')
parser.add_argument('-i', '--input',
                    help='Path to Quotebank quotations.', required=True)
parser.add_argument('-o', '--output',
                    help='Path where clean Quotebank will be written.', required=True)
parser.add_argument('--input_format',
                    help='Format of the input data. (e.g., json, parquet)', required=True)
parser.add_argument('--output_format',
                    help='Format of the output data. (e.g., json, parquet)', required=True)
parser.add_argument('-d', '--disambiguation-mapping',
                    help='Path to the quoteID -> speaker QID mapping', required=True)
parser.add_argument('--self-quotations-filtered',
                    help='Path to the data containing quoteIDs of quotations that are not self-attribtued.', required=True)
parser.add_argument('-c', '--compression',
                    help='Compression algorithm used to compress the resulting data. If not specified, the data will not be compressed', required=False)
parser.add_argument('-b', '--blacklists',
                    help='Path to the folder containing name and domain blacklists. ', required=True)
parser.add_argument('-l', '--min-quotation-length',
                    help='Minimum quotation length in Penn Treebank tokens', required=False, default=5)

if __name__ == '__main__':
    args = parser.parse_args()
    spark_config = configparser.ConfigParser()
    spark_config.read(args.spark_config)
    spark = start_spark(spark_config)

    quotes_input = args.input
    quotes_output = args.output

    input_format = args.input_format
    output_format = args.output_format

    quotes = spark.read.format(input_format).load(quotes_input)

    self_quotations_filtered = spark.read.parquet(args.self_quotations_filtered)
    disambiguation_mapping = spark.read.parquet(args.disambiguation_mapping)

    # Removes quotes with no speaker attributed.
    quotes = quotes.where(f.col('speaker') != 'None')

    if 'domains' not in quotes.columns:
        # Adds the first level domain column.
        quotes = quotes.withColumn('domains', URLs2domain('urls'))

    blacklists = args.blacklists
    with open(blacklists + '/domain_blacklist.txt') as file:
        faulty_domains = {i.strip() for i in file}

    @f.udf(t.BooleanType())
    def all_faulty(domains):
        """
        Returns True if all the domains a quotation appears in are identified as faulty and False otherwise.
        :param domains: List of first-level domains.
        :return: True if all the domains are labelled faulty, False otherwise
        """
        return all([i in faulty_domains for i in domains])

    with open(blacklists + '/name_blacklist.txt') as file:
        faulty_names = {i.strip() for i in file}

    if int(args.min_quotation_length) > 0:
        tok = TreebankWordTokenizer()
        tok = spark.sparkContext.broadcast(tok)

        @f.udf(t.IntegerType())
        def n_tokens(quotation):
            """
            Counts the number of Penn Treebank tokens a quotation consists o.
            """
            quotation = quotation.lower()
            quotation = quotation.translate(str.maketrans('', '', string.punctuation))
            quotation = ' '.join(quotation.split())
            quotation = tok.value.tokenize(quotation)
            return len(quotation)

        # Removes all the quotations with less than min_quotation_length tokens.
        quotes = quotes.where(n_tokens('quotation') >= args.min_quotation_length)

    # Removes quotations that can be parsed as dates
    quotes = quotes.where(~is_date('quotation'))
    # Removes quotations that appear only in the domains labelled as faulty
    quotes = quotes.where(~all_faulty('domains'))
    # Removes all the quotations attributed to a speaker whose name is labelled as faulty
    quotes = quotes.where(~f.col('speaker').isin(faulty_names))

    # Removes the quotations identified as self quotations
    quotes = quotes.join(self_quotations_filtered, on='quoteID')
    # Maps each quotation to a Wikidata QID of its speaker
    quotes = quotes.select(*[i for i in quotes.columns if i != 'speaker']) \
        .join(disambiguation_mapping, on='quoteID')

    if args.compression is not None:
        quotes.write.format(output_format) \
            .mode('overwrite') \
            .option('compression', args.compression) \
            .save(quotes_output)
    else:
        quotes.write.format(output_format) \
            .mode('overwrite') \
            .save(quotes_output)