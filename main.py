from database.db import engine,create_db,PostCRUD
from database.models import PostBase
from httpx import Client
from scraper.scraper import ScraperContianer,extract_data,parser_data
from sqlmodel import Session
# from bot.bot import run



# def write_news_list(detials):
#     with Session(engine) as session:
#         for d in detials:
#                     if isinstance(d,str):
#                         continue
#                     news = NewsBase(

#                         title=d.get("title"),type_=d.get("type"),content=d.get("content"),
#                         year=d.get("year"),image=d.get('image'),link=d.get("link")
                                    
#                         )
#                     NewsCRUD.create(session,news)

# def make_post():
#     with Session(engine) as session:
#         for news in NewsCRUD.get_all(session=session):      
#                     post = PostBase(title=news.title,type_="movie",summery=news.content,schedule='',image=news.image,trailer=None,use_trailer=False)
#                     PostCRUD.create(session,post)
import datetime
from persian_nlp_tools.persian_text_summarizer import TextSummarizationPipeline 
def write_post_list(detials):
    with Session(engine) as session:
        for d in detials:
                    if isinstance(d,str):
                        continue
                    TextSummarization = TextSummarizationPipeline(d.get("content"),0.3,3)
                    summary = TextSummarization.process_and_summarize()
                    post = PostBase(

                        title=d.get("title"),type_='N/A',summery=summary,
                        schedule=datetime.datetime.now(),image=d.get("image"),trailer='N/A',use_trailer=False,
                        link=d.get("link")
                                    
                        )
                    PostCRUD.create(session,post)

import json
from bot.bot import run
if __name__ == "__main__":
    option = int(input("1(bot)\n2(scrape)\n"))
    if option == 1:
        run()
    elif option == 2:
        session = Client()
        contianer = ScraperContianer()
        create_db()
        for sc in contianer.scraper_map:
            scraper = contianer.resolve(sc,session=session)
            data = extract_data(scraper)
            parsed_data_list = parser_data(scraper,data)
            detials = scraper.detail_parser(parsed_data_list)
            # write_news_list(detials)    
            write_post_list(detials)


    # make_post()
 
 
 
        









# if __name__ == "__main__":
#     import json
#     session = Client()
#     contianer = ScraperContianer()



#     scraper = contianer.resolve("gamefa",session=session)
#     data = extract_data(scraper)


#     parsed_data_list = parser_data(scraper,data)
#     # print(json.dumps(parsed_data_list,indent=4,ensure_ascii=False))
#     detial = scraper.detail_parser(parsed_data_list)
#     with open("gamefa.json",'w',encoding='utf-8') as f:
#         json.dump(detial,f,indent=4,ensure_ascii=False)
