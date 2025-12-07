import json
from typing import List
from .base import Button,Layout
from telegram import (
    Update,
    CallbackQuery,
    InlineKeyboardMarkup,

)

class AdminLayout(Layout):  

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
        self.__add_buttons([Button("A",{'class':"A"}),Button("B",{'class':"B"})])
        return None
    
    def render(self):
        self.__render_defaults()
        return InlineKeyboardMarkup(self.layout)

