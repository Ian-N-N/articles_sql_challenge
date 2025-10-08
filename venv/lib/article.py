from lib.database_utils import get_connection

class Article:
    def __init__(self, title, author, magazine, id=None):
        # title validation (read-only property)
        if not isinstance(title, str):
            raise Exception("Article title must be a string.")
        if not title.strip():
            raise Exception("Article title must not be empty.")

        # author and magazine should be instances of Author and Magazine
        # we avoid importing at module load to prevent circular import
        from lib.author import Author as _Author
        from lib.magazine import Magazine as _Magazine

        if not isinstance(author, _Author):
            raise Exception("author must be an Author instance.")
        if not isinstance(magazine, _Magazine):
            raise Exception("magazine must be a Magazine instance.")

        self._title = title
        self._author = author
        self._magazine = magazine
        self.id = id

    def __repr__(self):
        return f"<Article id={self.id} title={self._title!r} author_id={self._author.id} magazine_id={self._magazine.id}>"

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        from lib.author import Author as _Author
        if not isinstance(value, _Author):
            raise Exception("author must be an Author instance.")
        self._author = value

    @property
    def magazine(self):
        return self._magazine

    @magazine.setter
    def magazine(self, value):
        from lib.magazine import Magazine as _Magazine
        if not isinstance(value, _Magazine):
            raise Exception("magazine must be a Magazine instance.")
        self._magazine = value

    # --- DB helpers ---
    @classmethod
    def new_from_db(cls, row):
        if row is None:
            return None
        try:
            id_val = row["id"]
            title_val = row["title"]
            author_id = row["author_id"]
            magazine_id = row["magazine_id"]
        except Exception:
            id_val, title_val, author_id, magazine_id = row[0], row[1], row[2], row[3]

        # Lazy: fetch author and magazine objects by id
        from lib.author import Author
        from lib.magazine import Magazine
        author_obj = Author.find_by_id(author_id)
        magazine_obj = Magazine.find_by_id(magazine_id)
        return cls(title_val, author_obj, magazine_obj, id=id_val)

    @classmethod
    def find_by_id(cls, id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, author_id, magazine_id FROM articles WHERE id = ?", (id,))
        row = cur.fetchone()
        conn.close()
        return cls.new_from_db(row)

    def save(self):
        """
        INSERT or UPDATE using foreign keys from self.author.id and self.magazine.id
        """
        from lib.author import Author as _Author
        from lib.magazine import Magazine as _Magazine

        if not isinstance(self._author, _Author):
            raise Exception("author must be an Author instance before saving.")
        if not isinstance(self._magazine, _Magazine):
            raise Exception("magazine must be a Magazine instance before saving.")
        if self._author.id is None or self._magazine.id is None:
            raise Exception("author and magazine must be saved (have ids) before saving article.")

        conn = get_connection()
        cur = conn.cursor()
        if self.id is None:
            cur.execute(
                "INSERT INTO articles (title, author_id, magazine_id) VALUES (?, ?, ?)",
                (self._title, self._author.id, self._magazine.id)
            )
            self.id = cur.lastrowid
        else:
            cur.execute(
                "UPDATE articles SET title = ?, author_id = ?, magazine_id = ? WHERE id = ?",
                (self._title, self._author.id, self._magazine.id, self.id)
            )
        conn.commit()
        conn.close()
