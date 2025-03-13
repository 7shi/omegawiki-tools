import sqlite3

conn, cur = None, None
lid_en = None

def open_db(db):
    global conn, cur, lid_en
    conn = sqlite3.connect(db)
    cur  = conn.cursor()
    lid_en = language_id("en")

def language_id(code):
    result = cur.execute("""
        SELECT language_id FROM language
        WHERE wikimedia_key = ? OR iso639_3 = ? OR iso639_2 = ?
        """, (code, code, code)).fetchone()
    if result: return result[0]
    result = cur.execute("""
        SELECT language_id FROM language_names WHERE language_name = ?
        """, (code,)).fetchone()
    if result: return result[0]
    result = cur.execute("""
        SELECT language_id FROM language_names WHERE language_name LIKE ?
        """, (code + "%",)).fetchone()
    return result[0] if result else None

def language_name(lid, name_lid=None):
    if name_lid:
        result = cur.execute("""
            SELECT language_name FROM language_names
            WHERE language_id = ? AND name_language_id = ?
            """, (lid, name_lid)).fetchone()
        return result[0] if result else ""
    name = language_name(lid, lid) or language_name(lid, lid_en)
    if name:
        return name
    result = cur.execute("""
        SELECT language_name FROM language_names
        WHERE language_id = ?
        LIMIT 1
        """, (lid,)).fetchone()
    return result[0] if result else ""

def langcode(lid):
    return cur.execute("""
        SELECT iso639_3, wikimedia_key FROM language WHERE language_id = ?
        """, (lid,)).fetchone()

def all_words(lid):
    return [(row[0], str(row[1])) for row in cur.execute("""
        SELECT expression_id, spelling FROM uw_expression WHERE language_id = ?
        """, (lid,))]

def expression_ids(spelling, lid):
    return [row[0] for row in cur.execute("""
        SELECT expression_id FROM uw_expression WHERE spelling = ? AND language_id = ?
        """, (spelling, lid))]

def meaning_ids(xid):
    return [row[0] for row in cur.execute("""
        SELECT defined_meaning_id FROM uw_syntrans WHERE expression_id = ?
        """, (xid,))]

def get_words(mid, lid):
    return [(row[0], str(row[1])) for row in cur.execute("""
        SELECT uw_syntrans.expression_id, spelling FROM uw_syntrans
        INNER JOIN uw_expression ON uw_syntrans.expression_id = uw_expression.expression_id
        WHERE defined_meaning_id = ? AND language_id = ?
        """, (mid, lid))]

class Language:
    def __init__(self, id = None, code = None):
        if id:
            self.id = id
        elif code:
            self.id = language_id(code)
        else:
            self.id = None
        self.name = language_name(self.id) if self.id else ""

    def code(self):
        return langcode(self.id)

    def words(self):
        return [Word(Expression(xid), spelling, self)
                for xid, spelling in all_words(self.id)]

    def lookup(self, spelling):
        return [Word(Expression(xid), spelling, self)
                for xid in expression_ids(spelling, self.id)]

class Word:
    def __init__(self, expression, spelling, language):
        self.expression = expression
        self.spelling = spelling
        self.language = language
        self.meanings = None

class Expression:
    def __init__(self, id):
        self.id = id

    def meanings(self):
        return [Meaning(mid) for mid in meaning_ids(self.id)]

class Meaning:
    def __init__(self, id):
        self.id = id

    def words(self, lang):
        return [Word(Expression(xid), spelling, lang)
                for xid, spelling in get_words(self.id, lang.id)]

def translate(target, *languages, uniq=False):
    """Generates translations for a target word in specified languages.
    
    Args:
        target: The Word object to translate
        *languages: Language objects to translate into
        uniq: If True, returns only unique spellings per language
        
    Returns:
        list[list[list[Word]]]: For each language, list of meanings lists containing translated Word objects.
        When uniq=True, filters out empty meaning lists and ensures unique spellings within a language.
    """
    target_meanings = target.expression.meanings()
    translations = []
    for lang in languages:
        meanings = []
        cache = set()
        for meaning in target_meanings:
            words = []
            for w in meaning.words(lang):
                word = w.spelling
                if not uniq or word not in cache:
                    cache.add(word)
                    words.append(w)
            meanings.append(words)
        if not cache:
            meanings = []
        elif uniq:
            meanings = [m for m in meanings if m]
        translations.append(meanings)
    return translations

if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description='OmegaWiki database query tool')
    parser.add_argument('db', help='database file')
    parser.add_argument('langs', nargs='+', help='language codes')
    parser.add_argument('-u', '--uniq', action='store_true', help='only show unique translations')
    parser.add_argument('-w', '--word', help='word to search for')
    args = parser.parse_args()

    open_db(args.db)
    languages = []
    unknowns = []
    for code in args.langs:
        lang = Language(code=code)
        if lang.id:
            languages.append(lang)
        else:
            unknowns.append(code)
    if unknowns:
        print("Unknown language(s):", ", ".join(unknowns), file=sys.stderr)
        exit(1)

    if args.word:
        words = languages[0].lookup(args.word)
    else:
        words = languages[0].words()
    if not words:
        print("No words found", file=sys.stderr)
        exit(1)

    print("\t".join(lang.name for lang in languages))
    for word in sorted(words, key=lambda w: w.spelling.lower()):
        translations = [
            "; ".join(", ".join(w.spelling for w in ws) for ws in translated)
            for translated in translate(word, *languages[1:], uniq=args.uniq)
        ]
        if not args.uniq or any(t for t in translations):
            print(word.spelling, *translations, sep="\t")
