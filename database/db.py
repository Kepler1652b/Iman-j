"""
This Modul Contains DataBase CRUD action For all Tables
"""

from sqlmodel import create_engine,select,SQLModel,Session
from typing import List, Optional
from models import (
    User, UserBase,
    Movie, MovieBase,
    Genre, GenreBase,
    Country, CountryBase,
    Actor, ActorBase,
    Trailer, TrailerBase,
    MovieGenreLink,
    MovieCountryLink,
    MovieActorLink
)



class UserCRUD:
    """
     Class for User CRUD actions
    """
    @staticmethod
    def create(session: Session, user_data: UserBase) -> User:
        
        """Create a new user"""
        user = User.model_validate(user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_by_id(session: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID
        returns None if User with id dose not exist
        """
        return session.get(User, user_id)
    
    @staticmethod
    def get_by_telegram_id(session: Session, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        statement = select(User).where(User.telegram_id == telegram_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        statement = select(User).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_active_users(session: Session) -> List[User]:
        """Get all active users"""
        statement = select(User).where(User.is_active == True)
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_admins(session: Session) -> List[User]:
        """Get all admin users"""
        statement = select(User).where(User.is_admin == True)
        return list(session.exec(statement).all())
    
    @staticmethod
    def update(session: Session, user_id: int, user_data: dict) -> Optional[User]:
        """Update user"""
        user = session.get(User, user_id)
        if not user:
            return None
        
        for key, value in user_data.items():
            setattr(user, key, value)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def delete(session: Session, user_id: int) -> bool:
        """Delete user"""
        user = session.get(User, user_id)
        if not user:
            return False
        
        session.delete(user)
        session.commit()
        return True


# ============= GENRE CRUD =============

class GenreCRUD:
    
    @staticmethod
    def create(session: Session, genre_data: GenreBase) -> Genre:
        """Create a new genre"""
        genre = Genre.model_validate(genre_data)
        session.add(genre)
        session.commit()
        session.refresh(genre)
        return genre
    
    @staticmethod
    def get_by_id(session: Session, genre_id: int) -> Optional[Genre]:
        """Get genre by ID"""
        return session.get(Genre, genre_id)
    
    @staticmethod
    def get_by_title(session: Session, title: str) -> Optional[Genre]:
        """Get genre by title"""
        statement = select(Genre).where(Genre.title == title)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all(session: Session) -> List[Genre]:
        """Get all genres"""
        statement = select(Genre)
        return list(session.exec(statement).all())
    
    @staticmethod
    def update(session: Session, genre_id: int, genre_data: dict) -> Optional[Genre]:
        """Update genre"""
        genre = session.get(Genre, genre_id)
        if not genre:
            return None
        
        for key, value in genre_data.items():
            setattr(genre, key, value)
        
        session.add(genre)
        session.commit()
        session.refresh(genre)
        return genre
    
    @staticmethod
    def delete(session: Session, genre_id: int) -> bool:
        """Delete genre"""
        genre = session.get(Genre, genre_id)
        if not genre:
            return False
        
        session.delete(genre)
        session.commit()
        return True


# ============= COUNTRY CRUD =============

class CountryCRUD:
    
    @staticmethod
    def create(session: Session, country_data: CountryBase) -> Country:
        """Create a new country"""
        country = Country.model_validate(country_data)
        session.add(country)
        session.commit()
        session.refresh(country)
        return country
    
    @staticmethod
    def get_by_id(session: Session, country_id: int) -> Optional[Country]:
        """Get country by ID"""
        return session.get(Country, country_id)
    
    @staticmethod
    def get_by_title(session: Session, title: str) -> Optional[Country]:
        """Get country by title"""
        statement = select(Country).where(Country.title == title)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all(session: Session) -> List[Country]:
        """Get all countries"""
        statement = select(Country)
        return list(session.exec(statement).all())
    
    @staticmethod
    def update(session: Session, country_id: int, country_data: dict) -> Optional[Country]:
        """Update country"""
        country = session.get(Country, country_id)
        if not country:
            return None
        
        for key, value in country_data.items():
            setattr(country, key, value)
        
        session.add(country)
        session.commit()
        session.refresh(country)
        return country
    
    @staticmethod
    def delete(session: Session, country_id: int) -> bool:
        """Delete country"""
        country = session.get(Country, country_id)
        if not country:
            return False
        
        session.delete(country)
        session.commit()
        return True


# ============= ACTOR CRUD =============

class ActorCRUD:
    
    @staticmethod
    def create(session: Session, actor_data: ActorBase) -> Actor:
        """Create a new actor"""
        actor = Actor.model_validate(actor_data)
        session.add(actor)
        session.commit()
        session.refresh(actor)
        return actor
    
    @staticmethod
    def get_by_id(session: Session, actor_id: int) -> Optional[Actor]:
        """Get actor by ID"""
        return session.get(Actor, actor_id)
    
    @staticmethod
    def get_by_name(session: Session, name: str) -> Optional[Actor]:
        """Get actor by name"""
        statement = select(Actor).where(Actor.name == name)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Actor]:
        """Get all actors with pagination"""
        statement = select(Actor).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    @staticmethod
    def search_by_name(session: Session, name: str) -> List[Actor]:
        """Search actors by name (partial match)"""
        statement = select(Actor).where(Actor.name.contains(name))
        return list(session.exec(statement).all())
    
    @staticmethod
    def update(session: Session, actor_id: int, actor_data: dict) -> Optional[Actor]:
        """Update actor"""
        actor = session.get(Actor, actor_id)
        if not actor:
            return None
        
        for key, value in actor_data.items():
            setattr(actor, key, value)
        
        session.add(actor)
        session.commit()
        session.refresh(actor)
        return actor
    
    @staticmethod
    def delete(session: Session, actor_id: int) -> bool:
        """Delete actor"""
        actor = session.get(Actor, actor_id)
        if not actor:
            return False
        
        session.delete(actor)
        session.commit()
        return True


# ============= TRAILER CRUD =============

class TrailerCRUD:
    
    @staticmethod
    def create(session: Session, trailer_data: TrailerBase, movie_id: int) -> Trailer:
        """Create a new trailer"""
        trailer = Trailer.model_validate(trailer_data)
        trailer.movie_id = movie_id
        session.add(trailer)
        session.commit()
        session.refresh(trailer)
        return trailer
    
    @staticmethod
    def get_by_id(session: Session, trailer_id: int) -> Optional[Trailer]:
        """Get trailer by ID"""
        return session.get(Trailer, trailer_id)
    
    @staticmethod
    def get_by_movie_id(session: Session, movie_id: int) -> List[Trailer]:
        """Get all trailers for a movie"""
        statement = select(Trailer).where(Trailer.movie_id == movie_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_all(session: Session) -> List[Trailer]:
        """Get all trailers"""
        statement = select(Trailer)
        return list(session.exec(statement).all())
    
    @staticmethod
    def update(session: Session, trailer_id: int, trailer_data: dict) -> Optional[Trailer]:
        """Update trailer"""
        trailer = session.get(Trailer, trailer_id)
        if not trailer:
            return None
        
        for key, value in trailer_data.items():
            setattr(trailer, key, value)
        
        session.add(trailer)
        session.commit()
        session.refresh(trailer)
        return trailer
    
    @staticmethod
    def delete(session: Session, trailer_id: int) -> bool:
        """Delete trailer"""
        trailer = session.get(Trailer, trailer_id)
        if not trailer:
            return False
        
        session.delete(trailer)
        session.commit()
        return True


# ============= MOVIE CRUD =============

class MovieCRUD:
    

    @staticmethod
    def create(session: Session, movie_data: MovieBase) -> Movie:
        """Create a new movie"""
        movie = Movie.model_validate(movie_data)
        session.add(movie)
        session.commit()
        session.refresh(movie)
        return movie
    

    @staticmethod
    def get_by_id(session: Session, movie_id: int) -> Optional[Movie]:
        """Get movie by ID with all relationships"""
        return session.get(Movie, movie_id)
    

    @staticmethod
    def get_by_title(session: Session, title: str) -> Optional[Movie]:
        """Get movie by title"""
        statement = select(Movie).where(Movie.title == title)
        return session.exec(statement).first()
    

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Get all movies with pagination"""
        statement = select(Movie).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    

    @staticmethod
    def search_by_title(session: Session, title: str) -> List[Movie]:
        """Search movies by title (partial match)"""
        statement = select(Movie).where(Movie.title.contains(title))
        return list(session.exec(statement).all())
    

    @staticmethod
    def get_by_genre(session: Session, genre_id: int) -> List[Movie]:
        """Get all movies by genre's id"""
        statement = select(Movie).join(MovieGenreLink).where(MovieGenreLink.genre_id == genre_id)
        return list(session.exec(statement).all())
    

    @staticmethod
    def get_by_genre_title(session: Session, genre_title: int):
        """ Get all movies by genre's title"""
        genre = GenreCRUD.get_by_title(session,genre_title)
        statement = select(Movie).join(MovieGenreLink).where(MovieGenreLink.genre_id == genre.id)
        return list(session.exec(statement).all())


    @staticmethod
    def get_by_country(session: Session, country_id: int) -> List[Movie]:
        """Get all movies by country"""
        statement = select(Movie).join(MovieCountryLink).where(MovieCountryLink.country_id == country_id)
        return list(session.exec(statement).all())
    

    @staticmethod
    def get_by_country_name(session: Session, country_name: int) -> List[Movie]:
        """Get all movies by country's name"""
        country = CountryCRUD.get_by_title(session,country_name)
        statement = select(Movie).join(MovieCountryLink).where(MovieCountryLink.country_id == country.id)
        return list(session.exec(statement).all())


    @staticmethod
    def get_by_actor(session: Session, actor_id: int) -> List[Movie]:
        """Get all movies by actor"""
        statement = select(Movie).join(MovieActorLink).where(MovieActorLink.actor_id == actor_id)
        return list(session.exec(statement).all())
    

    @staticmethod
    def get_by_actor_name(session: Session, actor_name: int) -> List[Movie]:
        """Get all movies by actor"""
        actor = ActorCRUD.get_by_name(session,actor_name)
        statement = select(Movie).join(MovieActorLink).where(MovieActorLink.actor_id == actor.id)
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_persian_movies(session: Session) -> List[Movie]:
        """Get all Persian movies"""
        statement = select(Movie).where(Movie.is_persian == True)
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_by_year(session: Session, year: str) -> List[Movie]:
        """Get movies by year with (partial match)"""
        statement = select(Movie).where(Movie.year.contains(year))
        return list(session.exec(statement).all())
    
    @staticmethod
    def get_by_imdb_rating(session: Session, min_rating: float) -> List[Movie]:
        """Get movies with IMDB rating above threshold"""
        statement = select(Movie).where(Movie.imdb >= min_rating)
        return list(session.exec(statement).all())
    
    @staticmethod
    def update(session: Session, movie_id: int, movie_data: dict) -> Optional[Movie]:
        """Update movie"""
        movie = session.get(Movie, movie_id)
        if not movie:
            return None
        
        for key, value in movie_data.items():
            setattr(movie, key, value)
        
        session.add(movie)
        session.commit()
        session.refresh(movie)
        return movie
    
    @staticmethod
    def delete(session: Session, movie_id: int) -> bool:
        """Delete movie"""
        movie = session.get(Movie, movie_id)
        if not movie:
            return False
        
        session.delete(movie)
        session.commit()
        return True
    
    # ===== Relationship Management =====


    ## ===== Genre =====
    @staticmethod
    def add_genre(session: Session, movie_id: int, genre_id: int) -> bool:
        """Add a genre to a movie"""
        link = MovieGenreLink(movie_id=movie_id, genre_id=genre_id)
        session.add(link)
        try:
            session.commit()
            return True
        except:
            session.rollback()
            return False
    
    @staticmethod
    def remove_genre(session: Session, movie_id: int, genre_id: int) -> bool:
        """Remove a genre from a movie"""
        statement = select(MovieGenreLink).where(
            MovieGenreLink.movie_id == movie_id,
            MovieGenreLink.genre_id == genre_id
        )
        link = session.exec(statement).first()
        if not link:
            return False
        
        session.delete(link)
        session.commit()
        return True
    

    ## ===== Country =====
    @staticmethod
    def add_country(session: Session, movie_id: int, country_id: int) -> bool:
        """Add a country to a movie"""
        link = MovieCountryLink(movie_id=movie_id, country_id=country_id)
        session.add(link)
        try:
            session.commit()
            return True
        except:
            session.rollback()
            return False
    
    @staticmethod
    def remove_country(session: Session, movie_id: int, country_id: int) -> bool:
        """Remove a country from a movie"""
        statement = select(MovieCountryLink).where(
            MovieCountryLink.movie_id == movie_id,
            MovieCountryLink.country_id == country_id
        )
        link = session.exec(statement).first()
        if not link:
            return False
        
        session.delete(link)
        session.commit()
        return True
    

    ## ===== Actor =====
    @staticmethod
    def add_actor(session: Session, movie_id: int, actor_id: int) -> bool:
        """Add an actor to a movie"""
        link = MovieActorLink(movie_id=movie_id, actor_id=actor_id)
        session.add(link)
        try:
            session.commit()
            return True
        except:
            session.rollback()
            return False
    
    @staticmethod
    def remove_actor(session: Session, movie_id: int, actor_id: int) -> bool:
        """Remove an actor from a movie"""
        statement = select(MovieActorLink).where(
            MovieActorLink.movie_id == movie_id,
            MovieActorLink.actor_id == actor_id
        )
        link = session.exec(statement).first()
        if not link:
            return False
        
        session.delete(link)
        session.commit()
        return True




class Engine:
    engine = create_engine("sqlite:///movies.db")

    def create_db(engine):
        SQLModel.metadata.create_all(engine)



    
    
