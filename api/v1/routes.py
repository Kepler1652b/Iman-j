from fastapi import APIRouter
from sqlmodel import Session
from .data_models import Movie, Serial, Episode
from database.models import Episode as DataBaseEpisode
from bot.bot import send_to_telegram,app
from bot.config_loader import CHANNEL_ID
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

from .route_utilities import *

router  = APIRouter(prefix='/v1')

async def send_to_telegram_in_api(session,obj):
        session.refresh(obj.data)
        item  = obj.data
        data = item.model_dump()
        if isinstance(item, DataBaseEpisode) and getattr(item, "serial", None):
            data["serial"] = item.serial.model_dump()

        await send_to_telegram(data,app.bot,CHANNEL_ID)
        item.sent = True
        session.add(item)
        session.commit()
        return True


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

        if movieObj.data != None:
            return {f"This movie {movieObj.data.title}":"already exist"}
        
        movie = MovieCRUD.create(session,movie)
        add_movie_trailer(movie_json,session,movie)
        add_movie_genres(movie_json,session,movie)
        add_movie_actors(movie_json,session,movie)
        add_movie_country(movie_json,session,movie)
        # await send_to_telegram_in_api(session,movie)
        return {"Created":movie_json.title}


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
            add_movie_trailer(movie_json,session,movie)
            add_movie_genres(movie_json,session,movie)
            add_movie_actors(movie_json,session,movie)
            add_movie_country(movie_json,session,movie)
            # await send_to_telegram_in_api(session,movie)
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
        

@router.post('/episode')
async def create(serial_json:Episode):
    episode = serial_json.episode
    season = episode.get("season")
    


    with Session(engine) as session:


        serial = SerialCRUD.get_by_api_id(session,serial_json.id)
        if serial.data != None:
            seasonObj = SeasonBase(
                title=season.get("title"),
                api_id=season.get("id"),
                serial_id = serial.data.id
            )
            season = SeasonCRUD.get_by_api_id(session,season.get("id"))
            if season.data == None:
                season = SeasonCRUD.create(session=session,season_data=seasonObj)
                session.refresh(season.data)

            episodeBase = EpisodeBase(
                title = episode.get("title"),
                description = episode.get("description"),
                duration = episode.get("duration"),
                season_id = season.data.id,
                serial_id = serial.data.id,
                api_id = episode.get("id")
            )

            EpisodeObj= EpisodeCRUD.get_by_api_id(session,episode.get('id'))

            if EpisodeObj.data == None:
                episode_c = EpisodeCRUD.create(session,episodeBase)
                # await send_to_telegram_in_api(session,episode_c)

                return {"Created":episode.get('title')}
            
            return {f"This movie {EpisodeObj.data.title}":"already exist"}
        return "NO serial with this id exist"


@router.patch('/episode/{api_id}')
async def update(api_id:int,serial_json:Episode):
    episode = serial_json.episode
    season_json = episode.get("season")


    with Session(engine) as session:
        
        SerialObj= EpisodeCRUD.get_by_api_id(session,api_id)
        serial = SerialCRUD.get_by_api_id(session,serial_json.id)
        season = SeasonCRUD.get_by_api_id(session,season_json.get("id"))
        SeasonObj = SeasonBase(title=season_json.get('title'),api_id=season_json.get('id'),serial_id=serial.data.id)
        if season.data != None:
            season = SeasonCRUD.update(session,season.data.id,SeasonObj.model_dump())
        else:
            season = SeasonCRUD.create(session,SeasonObj)

        episodeBase = EpisodeBase(
                title = episode.get("title"),
                description = episode.get("description"),
                duration = episode.get("duration"),
                season_id = season.data.id,
                serial_id = serial.data.id,
                api_id = episode.get("id")
            )
        
        if SerialObj.data != None:
            serial = EpisodeCRUD.update(session,SerialObj.data.id,episodeBase.model_dump())
            # await send_to_telegram_in_api(session,serial)

            return {f"This movie '{SerialObj.data.title}'":"Updated "}
        return "No episdoe with this id"



@router.delete('/episode/{api_id}')
async def delete(api_id:int):
    with Session(engine) as session:
        EpisodeObj= EpisodeCRUD.get_by_api_id(session,api_id)
        if EpisodeObj.data != None:
            EpisodeCRUD.delete(session,EpisodeObj.data.id)
            return True
        return False
        





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

        if SerialObj.data != None:
            return {f"This movie {SerialObj.data.title}":"already exist"}
        

        serial = SerialCRUD.create(session,serial)

        add_serial_trailer(serial_json,session,serial)
        add_serial_genre(serial_json,session,serial)
        add_serial_countries(serial_json,session,serial)
        add_serial_actors(serial_json,session,serial)
        # await send_to_telegram_in_api(session,serial)
        return {"Created":serial_json.title}
        

    


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
            add_serial_trailer(serial_json,session,serial)
            add_serial_genre(serial_json,session,serial)
            add_serial_countries(serial_json,session,serial)
            add_serial_actors(serial_json,session,serial)
            # await send_to_telegram_in_api(session,serial)
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
        
