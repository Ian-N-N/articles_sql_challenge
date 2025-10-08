import pytest
from lib.author import Author
from lib.magazine import Magazine
from lib.article import Article

def test_author_name_validation():
    with pytest.raises(Exception):
        Author("").save()
    with pytest.raises(Exception):
        Author(123).save()

def test_magazine_validation():
    with pytest.raises(Exception):
        Magazine("", "Science")
    with pytest.raises(Exception):
        Magazine("Nature", "")

def test_article_validation():
    a = Author("Valid Author").save()
    m = Magazine("Valid Mag", "Tech").save()
    with pytest.raises(Exception):
        Article("", a, m)
    with pytest.raises(Exception):
        Article("Title", "NotAuthor", m)
    with pytest.raises(Exception):
        Article("Title", a, "NotMag")

def test_foreign_key_enforcement():
    """
    Ensure article cannot reference invalid author/magazine IDs.
    """
    a = Author("Paul").save()
    m = Magazine("Business", "Finance").save()

    from lib.database_utils import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    with pytest.raises(Exception):
        # invalid author_id
        cursor.execute(
            "INSERT INTO articles (title, author_id, magazine_id) VALUES (?, ?, ?)",
            ("Invalid FK", 999, m.id)
        )
        conn.commit()
