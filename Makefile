all:
	python dump2sqlite.py omegawiki-lexical.sql
	rm -f omegawiki.db
	sqlite3 omegawiki.db ".read omegawiki-lexical-sqlite.sql"

download:
	wget -c --waitretry=5 http://www.omegawiki.org/downloads/omegawiki-lexical.sql.gz

upload:
	huggingface-cli upload --repo-type=dataset n7shi/OmegaWiki $(FILENAME)
