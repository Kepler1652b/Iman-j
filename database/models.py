"""
This Modul Contains DataBase Models and tables 
Do not change anything 
"""



from typing import List, Optional
from sqlmodel import SQLModel,Field,Relationship
from datetime import datetime


class UserBase(SQLModel):
    """
    Base User Data model for User table 

    """

    username:str | None # telegram username
    telegram_id : int = Field(index=True) # telegram chat id 
    is_active : bool = Field(default=False)
    is_admin: bool = Field(default=False)
    is_superadmin: bool = Field(default=False)
    created_at:datetime = Field(default_factory=datetime.now)

class User(UserBase,table=True):
    id: int | None = Field(default=None,primary_key=True)


# Link Tables for Many-to-Many relationships
class MovieGenreLink(SQLModel, table=True):
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)

class MovieCountryLink(SQLModel, table=True):
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id", primary_key=True)
    country_id: Optional[int] = Field(default=None, foreign_key="country.id", primary_key=True)

class MovieActorLink(SQLModel, table=True):
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id", primary_key=True)
    actor_id: Optional[int] = Field(default=None, foreign_key="actor.id", primary_key=True)




class GenreBase(SQLModel):
    """
    Genra Base model for Genre table
    """
    title: str = Field(index=True)


class Genre(GenreBase, table=True):
    """
    Genre table with movies attr refere to List of Movie's
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    movies: List["Movie"] = Relationship(back_populates="genres", link_model=MovieGenreLink)


class CountryBase(SQLModel):
    """
    Country Base Model for Country Table
    """
    title: str
    image_url: str


class Country(CountryBase, table=True):
    """
    Country table with movies attr refere to List of Movie's
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    movies: List["Movie"] = Relationship(back_populates="countries", link_model=MovieCountryLink)


class ActorBase(SQLModel):
    """
    Actor Base Model for Actor Table
    """
    name: str
    image_url: str


class Actor(ActorBase, table=True):
    """
    Actor table with movies attr refere to List of Movie's
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    movies: List["Movie"] = Relationship(back_populates="actors", link_model=MovieActorLink)


class TrailerBase(SQLModel):
    """
    Trailer Base Model for Trailer table
    """
    type_: str 
    url: str


class Trailer(TrailerBase, table=True):
    """
    Trailer table with movie attr refere Movie and id to movie row
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id")
    movie: Optional["Movie"] = Relationship(back_populates="trailers")


class MovieBase(SQLModel):
    """
    Movie Base Model for table Movie
    """
    title: str = Field(index=True)
    type_: str
    description: str
    year: str
    duration: int
    imdb: float
    is_persian: bool
    image_url: str
    cover_url: str


class Movie(MovieBase, table=True):
    """
    Movie Table with trailers,genres,countries and actors list 
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    
    trailers: List[Trailer] = Relationship(back_populates="movie")  
    genres: List[Genre] = Relationship(back_populates="movies", link_model=MovieGenreLink)
    countries: List[Country] = Relationship(back_populates="movies", link_model=MovieCountryLink)
    actors: List[Actor] = Relationship(back_populates="movies", link_model=MovieActorLink)




