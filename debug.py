from lib.database_utils import create_tables
from lib.author import Author
from lib.magazine import Magazine
from lib.article import Article

# Setup tables
create_tables()

# Create authors
a1 = Author("Ian").save()
a2 = Author("Sarah").save()

# Create magazines
m1 = Magazine("Nature Weekly", "Science").save()
m2 = Magazine("Tech World", "Technology").save()

# Add articles
a1.add_article(m1, "The Wonders of DNA")
a1.add_article(m2, "AI in 2025")
a2.add_article(m1, "Climate Change Realities")

# Print results
print("Ian's Articles:", [a.title for a in a1.articles()])
print("Ian's Magazines:", [m.name for m in a1.magazines()])
print("Sarah's Topics:", a2.topic_areas())

print("Tech World contributors:", [au.name for au in m2.contributors()])
print("Nature Weekly titles:", m1.article_titles())
print("Top Publisher:", Magazine.top_publisher().name)
