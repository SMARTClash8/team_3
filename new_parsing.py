from bs4 import BeautifulSoup as bs
import requests



def get_wp_news():
    url = "https://www.washingtonpost.com/politics/?itid=hp_top_nav_politics"
    response = requests.get(url)
    soup = bs(response.text, 'lxml')

    stories = soup.find_all("div", attrs={'data-feature-id': 'homepage/story'})
    articles = []

    for story in stories:
        article = {
            "name": story.find("h3").text,
            "description": story.find("p").text,
            "author": story.find_all("a", attrs={'class': ["wpds-c-knSWeD", "wpds-c-knSWeD-iRfhkg-as-a"]})[0].text,
            "source": "Washington Post"
        }
        if article not in articles:
            articles.append(article)
    articles = articles[:5]
    return articles