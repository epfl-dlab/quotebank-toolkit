# quotebank-toolkit
This repository contains utility scripts for preprocessing [Quotebank](https://zenodo.org/record/4277311) [1]. Currently, two scripts are available:
- [`json2parquet.py`](#json2parquetpy) - converts Quotebank data stored in JSON format to parquet format. Parquet files are faster to load, making data exploration significantly more convenient. For details about the Parquet format, see [the official documentation](https://parquet.apache.org/docs/).
- [`cleanup_disambiguate.py`](#cleanup_disambiguatepy) - performs basic cleanup of the quotation-centric Quotebank data and assigns a Wikidata QID to the respective speaker of each quotation. In other words, the script links each attributed speaker to its corresponding Wikidata item, making Wikidata's rich knowledge usable for further analyses. To be more specific, `cleanup_disambiguate.py` performs the following preprocessing steps:
	- removal of the quotes that meet the following conditions:
		- attributed to no speaker
		- that can be parsed as a date
		- where the speaker name is identified as spurious (see [data/blacklists/name_blacklist.txt](https://github.com/epfl-dlab/quotebank-toolkit/blob/main/data/blacklists/name_blacklist.txt))
		- that appear only on domains identified as faulty (see [data/blacklists/domain_blacklist.txt](https://github.com/epfl-dlab/quotebank-toolkit/blob/main/data/blacklists/domain_blacklist.txt))
		- mentioning the speaker to which they are attributed (self-quotations) by joining Quotebank with `self_quotations_filtered`
	- speaker disambiguation by joining Quotebank with `data/quotebank_disambiguation_mapping`. Due to the size of the dataset, speaker disambiguation mapping has been obtained using lightweight heuristics [2].

## Usage instructions
1. Clone this repository by running
```
git clone https://www.github.com/epfl-dlab/quotebank-toolkit
```
or, if you have an ssh key set up with GitHub, by running
```
git clone git@github.com:epfl-dlab/quotebank-toolkit
```
2. Position yourself inside the repository by running
```
cd quotebank-toolkit
```
3. Download the quotation-centric Quotebank from [Zenodo](https://zenodo.org/record/4277311) into `data/quotes`. You only need to download the files whose name follows the format `quotes-YYYY.json.bz2`. 
4. Download the data required to run the scripts. The data is available on [drive](https://drive.google.com/file/d/1svi0ILAL9JIZ9llncSOlTqfZTYbpCLe0/view?usp=sharing).
5. Unzip the data into `data`.
6. You can run the scripts in a Conda environment or a Docker container. If you want to run the scripts in a Conda environment, please see [Conda environment instructions](#conda-environment-instructions). Otherwise, see [Docker container instructions](#docker-container-instructions).
7. For the details about the scripts and their respective arguments, please see [Script-specific instructions](#script-specific-instructions).

### Conda environment instructions
1. Install [Anaconda](https://www.anaconda.com/products/distribution#download-section) (64-bit Python 3.9 version)
2. Setup the virtual environment named `quotebank-toolkit` to install all the required dependencies by running the command

```
conda env create -f quotebank_toolkit.yml
```
4. Activate the installed environment
```
conda activate quotebank-toolkit
```

### Docker container instructions 
1. Install [Docker](https://docs.docker.com/get-docker/).
2. Pull the `maculjak/quotebank-toolkit` Docker image  from DockerHub by running
```
docker pull maculjak/quotebank-toolkit
```
3. Run the Docker container by using
```
docker run -it -v $(pwd):/quotebank-toolkit maculjak/quotebank-toolkit
```
This command will run the container and start a new `bash` shell inside it with all the dependencies installed. The folder `quotebank-toolkit` will be created inside the container and bind it with the current working directory. This will make the scripts and data accessible from the container.
4. Position yourself inside the `quotebank-toolkit` directory by running
```
cd quotebank-toolkit
```

### Script-specific instructions
#### `json2parquet.py`
To run this script, run the following command:

```
python json2parquet.py \
        --spark-config SPARK_CONFIG \
        --json JSON_DATA \
        --parquet PARQUET_DATA
```
- `SPARK_CONFIG` - Path to the file configuring a Spark session. For details about configuring Spark sessions, please see [the official documentation](https://spark.apache.org/docs/latest/configuration.html#application-properties). This should provide you with enough information to configure the Spark sessions according to your needs. You can add options to the config file according to the [Application properties table](https://spark.apache.org/docs/latest/configuration.html#application-properties) in the documentation. The only option in the provided config file not mentioned in the official documentation is `num_threads`, whose name is self-explanatory. It merely sets the maximum number of processor threads usable by the script.
- `JSON_DATA` - Path to the file with Quotebank data in JSON format.
- `PARQUET_DATA` - Path where Quotebank will be saved in Parquet format. 

For example:
```
python json2parquet.py \
        --spark-config config.ini \
        --json data/quotes \
        --parquet data/quotes.parquet
```
This command will use Spark configuration specified in `config.ini`, read the quotes stored in `data/quotes`, and write the resulting data in Parquet format to `data/quotes_parquet`

#### `cleanup_disambiguate.py`
To run this script, run the following command:
```
python cleanup_disambiguate.py \
	--spark-config SPARK_CONFIG \
	--input INPUT \
	--output OUTPUT \
	--input_format INPUT_FORMAT \
	--output_format OUTPUT_FORMAT \
	--disambiguation-mapping DISAMBIGUATION_MAPPING \
	--self-quotations-filtered SELF_QUOTATIONS_FILTERED \
	--blacklists BLACKLISTS \
	--compression COMPRESSION \
	--min-quotation-length MIN_QUOTATION_LENGTHS
```
- `SPARK_CONFIG` - Path to the file with the configuration for a Spark session. For details, please see the instructions for `json2parquet.py` .  
- `INPUT` - Path to the original quotation-centric Quotebank data.
- `OUTPUT` - Path where clean quotation-centric Quotebank data will be written.
- `INPUT_FORMAT` - Format of the input data. (e.g., `json`, `parquet`, etc.)
- `OUTPUT_FORMAT` - Format of the output data. (e.g., `json`, `parquet` etc.)
- `DISAMBIGUATION_MAPPING` - Path to the `quoteID` $\rightarrow$ `speakerQID` mapping.
- `SELF_QUOTATIONS_FILTERED` - Path to the data containing quoteIDs of quotations that are not self-attributed. Self-attributed quotations are mostly falsely attributed and should be removed.
- `BLACKLISTS` - Path to the folder containing name and domain blacklists used for filtering quotations appearing only on spurious domains or attributed to speakers with spurious names.
- `COMPRESSION` - Compression algorithm (e.g., `bz2`, `gzip`, etc.) used to compress the resulting data. If not specified, the data will not be compressed.
- `MIN_QUOTATION_LENGTH` - Minimum quotation length in Penn Treebank tokens. Extremely short quotations are usually noise and should be removed. The recommended value for this argument is `5`. Since tokenization is the most computationally expensive operation performed by this script, not removing short quotations by setting this argument to `0` will drastically speed up the runtime.

For example:
```
python cleanup_disambiguate.py \
	--spark-config config.ini \
	--input data/quotes.parquet \
	--output data/quotes_clean_parquet.parquet \
	--input_format parquet \
	--output_format parquet \
	--disambiguation-mapping data/quotebank_disambiguation.parquet \
	--self-quotations-filtered data/self_quotations_filtered.parquet \
	--blacklists data/blacklists \
	--min-quotation-length 5
```
This command will use the Spark session configuration specified in `config.ini`, read the quotes stored in Parquet format in `data/quotes_parquet`, and write the resulting data in Parquet format to `data/quotes_clean_parquet`. For speaker disambiguation and self-quotation removal, the data from `data/quotebank_disambiguation_mapping_quote` and `data/self_quotations_filtered.parquet` will be used, respectively. The blacklists will be loaded from `data/blacklists`, while all the quotations with less than 5 Penn Treebank tokens will be removed. The resulting dataset will not be compressed as nothing was passed to the `compression` argument. Note that the proposed preprocessing steps can only clean up Quotenank partially, and a portion of faulty and falsely attributed quotations will remain in the dataset.

## References
[1] Timoté Vaucher, Andreas Spitz, Michele Catasta, and Robert West. “Quotebank: A Corpus of Quotations from a Decade of News”. In Proceedings of the 14th ACM International Conference on Web Search and Data Mining. 2021.

[2] Marko Čuljak, Andreas Spitz, Robert West, Akhil Arora. “Strong Heuristics for Named Entity Linking”. In Proceedings 2022 Conference of the North American Chapter of the Association for Computational Linguistics: Student Research Workshop.

