from dateutil.parser import parse as parseDate
import pyspark.sql.functions as f
import pyspark.sql.types as t
from pyspark.sql import SparkSession
from tld import get_tld
import configparser

@f.udf(t.BooleanType())
def is_date(string: str) -> bool:
    """
    Returns true if the input string can be parsed to a date. Works for filtering non-date quotations.
    With help from: https://stackoverflow.com/questions/25341945/check-if-string-has-date-any-format
    :param string: Arbitrary input string
    :return: Boolean indicator for "is string a date?"
    """

    try:
        parseDate(string, fuzzy=False, ignoretz=True)
        return True
    except Exception as exe:
        if not isinstance(exe, ValueError):
            if isinstance(exe, TypeError):
                pass  # Internal error of dateparser when handling the Value Error. So a type error is most likely actually a value error
            else:
                print('Caught unexpected Error', exe)
                print(exe)
        return False


def start_spark(config):
    """
    Configures a Spark session from a .ini file.
    :param cfg_file_path: Path to .ini file containing Spark session configuration.
    :return: SparkSession object
    """
    n_threads = config['spark']['n_threads']
    app_name = config['spark']['appName']

    spark = (SparkSession.builder.master(f'local[{n_threads}]')
             .appName(app_name))

    del config['spark']['n_threads']
    del config['spark']['appName']
    cfg_list = list(config['spark'].items())

    for k, v in cfg_list:
        spark = spark.config(k, v)

    return spark.getOrCreate()


def __URL2domain(url):
    """
    Trims a URL and leaves only the root domain.
    :param url: URL string.
    :return: Domain extracted from the URL string.
    """

    ret = get_tld(url, as_object=True)
    return ret.domain + '.' + ret.tld


@f.udf(t.ArrayType(t.StringType()))
def URLs2domain(urls):
    """
    Trims a list of URLs and leaves only the root domains.
    :param urls: List of URL strings.
    :return: List of domains extracted from the URL strings.
    """
    return [__URL2domain(url) for url in urls]

def parse_config(config_path):
    """
    Parses the config file specified by its location.
    :param config_path: Location of the config file to be parsed.
    :return: Parsed config file.
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config