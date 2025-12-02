from sqlmodel import SQLModel,Field
from datetime import datetime
# from typing import Dict,Any,List

class UserBase(SQLModel):
    username:str | None
    telegram__id : int = Field(max_digits=10,index=True)
    is_active : bool = Field(default=False)
    is_admin: bool = Field(default=False)
    is_superadmin: bool = Field(default=False)
    created_at:str = Field(default_factory=datetime.now)

    # group:


class User(UserBase,table=True):
    id: int | None = Field(default=None,primary_key=True)


class GenreBase(SQLModel):
    title : str = Field(index=True)


class Genre(GenreBase, table=True):
    id : int | None = Field(default=None, primary_key=True)


class CountryBase(SQLModel):
    title: str
    image_url:str


class Country(CountryBase, table=True):
    id : int | None = Field(default=None, primary_key=True)


class ActorBase(SQLModel):
    name:str
    image_url:str


class Actor(ActorBase, table=True):
    id : int | None = Field(default=None, primary_key=True)
    # movie:


class TrailerBase(SQLModel):
    type_:str 
    url:str


class Trailer(TrailerBase, table=True):
    id : int | None = Field(default=None, primary_key=True)


class MovieBase(SQLModel):
    title : str = Field(index=True)
    type_ : str
    description : str
    year : str
    duration : int
    imdb : float
    is_persian : bool
    image_url : str
    cover_url : str

    trailer_id : int | None = Field(default=None,primary_key="trailer.id")
    # genres : List[Genre] = Field()
    # countries : List[Country] = Field()
    # actors : List[Actor] = Field()

class Movie(MovieBase, table=True):
    id : int | None = Field(default=None, primary_key=True)

