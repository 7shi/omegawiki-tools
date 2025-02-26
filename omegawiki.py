import sqlite3, os, sys

conn, cur = None, None

def open_db(db):
    global conn, cur
    with open(db, "rb") as f: pass
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

def meaning_id(xid):
    result = cur.execute("""
        SELECT defined_meaning_id FROM uw_syntrans WHERE expression_id = ?
        """, (xid,)).fetchone()
    return result[0] if result else None

def get_word(mid, lid):
    result = cur.execute("""
        SELECT uw_syntrans.expression_id, spelling FROM uw_syntrans
        INNER JOIN uw_expression ON uw_syntrans.expression_id = uw_expression.expression_id
        WHERE defined_meaning_id = ? AND language_id = ?
        """, (mid, lid)).fetchone()
    return result if result else (None, "")

if __name__ == "__main__":
    try:
        db, *langs = sys.argv[1:]
    except:
        sys.stderr.write(f"usage: {sys.argv[0]} db lang\n")
        exit(1)

    open_db(db)
    lid, *lids = [language_id(l) for l in langs]
    if not lid:
        print("not found:", lang)
        exit(0)

    names = [language_name(l, l) for l in [lid] + lids]
    print("\t".join(names))
    for xid, spell in sorted(all_words(lid), key=lambda x:x[1].lower()):
        mid = meaning_id(xid)
        words = [str(get_word(mid, l)[1]) for l in lids]
        print("\t".join([spell] + words))
