import gzip

def read_string(src, pos):
    """Parse a string enclosed in single quotes"""
    length = len(src)
    if pos >= length or src[pos] != "'":
        return None

    pos += 1
    sb = []
    while pos < length and src[pos] != "'":
        if src[pos] == '\\':
            pos += 1
            ch = src[pos] if pos < length else ' '
            if not (ch == '"' or ch == "'" or ch == "\\"):
                sb.append('\\')
        if pos < length:
            s = "\\t" if src[pos] == '\t' else src[pos]
            sb.append(s)
            pos += 1

    if pos < length and src[pos] == "'":
        pos += 1

    return ("".join(sb), pos)

def read_value(src, pos):
    """Read a value (string or non-string) from SQL data"""
    length = len(src)
    if pos >= length:
        return None

    sp = read_string(src, pos)
    if sp is not None:
        return sp

    p = pos
    while p < length and src[p] != ',' and src[p] != ')':
        p += 1
    return (src[pos:p], p)

def read_values(src, pos):
    """Read a set of values enclosed in parentheses"""
    length = len(src)
    if pos >= length or src[pos] != '(':
        return None

    pos += 1
    ret = []
    if pos < length and src[pos] != ')':
        loop = True
        while loop:
            result = read_value(src, pos)
            if result is not None:
                s, p = result
                ret.append(s)
                if p < length and src[p] == ',':
                    pos = p + 1
                else:
                    pos = p
                    loop = False
            else:
                loop = False

    if pos < length and src[pos] == ')':
        pos += 1
    return (ret, pos)

def read_all_values(src, pos):
    """Read multiple sets of values"""
    length = len(src)
    pos = pos
    result = []

    while pos < length:
        values = read_values(src, pos)
        if values is not None:
            s, p = values
            result.append(s)
            # Continue if there's a comma after the values
            if p < length and src[p] == ',':
                pos = p + 1
            else:
                pos = p
                break
        else:
            break

    return result

def read_sql(stream):
    """Read SQL INSERT statements from a file stream"""
    for line in stream:
        if not isinstance(line, str):
            line = line.decode('utf-8', errors='ignore')

        line = line.strip()
        if not line.startswith("INSERT INTO `"):
            continue

        end_table_idx = line.find("`", 13)
        if end_table_idx == -1:
            continue

        table = line[13:end_table_idx]
        p = line.find("VALUES (")

        if p < 0:
            continue

        values = read_all_values(line, p + 7)
        for value in values:
            yield (table, value)

def process_sql_file(file_stream, tsv_files):
    for table, values in read_sql(file_stream):
        if table not in tsv_files:
            tsv_files[table] = open(f"{table}.tsv", "w", encoding="utf-8", newline="\n")
        tsv_files[table].write("\t".join(values) + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Convert SQL file to TSV format')
    parser.add_argument('sql_file', help='SQL file (can be .sql or .sql.gz)')
    args = parser.parse_args()

    target = args.sql_file
    if not (target.endswith(".sql") or target.endswith(".sql.gz")):
        parser.error("Input file must end with .sql or .sql.gz")

    tsv_files = {}

    try:
        if target.endswith(".gz"):
            with gzip.open(target, 'rb') as f:
                process_sql_file(f, tsv_files)
        else:
            with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                process_sql_file(f, tsv_files)
    finally:
        # Close all open files
        for file in tsv_files.values():
            file.close()
