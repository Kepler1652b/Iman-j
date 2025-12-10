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

def add_movie_actors(movie_json,session,movie):
    for actor in movie_json.actors:
        name = actor.get("name")
        image = actor.get("image")
        actor = ActorCRUD.get_by_name(session,name)

        if actor.data == None:
            actor_c = ActorBase(name=name,image_url=image)
            actor = ActorCRUD.create(session,actor_c)
            MovieCRUD.add_actor(session,movie_id=movie.data.id,actor_id=actor.data.id)
        else:
            MovieCRUD.add_actor(session,movie_id=movie.data.id,actor_id=actor.data.id)



def add_movie_genres(movie_json,session,movie):
    for genre in movie_json.genres:
        title = genre.get("title")
        genre = GenreCRUD.get_by_title(session,title)
                    
        if genre.data == None:
            genre_c = GenreBase(title=title)
            genre = GenreCRUD.create(session,genre_c)
            MovieCRUD.add_genre(session,movie_id=movie.data.id,genre_id=genre.data.id)
        else:
            MovieCRUD.add_genre(session,movie_id=movie.data.id,genre_id=genre.data.id)
    

def add_movie_country(movie_json,session,movie):
    for country in movie_json.countries:
        title = country.get("title")
        image = country.get("image")
        country = CountryCRUD.get_by_title(session,title=title)

        if country.data == None:
            country_c = CountryBase(title=title,image_url=image)
            country = CountryCRUD.create(session,country_c)
            session.refresh(country.data)
            MovieCRUD.add_country(session,movie_id=movie.data.id,country_id=country.data.id)
        else:
            MovieCRUD.add_country(session,movie_id=movie.data.id,country_id=country.data.id)


def add_movie_trailer(movie_json,session,movie):
    type_ = movie_json.trailer.get("type")
    url = movie_json.trailer.get("url")
    trailer = TrailerBase(type_=type_,url=url)
    TrailerCRUD.create(session,trailer,movie_id=movie.data.id)

def add_serial_genre(serial_json,session,serial):
    for genre in serial_json.genres:
        title = genre.get("title")
        genre = GenreCRUD.get_by_title(session,title)
        if genre.data == None:
            genre_c = GenreBase(title=title)
            genre = GenreCRUD.create(session,genre_c)
            SerialCRUD.add_genre(session,serial_id=serial.data.id,genre_id=genre.data.id)
        else:
            SerialCRUD.add_genre(session,serial_id=serial.data.id,genre_id=genre.data.id)



def add_serial_actors(serial_json,session,serial):
    for actor in serial_json.actors:
        name = actor.get("name")
        image = actor.get("image")
        actor = ActorCRUD.get_by_name(session,name)

        if actor.data == None:
            actor_c = ActorBase(name=name,image_url=image)
            actor = ActorCRUD.create(session,actor_c)
            SerialCRUD.add_actor(session,serial_id=serial.data.id,actor_id=actor.data.id)
        else:
            SerialCRUD.add_actor(session,serial_id=serial.data.id,actor_id=actor.data.id)   


def add_serial_countries(serial_json,session,serial):
    for country in serial_json.countries:
        title = country.get("title")
        image = country.get("image")
        country = CountryCRUD.get_by_title(session,title=title)
        if country.data == None:
            country_c = CountryBase(title=title,image_url=image)
            country = CountryCRUD.create(session,country_c)
            SerialCRUD.add_country(session,serial_id=serial.data.id,country_id=country.data.id)
        else:
            SerialCRUD.add_country(session,serial_id=serial.data.id,country_id=country.data.id)


def add_serial_trailer(serial_json,session,serial):
    type_ = serial_json.trailer.get("type")
    url = serial_json.trailer.get("url")
    trailer = TrailerBase(type_=type_,url=url)
    TrailerCRUD.create(session,trailer,serial_id=serial.data.id)
