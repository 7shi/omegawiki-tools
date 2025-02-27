# OmegaWiki Data Processing Tools

OmegaWiki was a collaborative multilingual dictionary project (now discontinued).

This project provides tools for processing and querying OmegaWiki database dumps.

## Requirements

- Python 3 (no additional libraries required)
- SQLite 3

## Tools

- `sql2tsv.py`: Extracts data from SQL dump to TSV format
- `dump2sqlite.py`: Creates a SQL from SQL dump to import the data into SQLite
- `omegawiki.py`: Extracts multilingual word lists from the database

## Directory Structure

- `db/`: Contains database processing scripts and data files
- `examples/`: Contains example language extraction scripts
- `etc/`: Experimental files and resources

## Database Schema

Below is an Entity-Relationship diagram of the main tables in the OmegaWiki database:

```mermaid
erDiagram
    language {
        int language_id PK
        int dialect_of_lid
        string iso639_2
        string iso639_3
        string wikimedia_key
    }
    language_names {
        int language_id PK
        int name_language_id PK
        string language_name
    }
    uw_expression {
        int expression_id
        string spelling
        int language_id FK
        int add_transaction_id
        int remove_transaction_id
    }
    uw_defined_meaning {
        int defined_meaning_id
        int expression_id FK
        int meaning_text_tcid
        int add_transaction_id
        int remove_transaction_id
    }
    uw_syntrans {
        int syntrans_sid
        int defined_meaning_id FK
        int expression_id FK
        boolean identical_meaning
        int add_transaction_id
        int remove_transaction_id
    }
    uw_text {
        int text_id PK
        blob text_text
        blob text_flags
    }
    uw_translated_content {
        int translated_content_id
        int language_id FK
        int text_id FK
        int add_transaction_id
        int remove_transaction_id
    }
    uw_meaning_relations {
        int relation_id
        int meaning1_mid FK
        int meaning2_mid FK
        int relationtype_mid FK
        int add_transaction_id
        int remove_transaction_id
    }
    
    language ||--o{ language_names : "has names in"
    language ||--o{ uw_expression : "contains"
    uw_expression ||--o{ uw_defined_meaning : "defines"
    uw_defined_meaning ||--o{ uw_syntrans : "has"
    uw_expression ||--o{ uw_syntrans : "used in"
    uw_text ||--o{ uw_translated_content : "translated as"
    language ||--o{ uw_translated_content : "in language"
    uw_defined_meaning ||--o{ uw_meaning_relations : "meaning1"
    uw_defined_meaning ||--o{ uw_meaning_relations : "meaning2"
```

## Processing the Database

In `db/` directory:

1. Place the OmegaWiki dump file `omegawiki-lexical-20230530.sql.gz` retrieved from:  
   https://huggingface.co/datasets/n7shi/OmegaWiki
2. Extract the `.gz` file using `gunzip`
3. Run `make` to create `omegawiki.db`

To clean up generated files:

```bash
make clean
```

## Extracting Language Data

Example usage for extracting multilingual word lists:

```bash
cd examples
make
```

This will create:

- `Latin.tsv`: Latin words with Italian, Spanish, French, English, and Japanese translations
- `Ido.tsv`: Ido words with Esperanto, Latin, French, English, and Japanese translations

Note: Ido is a constructed language based on Esperanto.

Custom language extraction can be done using:

```bash
python omegawiki.py db/omegawiki.db [source-lang] [target-lang1] [target-lang2] ...
```
