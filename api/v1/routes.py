from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict , List,Any
from sqlmodel import Session



from database.db import (
     MovieCRUD,GenreCRUD,
     ActorCRUD,CountryCRUD,
     TrailerCRUD,SerialCRUD,
     engine,EpisodeCRUD,
     SeasonCRUD

     )

from database.models import ( 
     MovieBase,TrailerBase, 
     GenreBase,ActorBase,
     CountryBase,
     SeasonBase,EpisodeBase,
     SerialBase

                             
)










router  = APIRouter(prefix='/v1')

class Movie(BaseModel):
    """Movie Base Model for table Movie"""
    title: str 
    id : int
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
        api_id=movie_json.id
        )

    with Session(engine) as session:

        movieObj= MovieCRUD.get_by_title(session,movie_json.title)

        if movieObj.data == None:
            movie = MovieCRUD.create(session,movie)
            session.refresh(movie.data)
            type_ = movie_json.trailer.get("type")
            url = movie_json.trailer.get("url")
            trailer = TrailerBase(type_=type_,url=url)
            TrailerCRUD.create(session,trailer,movie_id=movie.data.id)
            for genre in movie_json.genres:
                    title = genre.get("title")
                    genre = GenreCRUD.get_by_title(session,title)
                    
                    if genre.data == None:
                        genre_c = GenreBase(title=title)
                        genre = GenreCRUD.create(session,genre_c)
                        session.refresh(genre.data)
                        MovieCRUD.add_genre(session,movie_id=movie.data.id,genre_id=genre.data.id)
                    MovieCRUD.add_genre(session,movie_id=movie.data.id,genre_id=genre.data.id)
        
            for actor in movie_json.actors:
                    name = actor.get("name")
                    image = actor.get("image")
                    actor = ActorCRUD.get_by_name(session,name)

                    if actor.data == None:
                        actor_c = ActorBase(name=name,image_url=image)
                        actor = ActorCRUD.create(session,actor_c)
                        session.refresh(actor.data)
                        MovieCRUD.add_actor(session,movie_id=movie.data.id,actor_id=actor.data.id)
                    MovieCRUD.add_actor(session,movie_id=movie.data.id,actor_id=actor.data.id)

            for country in movie_json.countries:
                    title = country.get("title")
                    image = country.get("image")
                    country = CountryCRUD.get_by_title(session,title=title)

                    if country.data == None:
                        country_c = CountryBase(title=title,image_url=image)
                        country = CountryCRUD.create(session,country_c)
                        session.refresh(country.data)
                        MovieCRUD.add_country(session,movie_id=movie.data.id,country_id=country.data.id)
                    MovieCRUD.add_country(session,movie_id=movie.data.id,country_id=country.data.id)


            return {"Created":movie_json.title}
        
        return {f"This movie {movieObj.data.title}":"already exist"}
    


@router.patch('/movie/{api_id}')
async def update(api_id:int,movie_json:Movie):

    movie = MovieBase(
        title=movie_json.title,type_=movie_json.type,
        description=movie_json.description,
        year=movie_json.year,
        duration=movie_json.duration,
        imdb=movie_json.imdb,
        is_persian=movie_json.persian,
        image_url=movie_json.image,
        cover_url=movie_json.cover,
        api_id=movie_json.id
        )

    with Session(engine) as session:

        movieObj= MovieCRUD.get_by_api_id(session,api_id)
        if movieObj.data != None:
            movie = MovieCRUD.update(session,movieObj.data.id,movie.model_dump())
            return {f"This movie '{movieObj.data.title}'":"Updated "}
        return "No movie with this id"



@router.delete('/movie/{api_id}')
async def delete(api_id:int):
    with Session(engine) as session:
        movieObj= MovieCRUD.get_by_api_id(session,api_id)
        if movieObj.data != None:
            MovieCRUD.delete(session,movieObj.data.id)
            return True
        return False
        










