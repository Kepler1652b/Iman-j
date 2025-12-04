from scraper import ScraperContianer,extract_data,parser_data
from httpx import Client
import json


class MoviemagConverter:
    def __init__(self):
        self.container = ScraperContianer()
        self.session = Client()
        self.scraper = self.container.resolve("moviemag",self.session)

    def get_data(self):
        return extract_data(self.scraper)
    
    def paser(self):
        return parser_data(self.scraper,self.get_data())
    
    def convert(self):
        movie_list = self.paser()
        converted_data_list = []
        for m in movie_list:
            formated:dict = {
                "title":m.get("Title"), 
                "type":"", 
                "description":m.get("Summary/Description:"), 
                "year":m.get("Published"), 
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
                        
            print(formated)





if __name__ == "__main__":
    converter = MoviemagConverter()
    converter.convert()