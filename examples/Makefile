TARGETS = Latin.tsv Ido.tsv
DB = ../db/omegawiki.db

all: $(TARGETS)

clean:
	rm -f $(TARGETS)

Latin.tsv: $(DB)
	python ../omegawiki.py $(DB) la it es fr en ja > $@

Ido.tsv: $(DB)
	python ../omegawiki.py $(DB) io eo la fr en ja > $@

.PHONY: all clean