class Serial(BaseModel):
    """Movie Base Model for table Movie"""
    title: str 
    id : int
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
    season_count : int






@router.post('/serial')
async def create(serial_json:Serial):
    serial = SerialBase(
        title=serial_json.title,type_=serial_json.type,
        description=serial_json.description,
        year=serial_json.year,
        duration=serial_json.duration,
        imdb=serial_json.imdb,
        is_persian=serial_json.persian,
        image_url=serial_json.image,
        cover_url=serial_json.cover,
        api_id=serial_json.id,
        season_count=serial_json.season_count

        )

    with Session(engine) as session:

        SerialObj= SerialCRUD.get_by_title(session,serial_json.title)

        if SerialObj.data == None:
            serial = SerialCRUD.create(session,serial)
            session.refresh(serial.data)

            type_ = serial_json.trailer.get("type")
            url = serial_json.trailer.get("url")
            trailer = TrailerBase(type_=type_,url=url)
            print(serial.data.id,url,type_)
            TrailerCRUD.create(session,trailer,serial_id=serial.data.id)



            for genre in serial_json.genres:
                    title = genre.get("title")
                    genre = GenreCRUD.get_by_title(session,title)
                    
                    if genre.data == None:
                        genre_c = GenreBase(title=title)
                        genre = GenreCRUD.create(session,genre_c)
                        session.refresh(genre.data)
                        SerialCRUD.add_genre(session,serial_id=serial.data.id,genre_id=genre.data.id)
                    else:
                        SerialCRUD.add_genre(session,serial_id=serial.data.id,genre_id=genre.data.id)
        
            for actor in serial_json.actors:
                    name = actor.get("name")
                    image = actor.get("image")
                    actor = ActorCRUD.get_by_name(session,name)

                    if actor.data == None:
                        actor_c = ActorBase(name=name,image_url=image)
                        actor = ActorCRUD.create(session,actor_c)
                        session.refresh(actor.data)
                        SerialCRUD.add_actor(session,serial_id=serial.data.id,actor_id=actor.data.id)
                    else:
                        SerialCRUD.add_actor(session,serial_id=serial.data.id,actor_id=actor.data.id)   

            for country in serial_json.countries:
                    title = country.get("title")
                    image = country.get("image")
                    country = CountryCRUD.get_by_title(session,title=title)

                    if country.data == None:
                        country_c = CountryBase(title=title,image_url=image)
                        country = CountryCRUD.create(session,country_c)
                        session.refresh(country.data)
                        SerialCRUD.add_country(session,serial_id=serial.data.id,country_id=country.data.id)
                    else:
                        SerialCRUD.add_country(session,serial_id=serial.data.id,country_id=country.data.id)


            return {"Created":serial_json.title}
        
        return {f"This movie {SerialObj.data.title}":"already exist"}
    


@router.patch('/serial/{api_id}')
async def update(api_id:int,serial_json:Serial):
    serial = SerialBase(
        title=serial_json.title,type_=serial_json.type,
        description=serial_json.description,
        year=serial_json.year,
        duration=serial_json.duration,
        imdb=serial_json.imdb,
        is_persian=serial_json.persian,
        image_url=serial_json.image,
        cover_url=serial_json.cover,
        api_id=serial_json.id,
        season_count=serial_json.season_count

        )
    with Session(engine) as session:

        SerialObj= SerialCRUD.get_by_api_id(session,api_id)
        if SerialObj.data != None:
            serial = SerialCRUD.update(session,SerialObj.data.id,serial.model_dump())
            return {f"This movie '{SerialObj.data.title}'":"Updated "}
        return "No serial with this id"



@router.delete('/serial/{api_id}')
async def delete(api_id:int):
    with Session(engine) as session:
        SerialObj= SerialCRUD.get_by_api_id(session,api_id)
        if SerialObj.data != None:
            SerialCRUD.delete(session,SerialObj.data.id)
            return True
        return False
        