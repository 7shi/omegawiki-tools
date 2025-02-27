TARGET := omegawiki.db
SQL1 := omegawiki-lexical-20230530.sql
SQL2 := $(SQL1:.sql=-sqlite.sql)

all: $(TARGET)

$(TARGET): $(SQL1)
	python ../sql2tsv.py $<
	python ../dump2sqlite.py $<
	sqlite3 $@ ".read $(SQL2)"

clean:
	rm -f $(TARGET) $(SQL2) *.tsv

.PHONY: all clean
