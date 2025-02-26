import re, argparse

parser = argparse.ArgumentParser(description='Convert SQL dump to SQLite format')
parser.add_argument('sql', help='Input SQL file')
args = parser.parse_args()

sql = args.sql
if not sql.endswith('.sql'):
    parser.error('Input file must have .sql extension')

with open(sql, "r", encoding="utf-8", errors="replace") as f1:
    with open(sql[:-4] + "-sqlite.sql", "w", encoding="utf-8") as f2:
        f2.write(f"-- convert from {sql}\n");
        f2.write("\n.mode ascii\n")
        f2.write('.separator "\\t" "\\n"\n')
        table   = ""
        indices = []
        def create_indices():
            if not table: return
            for idx, cols in indices:
                f2.write(f"CREATE INDEX `{table}_{idx}` ON `{table}`({cols});\n")
        while (line := next(f1, "")):
            if table and line.startswith("INSERT INTO "):
                f2.write(f".import {table}.tsv {table}\n")
                create_indices()
                table = ""
            if not (m := re.match("DROP TABLE IF EXISTS `(.*)`", line)):
                continue
            create_indices()
            table = m[1]
            f2.write(f"\n.print importing {table}.tsv ...\n")
            f2.write(line)
            while (line := next(f1)) and line.startswith("/*"):
                pass
            f2.write(line)
            columns = []
            indices = []
            while (line := next(f1).strip()) and not line.startswith(")"):
                if (m := re.match(r"KEY `(.*?)` \((.*)\)", line)):
                    indices.append((m[1], m[2]))
                else:
                    line = re.sub(",$", "", line)
                    line = re.sub(r"\bunsigned\b", "", line)
                    line = re.sub(r"\bAUTO_INCREMENT\b", "", line)
                    line = re.sub(r"\bCHARACTER SET \w+", "", line)
                    columns.append(line.strip())
            f2.write("  " + ",\n  ".join(columns) + "\n);\n");
        create_indices()
