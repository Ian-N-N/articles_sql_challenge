from lib.magazine import Magazine
from lib.author import Author

def test_magazine_creation_and_update():
    m = Magazine("Nature", "Science").save()
    assert m.id is not None

    m.name = "Nature Weekly"
    m.save()
    updated = Magazine.find_by_id(m.id)
    assert updated.name == "Nature Weekly"

def test_magazine_articles_and_contributors():
    a1 = Author("John").save()
    a2 = Author("Sarah").save()
    m = Magazine("Space", "Astronomy").save()

    a1.add_article(m, "Stars")
    a2.add_article(m, "Planets")

    assert len(m.articles()) == 2
    contributors = [a.name for a in m.contributors()]
    assert "John" in contributors and "Sarah" in contributors

def test_article_titles_method():
    a = Author("Ella").save()
    m = Magazine("Health", "Wellness").save()
    a.add_article(m, "Sleep Well")
    a.add_article(m, "Eat Better")
    titles = m.article_titles()
    assert sorted(titles) == ["Eat Better", "Sleep Well"]
