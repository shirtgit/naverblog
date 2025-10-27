from utils import parsing
from data.const import *
articles = parsing.get_body()

for article in articles:
    print(article)

count = sum(1 for text in articles if text == PHOTO)
print(count)