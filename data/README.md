# Auxilliary data descriptions
This data repository contains the datasets useful for enriching and preprocessing [Quotebank](https://zenodo.org/record/4277311), a dataset of unique, speaker-attributed quotations. The scripts utilizing the below data can be found in the [quotoolbox](https://www.github.com/epfl-dlab/quotoolbox). The provided datasets are listed and provided below.
## Blacklists
- `domain_blaklists.txt` - a list of web domains (one per line) that usually feature noisy and fully attributed quotations. There is one web domain in each line.
- `name_blacklist.txt` - a list of names (one per lane) belonging to fictional characters or non-person entities. 

## `disambiguation_mapping.parquet`
Provides the `quoteID`-> `speakerQID` mapping for each quotation, disambiguating ambiguous speaker names and linking them to their respective [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) items. The schema of the dataset is as follows:
```
 |-- quoteID: primary key of the quotation (format: "YYYY-MM-DD-{increasing int:06d}")
 |-- speaker: Wikidata ID corresponding to the speaker of the quotation
```
## `self_quotations_filtered.parquet`
Contains the identifiers of the quotations identified as not being self-attributed. The schema of the dataset is as follows:
```
 |-- quoteID: primary key of the quotation (format: "YYYY-MM-DD-{increasing int:06d}") 
```
## `speaker_attributes.parquet`
Contains attributes of all the speakers appearing in Quotebank extracted from Wikidata. 
```
 |-- id: Wikidata item QID of the speaker, primary key
 |-- aliases: list of speaker's aliases
 |-- date_of_birth: list of possible speaker's dates of birth
 |-- nationality: list of speaker's nationalities
 |-- gender: list of speaker's previous or current genders
 |-- lastrevid: ID of the last revision of the speaker's item
 |-- ethnic_group: list of ethnic groups the speaker belongs to
 |-- US_congress_bio_ID: identifier for the speaker on the Biographical Directory of the United States Congress
 |-- occupation: list of speaker's occupations
 |-- party: list of parties the speaker is/was affiliated to
 |-- academic_degree: list of academic degrees obtained by the speaker
 |-- label: Wikidata label of the speaker
 |-- candidacy: list of the speaker's candidacies in political elections
 |-- type: type of the Wikidata entry (value is `item` for all the speakers)
 |-- religion: previous/current religious affiliations of the speaker
```
Using the `id` field corresponding to the Wikidata QID of a speaker, this dataset can be easily joined with disambiguated Quotebank obtained by running the `cleanup_disambiguate.py` script available in the aforementioned [quotoolbox](https://www.github.com/epfl-dlab/quotoolbox) repository.
