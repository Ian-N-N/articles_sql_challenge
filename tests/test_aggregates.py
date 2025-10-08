from lib.author import Author
from lib.magazine import Magazine

def test_author_topic_areas():
    a = Author("Nina").save()
    m1 = Magazine("Science Daily", "Science").save()
    m2 = Magazine("Tech Review", "Technology").save()
    a.add_article(m1, "Biotech")
    a.add_article(m2, "AI Advances")
    topics = a.topic_areas()
    assert "Science" in topics
    assert "Technology" in topics

def test_magazine_contributing_authors_and_top_publisher():
    a1 = Author("Kate").save()
    m1 = Magazine("Global News", "News").save()

    # Kate writes 3 articles in the same magazine
    for t in ["World", "Economy", "Politics"]:
        a1.add_article(m1, t)

    # Contributing author threshold (3+ articles)
    contribs = m1.contributing_authors()
    assert len(contribs) == 1 and contribs[0].name == "Kate"

    # Top publisher should be Global News
    top = Magazine.top_publisher()
    assert top.name == "Global News"
