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
    return [(row[0], str(row[1])) for row in cur.execute("""
        SELECT expression_id, spelling FROM uw_expression WHERE language_id = ?
        """, (lid,))]

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
    parser.add_argument('-u', '--uniq', action='store_true', help='only show unique translations')
    args = parser.parse_args()
    
    db, langs = args.db, args.langs

    open_db(db)
    lids = []
    unknowns = []
    for lang in langs:
        lid = language_id(lang)
        (lids if lid else unknowns).append(lid)
    if unknowns:
        print("Unknown language(s):", ", ".join(unknowns))
        exit(1)

    names = [language_name(lid, lid) for lid in lids]
    print("\t".join(names))
    for xid, spell in sorted(all_words(lids[0]), key=lambda x: x[1].lower()):
        mids = meaning_ids(xid)
        translations = []
        for lid in lids[1:]:
            meanings = []
            translation_words = set()
            for mid in mids:
                words = []
                for word in get_words(mid, lid):
                    if not args.uniq or word not in translation_words:
                        translation_words.add(word)
                        words.append(word)
                meanings.append(", ".join(words))
            if translation_words:
                if args.uniq:
                    meanings = [m for m in meanings if m]
                translations.append("; ".join(meanings))
            else:
                translations.append("")
        print(spell, *translations, sep="\t")
