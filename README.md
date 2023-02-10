# quotoolbox
This repository contains scripts utility for preprocessing Quotebank. Currently, two scripts are available:
- `json2parquet.py` - converts Quotebank data stored in JSON format to parquet format. Parquet files are faster to load, making data exploration significantly more convenient. For details about the Parquet format, see [the official documentation](https://parquet.apache.org/docs/).
- `cleanup_disambiguate.py` - performs basic cleanup of the quotation-level Quotebank data and assigns Wikidata QID to the respective speaker of each quotation. In other words, the script links each attributed speaker to its corresponding Wikidata item,  making Wikidata's rich knowledge usable for analyses.
 
## Usage instructions
1. Clone this repository by running
```
git clone https://www.github.com/epfl-dlab/quotoolbox
```
or, if you have an ssh key set up with GitHub, running
```
git clone git@github.com:epfl-dlab/quotoolbox
```
2. Position yourself inside the repository by running
```
cd quotoolbox
```
3. Download the quotation-level Quotebank from [Zenodo](https://zenodo.org/record/4277311) into `data/quotes`. You only need to download the files whose name follows the format `quotes-YYYY.json.bz2`. 
4. Download the data required to run the scripts. The data is available on [drive](https://drive.google.com/file/d/1svi0ILAL9JIZ9llncSOlTqfZTYbpCLe0/view?usp=sharing).
5. Unzip the data into `quotoolbox/data`.
6. You can run the scripts in a Conda environment or a Docker container. If you want to run the scripts in a Conda environment, please see [Conda environment instructions](#conda-environment-instructions). Otherwise, see [Docker container instructions](#docker-container-instructions).
7. For the details about the scripts and their respective arguments, please see [Script-specific instructions](#script-specific-instructions).

### Conda environment instructions
1. Install [Anaconda](https://www.anaconda.com/products/distribution#download-section) (64-bit Python 3.9 version)
2. Setup the virtual environment named `quotoolbox` to install all the required dependencies by running the command
```
conda env create -f quotoolbox.yml
```
4. Activate the installed environment
```
conda activate el
```

### Docker container instructions 
1. Install [Docker](https://docs.docker.com/get-docker/)
2. Pull the Quotoolbox Docker image `maculjak/quotoolbox` from DockerHub by running
```
docker pull maculjak/quotoolbox
```
3. Run the Quotoolbox Docker container by running
```
docker run -it -v $(pwd):/quotoolbox maculjak/quotoolbox
```
This command will run the container and start a new `bash` shell inside it with all the dependencies installed. The folder `quotoolbox` will be created inside the container and bind it with the current working directory. This will make the scripts and data accessible from the container.
4. Position yourself inside the `quotoolbox` directory by running
```
cd quotoolbox
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
- `SPARK_CONFIG` - Path to the file configuring a Spark session. For details about configuring Spark sessions, please see [the official documentation](https://spark.apache.org/docs/latest/configuration.html#application-properties). This should provide you with enough information to configure the Spark sessions according to your needs. Note that you can add additional options to the config file according to the [Application properties table](https://spark.apache.org/docs/latest/configuration.html#application-properties) in the documentation. The only option in the provided config file not mentioned in the official documentation is `num_threads`, whose name is self-explanatory. It merely sets the maximum number of processor threads usable by the script.
- `JSON_DATA` - Path to the file with Quotebank data in JSON format.
- `PARQUET_DATA` - Path where Quotebank will be saved in Parquet format.
For example:
```
python json2parquet.py \
        --spark-config config.ini \
        --json data/quotes \
        --parquet data/quotes_parquet
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
- `INPUT` - Path to the original quotation-level Quotebank data.
- `OUTPUT` - Path where clean quotation-level Quotebank data will be written.
- `INPUT_FORMAT` - Format of the input data. (e.g., `json` or `parquet`)
- `OUTPUT_FORMAT` - Format of the output data. (e.g., `json` or `parquet`)
- `DISAMBIGUATION_MAPPING` - Path to the `quoteID` $\rightarrow$ `speakerQID` mapping.
- `SELF_QUOTATIONS_FILTERED` - Path to the data containing quoteIDs of quotations that are not self-attributed. Self-attributed quotations are mostly falsely attributed and should be removed.
- `BLACKLISTS` - Path to the folder containing name and domain blacklists used for filtering quotations appearing only on spurious domains or attributed to speakers with spurious names.
- `COMPRESSION` - Compression algorithm used to compress the resulting data. If not specified, the data will not be compressed.
- `MIN_QUOTATION_LENGTH` - Minimum quotation length in Penn Treebank tokens. Extremely short quotations are usually noise and should be removed. The recommended value for this argument is `5`. Since tokenization is the most computationally expensive operation performed by this script, not removing short quotations by setting this argument to `0` will drastically speed up the runtime.

For example:
```
python cleanup_disambiguate.py \
	--spark-config config.ini \
	--input data/quotes_parquet \
	--output data/quotes_clean_parquet \
	--input_format parquet \
	--output_format parquet \
	--disambiguation-mapping data/quotebank_disambiguation_mapping_quote \
	--self-quotations-filtered data/self_quotations_filtered.parquet \
	--blacklists data/blacklists \
	--min-quotation-length 5
```
This command will use the Spark session configuration specified in `config.ini`, read the quotes stored in Parquet format in `data/quotes_parquet`, and write the resulting data in Parquet format to `data/quotes_clean_parquet`. For speaker disambiguation and self-quotation removal, the data from `data/quotebank_disambiguation_mapping_quote` and `data/self_quotations_filtered.parquet` will be used, respectively. The blacklists will be loaded from `data/blacklists`, while all the quotations with less than 5 Penn Treebank tokens will be removed.