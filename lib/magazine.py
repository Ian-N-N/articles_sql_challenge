from .database_utils import get_connection

class Magazine:
    def __init__(self, name, category, id=None):
        # validation for name and category (read/write)
        if not isinstance(name, str):
            raise Exception("Magazine name must be a string.")
        if not name.strip():
            raise Exception("Magazine name must not be empty.")
        if not isinstance(category, str):
            raise Exception("Magazine category must be a string.")
        if not category.strip():
            raise Exception("Magazine category must not be empty.")

        self._name = name
        self._category = category
        self.id = id

    def __repr__(self):
        return f"<Magazine id={self.id} name={self._name!r} category={self._category!r}>"

    # name property (read/write)
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise Exception("Magazine name must be a string.")
        if not value.strip():
            raise Exception("Magazine name must not be empty.")
        self._name = value

    # category property (read/write)
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, str):
            raise Exception("Magazine category must be a string.")
        if not value.strip():
            raise Exception("Magazine category must not be empty.")
        self._category = value

    # --- DB helper methods ---
    @classmethod
    def new_from_db(cls, row):
        if row is None:
            return None
        try:
            id_val = row["id"]
            name_val = row["name"]
            category_val = row["category"]
        except Exception:
            id_val, name_val, category_val = row[0], row[1], row[2]
        return cls(name_val, category_val, id=id_val)

    @classmethod
    def find_by_id(cls, id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, category FROM magazines WHERE id = ?", (id,))
        row = cur.fetchone()
        conn.close()
        return cls.new_from_db(row)

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        if self.id is None:
            cur.execute(
                "INSERT INTO magazines (name, category) VALUES (?, ?)",
                (self._name, self._category)
            )
            self.id = cur.lastrowid
        else:
            cur.execute(
                "UPDATE magazines SET name = ?, category = ? WHERE id = ?",
                (self._name, self._category, self.id)
            )
        conn.commit()
        conn.close()

    # --- Relationships & aggregates ---
    def articles(self):
        from .article import Article

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, author_id, magazine_id FROM articles WHERE magazine_id = ?", (self.id,))
        rows = cur.fetchall()
        conn.close()
        return [Article.new_from_db(r) for r in rows]

    def contributors(self):
        """
        Return distinct Author instances who have articles in this magazine.
        """
        from .author import Author

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT au.id, au.name
            FROM authors au
            JOIN articles a ON a.author_id = au.id
            WHERE a.magazine_id = ?
            """,
            (self.id,)
        )
        rows = cur.fetchall()
        conn.close()
        return [Author.new_from_db(r) for r in rows]

    def article_titles(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title FROM articles WHERE magazine_id = ?", (self.id,))
        rows = cur.fetchall()
        conn.close()
        # rows are Row objects with 'title'
        return [r["title"] for r in rows]

    def contributing_authors(self):
        """
        Return Author instances who have more than 2 articles in this magazine.
        Uses GROUP BY ... HAVING COUNT(id) > 2
        """
        from .author import Author

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT author_id
            FROM articles
            WHERE magazine_id = ?
            GROUP BY author_id
            HAVING COUNT(id) > 2
            """,
            (self.id,)
        )
        rows = cur.fetchall()
        conn.close()
        author_ids = [r["author_id"] for r in rows]
        return [Author.find_by_id(aid) for aid in author_ids]

    @staticmethod
    def top_publisher():
        """
        Bonus: Return the Magazine with the most articles (or None).
        """
        from .magazine import Magazine as _Magazine

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT magazine_id, COUNT(id) as cnt
            FROM articles
            GROUP BY magazine_id
            ORDER BY cnt DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        mag_id = row["magazine_id"]
        return _Magazine.find_by_id(mag_id)
