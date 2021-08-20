import os
import json
import sqlite3

def get_lan_server(id, text):
    default_language = "ja"

    if os.path.exists("main.db"):
        conn = sqlite3.connect("main.db", isolation_level=None)
        c = conn.cursor()
        c.execute("SELECT * FROM server WHERE id=:Id", {"Id": id})
        temp = c.fetchone()
        if temp is None:
            language = default_language
        else:
            language = temp[1]
            if not os.path.exists(f"lang/{language}.json"):
                language = default_language
        conn.close()
        # read language file
        with open(f"lang/{language}.json", 'rt', encoding='UTF8') as f:
            language_data = json.load(f)
        return language_data[text]

    else:
        with open(f"lang/{default_language}.json", 'rt', encoding='UTF8') as f:
            language_data = json.load(f)
        return language_data[text]
