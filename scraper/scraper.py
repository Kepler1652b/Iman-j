import feedparser

from typing import Any, Protocol,Dict,List
from httpx import Client
from bs4 import BeautifulSoup
from .scraper_utilities import format_timestamp





class Scraper(Protocol):
    """
    Main Protocol class for Scrapers 

    """


    def scrape(self) -> dict | List[Dict[str,Any]]:
        pass

    def parse(self,data) -> List[Dict[str,Any]]:
        pass

    def detail_parser(self,data) -> List[Dict[str,Any]]:
        pass


class ZoomgScraper:

    def __init__(self,session):
        self.__baseUrl = "https://api2.zoomg.ir/editorial/api/articles/browse?sort=Newest&publishDate=All&readingTime=All&pageNumber=1&PageSize=20"
        self.__session:Client = session
        self.__headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                "Accept-Language":"en-US,en;q=0.5",
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                # "Cookie":"_pk_ref.2.01fe=%5B%22%22%2C%22%22%2C1764827723%2C%22https%3A%2F%2Fwww.karlancer.com%2F%22%5D; _pk_id.2.01fe=4b60e94eaab94e4f.1762239023.; bob_anonymous_id=4c1d7b43-b5cf-4216-afd6-e0e074c0f0b1; _ga_BX3DD5ZERM=GS2.1.s1764827726$o2$g1$t1764828266$j51$l0$h286395348; _ga=GA1.1.1560322300.1762239025; analytics_campaign={%22source%22:%22karlancer.com%22%2C%22medium%22:%22referral%22}; analytics_token=1fa1eb7d-c2e8-7e3d-ee8e-2a69ad3cd68a; _yngt=01K96T34A7YSZHFJ9M6B0VKZGH; _yngt_iframe=1; _z_sess=176c3ae3-39d3-4574-83f3-14c67a696b02; _pk_ses.2.01fe=1; analytics_session_token=d7fa997a-778b-daaa-4724-39d312fd4a7a; yektanet_session_last_activity=12/4/2025"
            }

    def scrape(self,max_movie:int = 20) -> dict:
        response = self.__session.get(self.__baseUrl)
        # print(response.json())
        return response.json()


    def parse(self,data) -> dict:
        soup = BeautifulSoup(data,"html.parser")
        news_list = soup.select_one("div.px-4").find_all("div",attrs={"class":"scroll-m-16"})
        print(news_list)


class MoviemagScraper:

    def __init__(self,session):
        self.__baseUrl = "https://moviemag.ir/category/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1-%d8%b3%db%8c%d9%86%d9%85%d8%a7%db%8c-%d8%ac%d9%87%d8%a7%d9%86/"
        self.__RSS_URL = "https://moviemag.ir/category/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1-%d8%b3%db%8c%d9%86%d9%85%d8%a7%db%8c-%d8%ac%d9%87%d8%a7%d9%86/feed/"
        self.__session:Client = session


    def scrape(self) -> dict:
        try:
            feed = feedparser.parse(self.__RSS_URL)
            return feed
        except Exception as e:
            return None

    def parse(self,feed:dict ) ->  List[Dict[str,Any]]:
        if feed:
            data = []
            for entry in feed.entries:
                formated:dict = {
                    "title":entry.get("title", "N/A"), 
                    "type":"N/A", 
                    "content":"N/A",
                    "year":entry.get("published", entry.get("updated", "N/A")), 
                    "image":"N/A", 
                    'link':entry.get("link", "N/A"),
                }

                data.append(formated)

            return data
        return None
    

    def detail_parser(self,data:list):
        content = ''
        data_list = []
        for post in data:
            link = post.get("link",None)
            if link:
                try:
                    response = self.__session.get(link)
                    soup = BeautifulSoup(response.text,'html.parser')

                    text_list = soup.select_one(".elementor-element-f41c1d8 > div:nth-child(1)").find_all("p")
                    image_url = soup.select_one(".harika-featuredimage-widget").find('img').attrs.get("data-lazy-src")
                    
                    if text_list:
                        for p in text_list:
                            content += p.text
                    else:
                        content = 'N/A'

                    if image_url:
                        post['image'] = image_url
                    else:
                        post['image'] = "N/A"

                    post["content"] = content
                    

                    data_list.append(post)
                    content = ''

                except Exception as e:
                    print(f"logger  [class name] [time] [news title] : {e}")
            else:
                print("logger [class name] [time] [news title] : No link available")

        return data_list


class GameFaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://gamefa.com/category/cinema/"
        self.__session:Client = session

    def scrape(self) -> str:
        try:
            response = self.__session.get(self.__baseUrl)
            return response.text
        except Exception as e:
            return None

    def parse(self,html) ->  List[Dict[str,Any]] | None:
        if html:
            data = []
            soup = BeautifulSoup(html, "html.parser")

            card_list = soup.select_one(".posts-list > div:nth-child(1)").find_all("div",attrs={'class':"col-12"})

            if card_list:
                for master_card in card_list:
                    # Category
                    card = master_card.find("div", class_="row align-items-center")

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
                    

                    link_tag = master_card.find("a")
                    link = link_tag.attrs.get("href") if link_tag else "N/A"
                    
                    if category_text == "اخبار سینما":
                        formated:dict = {
                            "title":title_text, 
                            "type":"N/A", 
                            "content":"N/A", 
                            "year":time_text, 
                            "image":img_src, 
                            "link":link, 

                        }
                    else:
                        continue
                    data.append(formated)

                return data
            else:
                print("logger  [class name] [time] [news title] : No News Found")
        else:
            return None
        

    def detail_parser(self,data) -> List[Dict[str,Any]] | None:
        if data:
            content = ''
            data_list = []
            for post in data:
                link = post.get("link",None)
                if link:
                    try:
                        response = self.__session.get(link)

                        soup = BeautifulSoup(response.text,'html.parser')
                        text_list = soup.select_one(".post-content").find_all("p")
                        if text_list:
                            for p in text_list:
                                content += p.text
                        else:
                            content = 'N/A'
                        post["content"] = content
                        data_list.append(post)
                        content = ''

                    except Exception as e:
                        print(f"logger  [class name] [time] [news title] : HTTP error {e}")
                else:
                    print("logger  [class name] [time] [news title] : No link available")
            return data_list
        
        return None
        

class FromCinemaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://www.fromcinema.com/cinema-news/"
        self.__session:Client = session
        self.__section = (".elementor-element-ce54b4c > div:nth-child(1) > div:nth-child(1)",".elementor-element-e6930cd > div:nth-child(1) > div:nth-child(1)")
    
    
    def scrape(self) ->  List[Dict[str,Any]]:
        try:
            data = self.__session.get(self.__baseUrl)
            soup = BeautifulSoup(data.text,"html.parser")
            articel_soup = soup.select_one(self.__section[0])
            articel_list = articel_soup.find_all("article")
            return articel_list
        except Exception as e:
            print(f"logger  [class name] [time] [news title] : Http error {e}")


    def parse(self, article_list:list):
            if article_list:
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

                    formated:dict = {
                            "title":title, 
                            "type":"N/A", 
                            "content":description, 
                            "year":date, 
                            "image":image_url, 
                            "link":read_more_url, 
                        }
                    
                    data.append(formated)

                return data
            return None
    

    def detail_parser(self,data):
        if data:
            content = ''
            data_list = []
            for post in data:
                link = post.get("link",None)

                if link:
                    try:
                        response = self.__session.get(link)

                        soup = BeautifulSoup(response.text,'html.parser')
                        text_list = soup.find_all("p")
                        if text_list:
                            for p in text_list:
                                content += p.text

                        post["content"] = content
                        data_list.append(post)
                        content = ''
                    except Exception as e:
                        print(f'logger  [class name] [time] [news title] : Http error {e}')
                else:
                    print("logger  [class name] [time] [news title] : No link available")
            return data_list
                
        else:
            return None


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
        try:
            # Make the POST request
            response = self.__session.post(self.__baseUrl, headers=self.headers, data=self.request_data)


            # Parse the JSON
            data = response.json()
            news_list = data.get("list", [])
            return news_list
        
        except Exception as e :
            return None


    def parse(self,news_list) -> List[Dict[str,Any]] :
        if news_list:

            # Parse all news items
            all_news = []
            for news in news_list:
                content_soup = BeautifulSoup(news.get("content"),'html.parser')
                content = content_soup.text
                formated:dict = {
                    "title":news.get("title",None), 
                    "type":"", 
                    "content": content if content else None, 
                    "year":format_timestamp(news.get("publish_at")), 
                    "image":"https://caffecinema.com" + news.get("thumbnail") if news.get("thumbnail") else None, 
                    "link":"https://caffecinema.com/" + news.get("name") if news.get("name") else None,
                }
                all_news.append(formated)

            return all_news
        else:
            print("logger :No data availble ")
            return None

    def detail_parser(self,data):
        return data if data else None


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



# Use Scraper protocol for interface and run scrape method 
def extract_data(scraper:Scraper):
    return scraper.scrape()

# Use Scraper protocol for interface and run parse method 
def parser_data(scraper:Scraper,data):
    return scraper.parse(data)










        