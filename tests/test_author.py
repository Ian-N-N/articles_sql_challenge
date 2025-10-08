from lib.author import Author
from lib.magazine import Magazine

def test_author_creation_and_save():
    a = Author("Alice").save()
    assert isinstance(a.id, int)
    assert a.name == "Alice"

def test_author_find_by_id():
    a = Author("Bob").save()
    fetched = Author.find_by_id(a.id)
    assert fetched.name == "Bob"
    assert fetched.id == a.id

def test_author_articles_and_magazines():
    a = Author("Charlie").save()
    m1 = Magazine("World", "News").save()
    m2 = Magazine("Techy", "Tech").save()

    a.add_article(m1, "Headline 1")
    a.add_article(m2, "AI Today")

    assert len(a.articles()) == 2
    magazine_names = [m.name for m in a.magazines()]
    assert "World" in magazine_names and "Techy" in magazine_names
