from datetime import datetime
from database.db import engine,PostCRUD
from database.models import PostBase

from sqlmodel import Session
import datetime
from persian_nlp_tools.persian_text_summarizer import TextSummarizationPipeline 


# Function to convert Unix timestamp to readable format
def format_timestamp(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts
    
def write_post_list(detials):
    with Session(engine) as session:
        for d in detials:
                    if isinstance(d,str):
                        continue
                    if d.get("content") == None:
                         continue
                    TextSummarization = TextSummarizationPipeline(d.get("content"),0.3,3)
                    summary = TextSummarization.process_and_summarize()
                    if not summary:
                         continue
                    post = PostBase(

                        title=d.get("title"),type_='N/A',summary=summary,
                        schedule=datetime.datetime.now(),image=d.get("image"),trailer='N/A',use_trailer=False,
                        link=d.get("link")
                                    
                        )
                    PostCRUD.create(session,post)
