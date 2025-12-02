from sqlmodel import create_engine,select,SQLModel
from models import *


engine = create_engine("sqlite:///database.db")



def create_db(engine):
    SQLModel.metadata.create_all(engine)


create_db(engine)