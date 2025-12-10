"""
This Module Contains Database Models and tables 
Fixed version with all issues resolved
"""
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, String
from datetime import datetime
from pydantic import field_validator


# ============= USER MODEL =============

class UserBase(SQLModel):
    """Base User Data model for User table"""
    username: Optional[str] = Field(default=None, unique=True, max_length=100) 
    telegram_id: int = Field(unique=True, index=True)
    is_active: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    is_superadmin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) 


# ============= LINK TABLES =============

class MovieGenreLink(SQLModel, table=True):
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)


class MovieCountryLink(SQLModel, table=True):
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id", primary_key=True)
    country_id: Optional[int] = Field(default=None, foreign_key="country.id", primary_key=True)


class MovieActorLink(SQLModel, table=True):
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id", primary_key=True)
    actor_id: Optional[int] = Field(default=None, foreign_key="actor.id", primary_key=True)


class SerialGenreLink(SQLModel, table=True):
    serial_id: Optional[int] = Field(default=None, foreign_key="serial.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)


class SerialCountryLink(SQLModel, table=True):
    serial_id: Optional[int] = Field(default=None, foreign_key="serial.id", primary_key=True)
    country_id: Optional[int] = Field(default=None, foreign_key="country.id", primary_key=True)


class SerialActorLink(SQLModel, table=True):
    serial_id: Optional[int] = Field(default=None, foreign_key="serial.id", primary_key=True)
    actor_id: Optional[int] = Field(default=None, foreign_key="actor.id", primary_key=True)


# ============= GENRE MODEL =============

class GenreBase(SQLModel):
    """Genre Base model for Genre table"""
    title: str = Field(index=True, unique=True, max_length=100)


class Genre(GenreBase, table=True):
    """Genre table with movies and serials relationships"""
    id: Optional[int] = Field(default=None, primary_key=True)
    movies: List["Movie"] = Relationship(back_populates="genres", link_model=MovieGenreLink)
    serials: List["Serial"] = Relationship(back_populates="genres", link_model=SerialGenreLink)


# ============= COUNTRY MODEL =============

class CountryBase(SQLModel):
    """Country Base Model for Country Table"""
    title: str = Field(unique=True, max_length=100)
    image_url: str = Field(max_length=500)


class Country(CountryBase, table=True):
    """Country table with movies and serials relationships"""
    id: Optional[int] = Field(default=None, primary_key=True)
    movies: List["Movie"] = Relationship(back_populates="countries", link_model=MovieCountryLink)
    serials: List["Serial"] = Relationship(back_populates="countries", link_model=SerialCountryLink)


# ============= ACTOR MODEL =============

class ActorBase(SQLModel):
    """Actor Base Model for Actor Table"""
    name: str = Field(unique=True, max_length=200)
    image_url: str = Field(max_length=500)


class Actor(ActorBase, table=True):
    """Actor table with movies and serials relationships"""
    id: Optional[int] = Field(default=None, primary_key=True)
    movies: List["Movie"] = Relationship(back_populates="actors", link_model=MovieActorLink)
    serials: List["Serial"] = Relationship(back_populates="actors", link_model=SerialActorLink)


# ============= TRAILER MODEL =============

class TrailerBase(SQLModel):
    """Trailer Base Model for Trailer table"""
    type_: str = Field(max_length=50)
    url: str = Field(max_length=500)


class Trailer(TrailerBase, table=True):
    """Trailer table for movies and serials"""
    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: Optional[int] = Field(default=None, foreign_key="movie.id")
    serial_id: Optional[int] = Field(default=None, foreign_key="serial.id")
    movie: Optional["Movie"] = Relationship(back_populates="trailers")
    serial: Optional["Serial"] = Relationship(back_populates="trailers")


# ============= MOVIE MODEL =============

class MovieBase(SQLModel):
    """Movie Base Model for table Movie"""
    title: str = Field(index=True, max_length=300)
    type_: str = Field(default="movie", max_length=50)
    description: str = Field(sa_column=Column(Text)) 
    year: str = Field(max_length=10)
    duration: int
    imdb: float
    is_persian: bool
    image_url: str = Field(max_length=500)
    cover_url: str = Field(max_length=500)
    sent: bool = Field(default=False)


class Movie(MovieBase, table=True):
    """Movie Table with trailers, genres, countries and actors list"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    trailers: List[Trailer] = Relationship(back_populates="movie")
    genres: List[Genre] = Relationship(back_populates="movies", link_model=MovieGenreLink)
    countries: List[Country] = Relationship(back_populates="movies", link_model=MovieCountryLink)
    actors: List[Actor] = Relationship(back_populates="movies", link_model=MovieActorLink)


# ============= SEASON MODEL =============

class SeasonBase(SQLModel):
    """Season Base Model"""
    title: str = Field(max_length=200)
    season_number: int 


class Season(SeasonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial_id: int = Field(foreign_key="serial.id")  
    serial: "Serial" = Relationship(back_populates="seasons")
    episodes: List["Episode"] = Relationship(back_populates="season_obj")


# ============= SERIAL MODEL =============

class SerialBase(SQLModel):
    """Serial Base Model for table Serial"""
    title: str = Field(index=True, max_length=300)
    type_: str = Field(default='serie', max_length=50)
    description: str = Field(sa_column=Column(Text))
    year: str = Field(max_length=10)
    duration: int  # Duration per episode
    imdb: float
    is_persian: bool
    image_url: str = Field(max_length=500)
    cover_url: str = Field(max_length=500)
    sent: bool = Field(default=False)
    season_count: int


class Serial(SerialBase, table=True):
    """Serial Table with trailers, genres, countries, actors and seasons"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    trailers: List[Trailer] = Relationship(back_populates="serial")
    genres: List[Genre] = Relationship(back_populates="serials", link_model=SerialGenreLink)
    countries: List[Country] = Relationship(back_populates="serials", link_model=SerialCountryLink)
    actors: List[Actor] = Relationship(back_populates="serials", link_model=SerialActorLink)
    seasons: List[Season] = Relationship(back_populates="serial")
    episodes: List["Episode"] = Relationship(back_populates="serial")


# ============= SERIAL EPISODE MODEL =============

class EpisodeBase(SQLModel):
    """Serial Episode Base Model"""
    title: str = Field(index=True, max_length=300)
    description: str = Field(sa_column=Column(Text))
    duration: int
    episode_number: int
    season_id: Optional[int] = Field(default=None, foreign_key="season.id")
    serial_id: Optional[int] = Field(default=None, foreign_key="serial.id")
    sent: bool = Field(default=False)


class Episode(EpisodeBase, table=True):
    """Serial Episode Table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    season_obj: Optional[Season] = Relationship(back_populates="episodes")
    serial: Optional[Serial] = Relationship(back_populates="episodes")


# ============= POST MODEL =============

class PostBase(SQLModel):
    """Post Base Model"""
    title: str = Field(unique=True, max_length=300)
    type_: str = Field(max_length=50)
    summary: str 
    schedule: Optional[datetime] = Field(default=None)
    image: str = Field(max_length=500)
    link: Optional[str] = Field(default=None, max_length=500) 
    sent: bool = Field(default=False)


class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

