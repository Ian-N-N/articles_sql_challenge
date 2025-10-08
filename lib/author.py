from lib.database_utils import get_connection

class Author:
    def __init__(self, name, id=None):
        if not isinstance(name, str):
            raise Exception("Author name must be a string.")
        if not name.strip():
            raise Exception("Author name must not be empty.")
        self._name = name
        self.id = id

    def __repr__(self):
        return f"<Author id={self.id} name={self._name!r}>"

    # read-only property
    @property
    def name(self):
        return self._name

    # --- Class / helper methods for DB mapping ---
    @classmethod
    def new_from_db(cls, row):
        """
        row is sqlite3.Row with keys: id, name
        """
        if row is None:
            return None
        # row may be sqlite3.Row or tuple; prefer mapping by keys
        try:
            id_val = row["id"]
            name_val = row["name"]
        except Exception:
            # fallback for tuple ordering (id, name)
            id_val, name_val = row[0], row[1]
        return cls(name_val, id=id_val)

    @classmethod
    def find_by_id(cls, id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM authors WHERE id = ?", (id,))
        row = cur.fetchone()
        conn.close()
        return cls.new_from_db(row)

    def save(self):
        """
        INSERT if no id, else UPDATE
        """
        conn = get_connection()
        cur = conn.cursor()
        if self.id is None:
            cur.execute("INSERT INTO authors (name) VALUES (?)", (self._name,))
            self.id = cur.lastrowid
        else:
            cur.execute("UPDATE authors SET name = ? WHERE id = ?", (self._name, self.id))
        conn.commit()
        conn.close()

    # --- Relationships & aggregate methods ---
    def articles(self):
        """
        Return list of Article instances written by this author.
        """
        from .article import Article  # local import to avoid circular imports

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, author_id, magazine_id FROM articles WHERE author_id = ?", (self.id,))
        rows = cur.fetchall()
        conn.close()
        return [Article.new_from_db(r) for r in rows]

    def magazines(self):
        """
        Return list of distinct Magazine instances where this author has articles.
        """
        from lib.magazine import Magazine

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT m.id, m.name, m.category
            FROM magazines m
            JOIN articles a ON a.magazine_id = m.id
            WHERE a.author_id = ?
            """,
            (self.id,)
        )
        rows = cur.fetchall()
        conn.close()
        return [Magazine.new_from_db(r) for r in rows]

    def add_article(self, magazine, title):
        """
        Create a new Article tied to this author and the provided magazine.
        """
        from .article import Article

        if not isinstance(magazine, object) or magazine is None:
            raise Exception("magazine must be a Magazine instance.")
        # Use isinstance check dynamically
        from lib.magazine import Magazine as _Magazine
        if not isinstance(magazine, _Magazine):
            raise Exception("magazine must be a Magazine instance.")

        if not isinstance(title, str) or not title.strip():
            raise Exception("title must be a non-empty string.")

        article = Article(title=title, author=self, magazine=magazine)
        article.save()
        return article

    def topic_areas(self):
        """
        Extract unique categories from magazines this author contributes to.
        """
        mags = self.magazines()
        # unique categories
        categories = []
        for m in mags:
            if m.category not in categories:
                categories.append(m.category)
        return categories
