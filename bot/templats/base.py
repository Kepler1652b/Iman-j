import json
from typing import List
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,

)


class Button:
    def __init__(self,text:str,callback_data):
        self.text = text
        self.callback_data = json.dumps(callback_data)

    def render(self):
        return InlineKeyboardButton(text=self.text,callback_data=self.callback_data)
    
    def __repr__(self):
        return f"Button({self.text}-{self.callback_data})"



class Layout:

    def __init__(self):
        self.layout:List[Button] = []
        self.keyboard:List[List[Button]] = []

    def add_one_line_button(self,text:str,callback_data:dict):
        button = Button(text,callback_data).render()
        self.layout.append([button])


    def __add_buttons(self,buttons:List[Button]):
        row = []
        for button in buttons:
            button = Button(button.text,callback_data=button.callback_data).render()
            row.append(button)
        self.layout.append(row)

    def __render_defaults(self):
        return None
    
    def render(self):
        self.__render_defaults()
        return InlineKeyboardMarkup(self.layout)
    


