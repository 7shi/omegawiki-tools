import sqlite3

conn, cur = None, None

def open_db(db):
    global conn, cur
    conn = sqlite3.connect(db)
    cur  = conn.cursor()

def language_id(name):
    result = cur.execute("""
        SELECT language_id FROM language
        WHERE wikimedia_key = ? OR iso639_3 = ? OR iso639_2 = ?
        """, (name, name, name)).fetchone()
    if result: return result[0]
    result = cur.execute("""
        SELECT language_id FROM language_names WHERE language_name = ?
        """, (name,)).fetchone()
    if result: return result[0]
    result = cur.execute("""
        SELECT language_id FROM language_names WHERE language_name LIKE ?
        """, (name + "%",)).fetchone()
    return result[0] if result else None

def language_name(lid, name_lid):
    result = cur.execute("""
        SELECT language_name FROM language_names
        WHERE language_id = ? AND name_language_id = ?
        """, (lid, name_lid)).fetchone()
    return result[0] if result else ""

def langcode(lid):
    return cur.execute("""
        SELECT iso639_3, wikimedia_key FROM language WHERE language_id = ?
        """, (lid,)).fetchone()

def all_words(lid):
    return conn.cursor().execute("""
        SELECT expression_id, spelling FROM uw_expression WHERE language_id = ?
        """, (lid,))

def meaning_ids(xid):
    return [row[0] for row in cur.execute("""
        SELECT defined_meaning_id FROM uw_syntrans WHERE expression_id = ?
        """, (xid,))]

def get_words(mid, lid):
    return [str(row[0]) for row in cur.execute("""
        SELECT spelling FROM uw_syntrans
        INNER JOIN uw_expression ON uw_syntrans.expression_id = uw_expression.expression_id
        WHERE defined_meaning_id = ? AND language_id = ?
        """, (mid, lid))]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='OmegaWiki database query tool')
    parser.add_argument('db', help='database file')
    parser.add_argument('langs', nargs='+', help='language codes')
    args = parser.parse_args()
    
    db, langs = args.db, args.langs

    open_db(db)
    lids = []
    for lang in langs:
        lid = language_id(lang)
        if not lid:
            print("language not found:", lang)
        lids.append(lid)
    if None in lids:
        exit(1)

    names = [language_name(lid, lid) for lid in lids]
    print("\t".join(names))
    for xid, spell in sorted(all_words(lids[0]), key=lambda x: x[1].lower()):
        mids = meaning_ids(xid)
        words = [
            "; ".join(
                words
                for mid in mids
                if (words := ", ".join(get_words(mid, lid)))
            )
            for lid in lids[1:]
        ]
        print(spell, *words, sep="\t")
