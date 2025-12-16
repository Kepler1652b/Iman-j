from database.db import engine,create_db,PostCRUD
from database.models import PostBase
from httpx import Client
from scraper.scraper import ScraperContianer,extract_data,parser_data
from sqlmodel import Session
import datetime
from persian_nlp_tools.persian_text_summarizer import TextSummarizationPipeline 





def write_post_list(detials):
    with Session(engine) as session:
        for d in detials:
                    if isinstance(d,str):
                        continue
                    if d.get("content") == None:
                         continue
                    TextSummarization = TextSummarizationPipeline(d.get("content"),0.3,3)
                    summary = TextSummarization.process_and_summarize()
                    post = PostBase(

                        title=d.get("title"),type_='N/A',summary=summary,
                        schedule=datetime.datetime.now(),image=d.get("image"),trailer='N/A',use_trailer=False,
                        link=d.get("link")
                                    
                        )
                    PostCRUD.create(session,post)

from bot.bot import run
import uvicorn
import threading
import time
if __name__ == "__main__":
        # bot_thread = threading.Thread(target=run, daemon=True)
        # bot_thread.start()
        # time.sleep(3)
        # uvicorn.run("api.app:app", host="0.0.0.0", port=8000,workers=1)
    run()
    # make_post()
 
 
 
        









