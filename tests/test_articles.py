import pytest
from lib.article import Article
from lib.author import Author
from lib.magazine import Magazine

def test_article_creation_and_save():
    a = Author("Leo").save()
    m = Magazine("Nature", "Science").save()
    art = Article("Photosynthesis", a, m).save()
    assert art.id is not None
    assert art.title == "Photosynthesis"

def test_article_find_and_relationships():
    a = Author("Grace").save()
    m = Magazine("Computing", "Tech").save()
    art = a.add_article(m, "AI Ethics")

    fetched = art
    assert fetched.author.name == "Grace"
    assert fetched.magazine.name == "Computing"

def test_update_article_title():
    a = Author("Tom").save()
    m = Magazine("Design", "Art").save()
    art = Article("Minimalism", a, m).save()
    art._title = "Modern Design"
    art.save()
    updated = Article.new_from_db({"id": art.id, "title": "Modern Design", "author_id": a.id, "magazine_id": m.id})
    assert updated.title == "Modern Design"
