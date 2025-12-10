from fastapi import APIRouter
from database.db import MovieCRUD,GenreCRUD,ActorCRUD,CountryCRUD,engine
from pydantic import BaseModel
from database.models import MovieBase,TrailerBase, GenreBase,ActorBase,CountryBase
from typing import Dict , List,Any
from sqlmodel import Session

router  = APIRouter(prefix='/v1')

class Movie(BaseModel):
    """Movie Base Model for table Movie"""
    title: str 
    type: str 
    description: str 
    duration: str
    year:int
    imdb: float
    persian: bool
    image: str
    cover: str 
    trailer: Dict[str,Any]
    genres: List[Dict[str,Any]] 
    countries: List[Dict[str,Any]] 
    actors: List[Dict[str,Any]]




@router.post('/movie')
async def create(movie_json:Movie):
    movie = MovieBase(
        title=movie_json.title,type_=movie_json.type,
        description=movie_json.description,
        year=movie_json.year,
        duration=movie_json.duration,
        imdb=movie_json.imdb,
        is_persian=movie_json.persian,
        image_url=movie_json.image,
        cover_url=movie_json.cover,
        )

    with Session(engine) as session:

        movieObj= MovieCRUD.get_by_title(session,movie_json.title)
        if movieObj.data == None:
            movie = MovieCRUD.create(session,movie)

            for genre in movie_json.genres:
                    title = genre.get("title")
                    genre = GenreCRUD.get_by_title(session,title)
                    if genre.data == None:
                        genre_c = GenreBase(title=title)
                        GenreCRUD.create(session,genre_c)
                    MovieCRUD.add_genre(session,movie_id=movie.data.id,genre_id=genre.data.id)

        
            for actor in movie_json.actors:
                    name = actor.get("name")
                    image = actor.get("image")
                    actor = ActorCRUD.get_by_name(session,name)

                    if actor.data == None:
                        actor_c = ActorBase(name=name,image_url=image)
                        ActorCRUD.create(session,actor_c)

                    MovieCRUD.add_actor(session,movie_id=movie.data.id,actor_id=actor.data.id)


            for country in movie_json.countries:
                    title = country.get("title")
                    image = country.get("image")
                    country = CountryCRUD.get_by_title(session,title=title)

                    if country.data == None:
                        country_c = CountryBase(title=title,image_url=image)
                        CountryCRUD.create(session,country_c)

                    MovieCRUD.add_country(session,movie_id=movie.data.id,country_id=country.data.id)


            return {f"Created : {movie_json} "}
        
        return {f"This movie {movieObj.data.title}":"already exist"}