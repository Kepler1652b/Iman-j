from typing import Any, Protocol,Dict,List
from httpx import Client,post,get
from data_parser import Parser
from bs4 import BeautifulSoup
from scraper_utilities import format_timestamp
import json
import feedparser

class Scraper(Protocol):
    """
    Main Protocol class for Scrapers 

    """

    def scrape(self,max_movie:int = 20) -> None:
        pass

    def parse(self,data) -> dict:
        pass


class ZoomgScraper:

    def __init__(self,session):
        self.__baseUrl = "https://www.zoomg.ir/cinema/"
        self.__session:Client = session

    def scrape(self,max_movie:int = 20) -> dict:
        return "zoomg - scraper"

    def parse(self,data) -> dict:
        return "Not Parsed"


class MoviemagScraper:

    def __init__(self,session):
        self.__baseUrl = "https://moviemag.ir/category/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1-%d8%b3%db%8c%d9%86%d9%85%d8%a7%db%8c-%d8%ac%d9%87%d8%a7%d9%86/"
        self.__session:Client = session
        self.__RSS_URL = "https://moviemag.ir/category/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1-%d8%b3%db%8c%d9%86%d9%85%d8%a7%db%8c-%d8%ac%d9%87%d8%a7%d9%86/feed/"

    def scrape(self) -> dict:
        feed = feedparser.parse(self.__RSS_URL)
        return feed
    

    def parse(self,feed) ->  List[Dict[str,Any]]:
        data = []
        for entry in feed.entries:
            formated:dict = {
                "title":entry.get("title"), 
                "type":"", 
                "description":entry.get("summary", "")[:200],
                "year":entry.get("published", entry.get("updated", "N/A")), 
                "duration":"", 
                "imdb":"", 
                "persian":"", 
                "image":"", 
                "cover":"", 
                "trailer":{}, 
                "genres":[{}], 
                "countries":[{}], 
                "actors":[{}], 


            }
            data.append(formated)

        return data


class GameFaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://gamefa.com/category/cinema/"
        self.__session:Client = session

    def scrape(self,max_movie:int = 20) -> dict:
        response = session.get(self.__baseUrl)
        html = response.text
        return html
    

    def parse(self,html) ->  List[Dict[str,Any]]:
        data = []
        soup = BeautifulSoup(html, "html.parser")

        # Find all news cards
        news_cards = soup.find_all("div", class_="row align-items-center")

        for card in news_cards:
            # Category
            category = card.find("span", class_="category")
            category_text = category.text.strip() if category else "N/A"

            # Title
            title = card.find("h4", class_="title")
            title_text = title.text.strip() if title else "N/A"

            # Time
            time = card.find("div", class_="time")
            time_text = time.find("span").text.strip() if time else "N/A"

            # Comments
            comments = card.find("div", class_="comment-count")
            comments_text = comments.find("span").text.strip() if comments else "0"

            # Likes
            likes = card.find("div", class_="like-count")
            likes_text = likes.find("span").text.strip() if likes else "0"

            # Thumbnail
            img_tag = card.find("img")
            img_src = img_tag['src'] if img_tag else "N/A"

            # data_dcit={
            #     "category": category_text,
            #     "title": title_text,
            #     "time": time_text,
            #     "comments": comments_text,
            #     "likes": likes_text,
            #     "thumbnail": img_src
            # }
            formated:dict = {
                "title":title_text, 
                "type":"", 
                "description":"", 
                "year":"", 
                "duration":time_text, 
                "imdb":"", 
                "persian":"", 
                "image":img_src, 
                "cover":img_src, 
                "trailer":{}, 
                "genres":[{}], 
                "countries":[{}], 
                "actors":[{}], 


            }
            data.append(formated)

        return data


class FromCinemaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://www.fromcinema.com/cinema-news/"
        self.__session:Client = session
        self.__section = (".elementor-element-ce54b4c > div:nth-child(1) > div:nth-child(1)",".elementor-element-e6930cd > div:nth-child(1) > div:nth-child(1)")
    
    
    def scrape(self) ->  List[Dict[str,Any]]:
        
        data = self.__session.get(self.__baseUrl)
        self.__session.close()
        soup = BeautifulSoup(data.text,"html.parser")
        articel_soup = soup.select_one(self.__section[0])
        articel_list = articel_soup.find_all("article")
    
        return articel_list


    def parse(self, article_list):
            data = []
            for article in article_list:
                # Title and URL
                title_tag = article.find("h3", class_="elementor-post__title")
                title = title_tag.get_text(strip=True) if title_tag else "Null"
                url = title_tag.find("a")["href"] if title_tag and title_tag.find("a") else "Null"

                # Excerpt / Description
                description_tag = article.find("div", class_="elementor-post__excerpt")
                description = description_tag.get_text(strip=True) if description_tag else "Null"

                # Meta info
                author_tag = article.find("span", class_="elementor-post-author")
                author = author_tag.get_text(strip=True) if author_tag else "Null"

                date_tag = article.find("span", class_="elementor-post-date")
                date = date_tag.get_text(strip=True) if date_tag else "Null"

                time_tag = article.find("span", class_="elementor-post-time")
                time = time_tag.get_text(strip=True) if time_tag else "Null"

                # Image (optional)
                img_tag = article.find("img")
                image_url = img_tag.get("src", "Null") if img_tag else "Null"

                # Read more link (optional)
                read_more_tag = article.find("a", class_="elementor-post__read-more")
                read_more_url = read_more_tag["href"] if read_more_tag else url

                # Save parsed data
                
                # data_dict = {
                #         "title": title,
                #         "url": url,
                #         "description": description,
                #         "author": author,
                #         "date": date,
                #         "time": time,
                #         "image_url": image_url,
                #         "read_more_url": read_more_url
                # }


                formated:dict = {
                        "title":title, 
                        "type":"", 
                        "description":description, 
                        "year":date, 
                        "duration":time, 
                        "imdb":"", 
                        "persian":"", 
                        "image":image_url, 
                        "cover":"", 
                        "trailer":{}, 
                        "genres":[{}], 
                        "countries":[{}], 
                        "actors":[{}], 


                    }
                data.append(formated)

            return data
            

class CaffeCinemaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://caffecinema.com/category/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D8%AC%D9%87%D8%A7%D9%86"
        self.__session:Client = session
        self.headers = {

                        "X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0"
                    }
        self.request_data = {
                        "dfh": "9def4c47bff842ebd0aeabba0f9c5502"
                    }



    def scrape(self) -> dict:

        # Make the POST request
        response = session.post(self.__baseUrl, headers=self.headers, data=self.request_data)
        response.raise_for_status() # Raise an error if request fails

        # Parse the JSON
        data = response.json()
        news_list = data.get("list", [])

        return news_list


    def parse(self,news_list) -> List[Dict[str,Any]] :

        # Parse all news items
        all_news = []
        for news in news_list:
            # parsed_news = {
            #     "id": news.get("id"),
            #     "title": news.get("title"),
            #     "excerpt": news.get("excerpt"),
            #     "content": news.get("content"),
            #     "slug": news.get("name"),
            #     "likes": news.get("like_count"),
            #     "dislikes": news.get("dislike_count"),
            #     "comments": news.get("comment_count"),
            #     "published_at": format_timestamp(news.get("publish_at")),
            #     "thumbnail": "https://caffecinema.com" + news.get("thumbnail") if news.get("thumbnail") else None,
            #     "categories": [cat.get("name") for cat in news.get("category", [])]
            # }

            formated:dict = {
                "title":news.get("title"), 
                "type":"", 
                "description": news.get("content"), 
                "year":format_timestamp(news.get("publish_at")), 
                "duration":"", 
                "imdb":"", 
                "persian":"", 
                "image":"https://caffecinema.com" + news.get("thumbnail") if news.get("thumbnail") else None, 
                "cover":"https://caffecinema.com" + news.get("thumbnail") if news.get("thumbnail") else None, 
                "trailer":{}, 
                "genres":[{}], 
                "countries":[{}], 
                "actors":[{}], 


            }
            all_news.append(formated)

        return all_news


class ScraperContianer:
    def __init__(self):
        self.scraper_map : dict= {
            "zoomg":ZoomgScraper,
            "gamefa":GameFaScraper,
            "caffecinema":CaffeCinemaScraper,
            "fromcinema":FromCinemaScraper,
            "moviemag":MoviemagScraper
        }

    def resolve(self,website:str,session) -> Scraper:
        scraper = self.scraper_map.get(website)
        if scraper:
            return scraper(session) 
        raise ValueError("site not supported ")




def extract_data(scraper:Scraper,**kwargs):
    return scraper.scrape()


def parser_data(scraper:Scraper,data):
    return scraper.parse(data)




if __name__ == "__main__":

    session = Client()
    contianer = ScraperContianer()


    for site in contianer.scraper_map.keys():
        print(f"Fetch Data From {site} ")
        scraper = contianer.resolve(site,session=session)
        data = extract_data(scraper)
        parsed_data_list = parser_data(scraper,data)

        with open(f"scraper/json/{site}_data.json",'w',encoding="utf-8") as f:
            json.dump(parsed_data_list,f,indent=4,ensure_ascii=False)
        print("Write Finished")
        