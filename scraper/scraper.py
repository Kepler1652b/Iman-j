from typing import Protocol
from httpx import Client
from data_parser import Parser
from bs4 import BeautifulSoup
import json


class Scraper(Protocol):
    """
    Main Protocol class for Scrapers 

    """

    def scrape(self,max_movie:int = 20) -> None:
        pass

    def parse(self) -> dict:
        pass


class ZoomgScraper:

    def __init__(self,session):
        self.__baseUrl = "https://www.zoomg.ir/cinema/"
        self.__session:Client = session

    def scrape(self,max_movie:int = 20) -> dict:
        return "zoomg - scraper"

    def parse(self,parser:Parser) -> dict:
        pass



class MoviemagScraper:

    def __init__(self,session):
        self.__baseUrl = "https://moviemag.ir/category/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1-%d8%b3%db%8c%d9%86%d9%85%d8%a7%db%8c-%d8%ac%d9%87%d8%a7%d9%86/"
        self.__session:Client = session

    def scrape(self,max_movie:int = 20) -> dict:
        return "moviemag - scraper"

    def parse(self,parser:Parser) -> dict:
        pass



class GameFaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://gamefa.com/"
        self.__session:Client = session

    def scrape(self,max_movie:int = 20) -> dict:
        return "gamefa - scraper"

    def parse(self,parser:Parser) -> dict:
        pass




class FromCinemaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://www.fromcinema.com/cinema-news/"
        self.__session:Client = session
        self.__parsed_data:dict = {}
        self.__section = (".elementor-element-ce54b4c > div:nth-child(1) > div:nth-child(1)",".elementor-element-e6930cd > div:nth-child(1) > div:nth-child(1)")
    
    
    def scrape(self,max_movie:int = 20) -> dict:
        
        data = self.__session.get(self.__baseUrl)
        self.__session.close()
        soup = BeautifulSoup(data.text,"html.parser")
        articel_soup = soup.select_one(self.__section[0])
        articel_list = articel_soup.find_all("article")
        

        return articel_list


    def parse(self,articel_list) -> dict:

        movie_counter = 1
        for articel in articel_list:
            title:str = articel.find("h3",attrs={"class":"elementor-post__title"}).text
            description:str  = articel.find("p").text
            author:str = articel.find("span",attrs={"class":"elementor-post-author"}).text
            date:str = articel.find("span",attrs={"class":"elementor-post-date"}).text
            time:str = articel.find("span",attrs={"class":"elementor-post-time"}).text
            try:
                image_url = articel.find("img").attrs.get("src")
            except Exception:
                image_url = "Null"

            self.__parsed_data.setdefault(f"Movie{movie_counter}",{})
            self.__parsed_data[f"Movie{movie_counter}"]["title"] = title.strip()
            self.__parsed_data[f"Movie{movie_counter}"]["description"] = description.strip()
            self.__parsed_data[f"Movie{movie_counter}"]["author"] = author.strip()
            self.__parsed_data[f"Movie{movie_counter}"]["date"] = date.strip()
            self.__parsed_data[f"Movie{movie_counter}"]["time"] = time.strip()
            self.__parsed_data[f"Movie{movie_counter}"]["image_url"] = image_url.strip()

            movie_counter += 1

        return self.__parsed_data
        

class CaffeCinemaScraper:

    def __init__(self,session):
        self.__baseUrl = "https://caffecinema.com/category/%D8%B3%DB%8C%D9%86%D9%85%D8%A7%DB%8C-%D8%AC%D9%87%D8%A7%D9%86"
        self.__session:Client = session

    def scrape(self,max_movie:int = 20) -> dict:
        return "caffecinema - scraper"

    def parse(self,parser:Parser) -> dict:
        pass


class ScraperContianer:
    def __init__(self):
        self.__scraper_map : dict= {
            "zoomg":ZoomgScraper,
            "gamefa":GameFaScraper,
            "caffecinema":CaffeCinemaScraper,
            "fromcinema":FromCinemaScraper,
            "moviemag":MoviemagScraper
        }

    def resolve(self,website:str,session) -> Scraper:
        scraper = self.__scraper_map.get(website)
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
    scraper = contianer.resolve("fromcinema",session=session)
    data = extract_data(scraper)

    with open("data.json",'w',encoding="utf-8") as f:
        json.dump(parser_data(scraper,data),f,indent=4,ensure_ascii=False)
    