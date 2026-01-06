from datetime import datetime
from database.db import engine,PostCRUD
from database.models import PostBase

from sqlmodel import Session
import datetime
from persian_nlp_tools.persian_text_summarizer import TextSummarizationPipeline 

import re

class PersianTextNormalizer:
    def __init__(self):
        # Common Persian word patterns that get joined
        self.word_patterns = {
            'جهاننام': 'جهان نام',
            'سینمایجهان': 'سینمای جهان',
            'فیلمنامه': 'فیلم نامه',
            'کارگردان': 'کارگردان',  # This is actually one word
            # Add more patterns as you discover them
        }
    
    def normalize(self, text: str) -> str:
        """Normalize Persian text without external libraries"""
        if not text or text in ["N/A", "Null"]:
            return text
        
        # Step 1: Replace known problematic patterns
        for wrong, correct in self.word_patterns.items():
            text = text.replace(wrong, correct)
        
        # Step 2: Add space between Persian and English/numbers
        # Persian/Arabic Unicode range: \u0600-\u06FF
        text = re.sub(r'([\u0600-\u06FF]+)([a-zA-Z0-9])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z0-9])([\u0600-\u06FF]+)', r'\1 \2', text)
        
        # Step 3: Normalize common Persian characters
        text = self._normalize_persian_chars(text)
        
        # Step 4: Clean up whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = text.strip()
        
        # Step 5: Remove zero-width characters that cause issues
        text = text.replace('\u200c', ' ')  # Zero-width non-joiner
        text = text.replace('\u200d', '')   # Zero-width joiner
        text = text.replace('\u200b', '')   # Zero-width space
        
        return text
    
    def _normalize_persian_chars(self, text: str) -> str:
        """Normalize Persian character variations"""
        # Arabic ك to Persian ک
        text = text.replace('\u0643', '\u06a9')
        # Arabic ي to Persian ی
        text = text.replace('\u0649', '\u06cc')
        text = text.replace('\u064a', '\u06cc')
        # Normalize Yeh with hamza
        text = text.replace('\u0626', '\u06cc')
        
        return text
    
    def normalize_dict(self, data: dict) -> dict:
        """Normalize all string fields in a dictionary"""
        normalized = {}
        for key, value in data.items():
            if isinstance(value, str):
                normalized[key] = self.normalize(value)
            else:
                normalized[key] = value
        return normalized
    

# Function to convert Unix timestamp to readable format
def format_timestamp(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts
norm = PersianTextNormalizer()
def write_post_list(detials):
    
    with Session(engine) as session:
        for d in detials:
                    if isinstance(d,str):
                        continue
                    if d.get("content") == None:
                         continue

                    summary = norm.normalize(d.get("content"))
                    TextSummarization = TextSummarizationPipeline(summary,0.3,3)
                    summary = TextSummarization.process_and_summarize()
                    if not summary:
                         continue


                    post = PostBase(

                        title=d.get("title"),type_='N/A',summary=summary,
                        schedule=datetime.datetime.now(),image=d.get("image"),trailer='N/A',use_trailer=False,
                        link=d.get("link")
                                    
                        )
                    PostCRUD.create(session,post)
