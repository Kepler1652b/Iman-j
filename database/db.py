"""
This Module Contains DataBase CRUD action For all Tables
WITH COMPREHENSIVE ERROR HANDLING
"""

from sqlmodel import create_engine, select, SQLModel, Session
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    DataError,
    DatabaseError,
    ProgrammingError,
    InvalidRequestError
)
import logging
from contextlib import contextmanager

from .models import (
    User, UserBase,
    Movie, MovieBase,
    Genre, GenreBase,
    Country, CountryBase,
    Actor, ActorBase,
    Trailer, TrailerBase,
    MovieGenreLink,
    MovieCountryLink,
    MovieActorLink,Post,PostBase,
    Serial,SerialBase,EpisodeBase,Episode,
    SerialGenreLink,SerialActorLink,SerialCountryLink,
    Season,SeasonBase

)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============= RESULT CLASSES =============

class CRUDResult:
    """Standard result object for CRUD operations"""
    def __init__(self, success: bool, data: Any = None, error: str = None, error_type: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.error_type = error_type
    
    def __bool__(self):
        return self.success
    
    def __repr__(self):
        if self.success:
            return f"CRUDResult(success=True, data={self.data})"
        return f"CRUDResult(success=False, error='{self.error}')"


# ============= ERROR HANDLER DECORATOR =============

def handle_db_errors(operation_name: str = "Database operation"):
    """Decorator to handle all database errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            session = args[0] if args else kwargs.get('session')
            
            try:
                result = func(*args, **kwargs)
                return CRUDResult(success=True, data=result)
            
            except IntegrityError as e:
                if session:
                    session.rollback()
                
                error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
                
                # Determine specific constraint violation
                if "UNIQUE constraint failed" in error_msg or "duplicate key" in error_msg.lower():
                    if "telegram_id" in error_msg:
                        error = "User with this Telegram ID already exists"
                    elif "username" in error_msg:
                        error = "Username already taken"
                    elif "email" in error_msg:
                        error = "Email already registered"
                    else:
                        error = "Record with this value already exists"
                elif "FOREIGN KEY constraint failed" in error_msg or "foreign key" in error_msg.lower():
                    error = "Referenced record does not exist"
                elif "NOT NULL constraint failed" in error_msg:
                    error = "Required field is missing"
                else:
                    error = "Database constraint violation"
                
                logger.warning(f"{operation_name} failed: {error} - {error_msg}")
                return CRUDResult(success=False, error=error, error_type="IntegrityError")
            
            except OperationalError as e:
                if session:
                    session.rollback()
                
                error_msg = str(e)
                
                if "database is locked" in error_msg.lower():
                    error = "Database is temporarily locked. Please try again."
                elif "no such table" in error_msg.lower():
                    error = "Database table not found. Please run migrations."
                elif "unable to open database" in error_msg.lower():
                    error = "Cannot connect to database"
                elif "timeout" in error_msg.lower():
                    error = "Database operation timed out"
                else:
                    error = "Database operational error"
                
                logger.error(f"{operation_name} failed: {error} - {error_msg}")
                return CRUDResult(success=False, error=error, error_type="OperationalError")
            
            except DataError as e:
                if session:
                    session.rollback()
                
                error_msg = str(e)
                
                if "too long" in error_msg.lower() or "value too long" in error_msg.lower():
                    error = "Data exceeds maximum length"
                elif "invalid input syntax" in error_msg.lower():
                    error = "Invalid data format"
                elif "numeric" in error_msg.lower():
                    error = "Invalid numeric value"
                else:
                    error = "Invalid data provided"
                
                logger.warning(f"{operation_name} failed: {error} - {error_msg}")
                return CRUDResult(success=False, error=error, error_type="DataError")
            
            except ProgrammingError as e:
                if session:
                    session.rollback()
                
                error = "Database programming error (check your query)"
                logger.error(f"{operation_name} failed: {error} - {str(e)}")
                return CRUDResult(success=False, error=error, error_type="ProgrammingError")
            
            except InvalidRequestError as e:
                if session:
                    session.rollback()
                
                error = "Invalid database request"
                logger.error(f"{operation_name} failed: {error} - {str(e)}")
                return CRUDResult(success=False, error=error, error_type="InvalidRequestError")
            
            except DatabaseError as e:
                if session:
                    session.rollback()
                
                error = "General database error"
                logger.error(f"{operation_name} failed: {error} - {str(e)}")
                return CRUDResult(success=False, error=error, error_type="DatabaseError")
            
            except Exception as e:
                if session:
                    session.rollback()
                
                error = f"Unexpected error: {str(e)}"
                logger.exception(f"{operation_name} failed with unexpected error")
                return CRUDResult(success=False, error=error, error_type="UnexpectedError")
        
        return wrapper
    return decorator


# ============= SAFE SESSION CONTEXT MANAGER =============

@contextmanager
def safe_session(engine):
    """Context manager for safe session handling"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Session error: {e}")
        raise
    finally:
        session.close()




class UserCRUD:
    """
     Class for User CRUD actions
    """
    @staticmethod
    @handle_db_errors("Create user")
    def create(session: Session, user_data: UserBase) -> User:
        """Create a new user"""
        user = User.model_validate(user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    @handle_db_errors("Get user by ID")
    def get_by_id(session: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID
        returns None if User with id dose not exist
        """
        return session.get(User, user_id)
    
    @staticmethod
    @handle_db_errors("Get user by Telegram ID")
    def get_by_telegram_id(session: Session, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        statement = select(User).where(User.telegram_id == telegram_id)
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Get all users")
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        statement = select(User).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get active users")
    def get_active_users(session: Session) -> List[User]:
        """Get all active users"""
        statement = select(User).where(User.is_active == True)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get admin users")
    def get_admins(session: Session) -> List[User]:
        """Get all admin users"""
        statement = select(User).where(User.is_admin == True)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Update user by ID")
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
    @handle_db_errors("Delete user")
    def delete(session: Session, user_id: int) -> bool:
        """Delete user"""
        user = session.get(User, user_id)
        if not user:
            return False
        
        session.delete(user)
        session.commit()
        return True
    
    # @staticmethod
    # def get_or_create(session: Session, telegram_id: int, **kwargs) -> Tuple[User, bool]:
    #     """Get existing user or create new one. Returns (user, created)"""
    #     result = UserCRUD.get_by_telegram_id(session, telegram_id)
        
    #     if result.success and result.data:
    #         return result.data, False
        
    #     # Create new user
    #     user_data = UserBase(telegram_id=telegram_id, **kwargs)
    #     create_result = UserCRUD.create(session, user_data)
        
    #     if create_result.success:
    #         return create_result.data, True
    #     else:
    #         # Race condition: created between check and insert
    #         result = UserCRUD.get_by_telegram_id(session, telegram_id)
    #         if result.success and result.data:
    #             return result.data, False
    #         raise Exception(f"Failed to get or create user: {create_result.error}")


# ============= GENRE CRUD =============

class GenreCRUD:
    
    @staticmethod
    @handle_db_errors("Create genre")
    def create(session: Session, genre_data: GenreBase) -> Genre:
        """Create a new genre"""
        genre = Genre.model_validate(genre_data)
        session.add(genre)
        session.commit()
        session.refresh(genre)
        return genre
    
    @staticmethod
    @handle_db_errors("Get genre by ID")
    def get_by_id(session: Session, genre_id: int) -> Optional[Genre]:
        """Get genre by ID"""
        return session.get(Genre, genre_id)
    
    @staticmethod
    @handle_db_errors("Get genre by Title")
    def get_by_title(session: Session, title: str) -> Optional[Genre]:
        """Get genre by title"""
        statement = select(Genre).where(Genre.title == title)
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Get  all genres")
    def get_all(session: Session) -> List[Genre]:
        """Get all genres"""
        statement = select(Genre)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Update genre by ID")
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
    @handle_db_errors("Delete genre by ID")
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
    @handle_db_errors("Create country")
    def create(session: Session, country_data: CountryBase) -> Country:
        """Create a new country"""
        country = Country.model_validate(country_data)
        session.add(country)
        session.commit()
        session.refresh(country)
        return country
    
    @staticmethod
    @handle_db_errors("Get country by ID")
    def get_by_id(session: Session, country_id: int) -> Optional[Country]:
        """Get country by ID"""
        return session.get(Country, country_id)
    
    @staticmethod
    @handle_db_errors("Get country by Title")
    def get_by_title(session: Session, title: str) -> Optional[Country]:
        """Get country by title"""
        statement = select(Country).where(Country.title == title)
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Get all countries")
    def get_all(session: Session) -> List[Country]:
        """Get all countries"""
        statement = select(Country)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Update country by ID")
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
    @handle_db_errors("Delete country by ID")
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
    @handle_db_errors("Create actor")
    def create(session: Session, actor_data: ActorBase) -> Actor:
        """Create a new actor"""
        actor = Actor.model_validate(actor_data)
        session.add(actor)
        session.commit()
        session.refresh(actor)
        return actor
    
    @staticmethod
    @handle_db_errors("Get actor by ID")
    def get_by_id(session: Session, actor_id: int) -> Optional[Actor]:
        """Get actor by ID"""
        return session.get(Actor, actor_id)
    
    @staticmethod
    @handle_db_errors("Get actor by name")
    def get_by_name(session: Session, name: str) -> Optional[Actor]:
        """Get actor by name"""
        statement = select(Actor).where(Actor.name == name)
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Get all actors")
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Actor]:
        """Get all actors with pagination"""
        statement = select(Actor).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Search actor by name")
    def search_by_name(session: Session, name: str) -> List[Actor]:
        """Search actors by name (partial match)"""
        statement = select(Actor).where(Actor.name.contains(name))
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Update actor by ID")
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
    @handle_db_errors("Delete actor by ID")
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
    @handle_db_errors("Create trailer")
    def create(session: Session, trailer_data: TrailerBase, movie_id: int = None, serial_id: int=None) -> Trailer:
        """Create a new trailer"""
        trailer = Trailer.model_validate(trailer_data)
        trailer.movie_id = movie_id
        trailer.serial_id = serial_id
        session.add(trailer)
        session.commit()
        session.refresh(trailer)
        return trailer
    
    @staticmethod
    @handle_db_errors("Get trailer by ID")
    def get_by_id(session: Session, trailer_id: int) -> Optional[Trailer]:
        """Get trailer by ID"""
        return session.get(Trailer, trailer_id)
    
    @staticmethod
    @handle_db_errors("Get trailers by movie ID")
    def get_by_movie_id(session: Session, movie_id: int) -> List[Trailer]:
        """Get all trailers for a movie"""
        statement = select(Trailer).where(Trailer.movie_id == movie_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get all trailers")
    def get_all(session: Session) -> List[Trailer]:
        """Get all trailers"""
        statement = select(Trailer)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Update trailer")
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
    @handle_db_errors("Delete trailer")
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
    @handle_db_errors("Create movie")
    def create(session: Session, movie_data: MovieBase) -> Movie:
        """Create a new movie"""
        movie = Movie.model_validate(movie_data)
        session.add(movie)
        session.commit()
        session.refresh(movie)
        return movie
    

    @staticmethod
    @handle_db_errors("Get movie by ID")
    def get_by_id(session: Session, movie_id: int) -> Optional[Movie]:
        """Get movie by ID with all relationships"""
        return session.get(Movie, movie_id)
    
    @staticmethod
    @handle_db_errors("Get movie by api ID")
    def get_by_api_id(session: Session, movie_api_id: int) -> Optional[Movie]:
        """Get movie by ID with all relationships"""
        statement = select(Movie).where(Movie.api_id == movie_api_id)
        return session.exec(statement).first()

    @staticmethod
    @handle_db_errors("Get movie by Title")
    def get_by_title(session: Session, title: str) -> Optional[Movie]:
        """Get movie by title"""
        statement = select(Movie).where(Movie.title == title)
        return session.exec(statement).first()
    

    @staticmethod
    @handle_db_errors("Get all movies")
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Get all movies with pagination"""
        statement = select(Movie).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    

    @staticmethod
    @handle_db_errors("Search movies by Title")
    def search_by_title(session: Session, title: str) -> List[Movie]:
        """Search movies by title (partial match)"""
        statement = select(Movie).where(Movie.title.contains(title))
        return list(session.exec(statement).all())
    

    @staticmethod
    @handle_db_errors("Get movie by genre ID")
    def get_by_genre(session: Session, genre_id: int) -> List[Movie]:
        """Get all movies by genre's id"""
        statement = select(Movie).join(MovieGenreLink).where(MovieGenreLink.genre_id == genre_id)
        return list(session.exec(statement).all())
    

    @staticmethod
    @handle_db_errors("Get movie by title")
    def get_by_genre_title(session: Session, genre_title: int):
        """ Get all movies by genre's title"""
        genre = GenreCRUD.get_by_title(session,genre_title)
        statement = select(Movie).join(MovieGenreLink).where(MovieGenreLink.genre_id == genre.id)
        return list(session.exec(statement).all())


    @staticmethod
    @handle_db_errors("Get movie by Country ID")
    def get_by_country(session: Session, country_id: int) -> List[Movie]:
        """Get all movies by country"""
        statement = select(Movie).join(MovieCountryLink).where(MovieCountryLink.country_id == country_id)
        return list(session.exec(statement).all())
    

    @staticmethod
    @handle_db_errors("Get movie by Country name")
    def get_by_country_name(session: Session, country_name: int) -> List[Movie]:
        """Get all movies by country's name"""
        country = CountryCRUD.get_by_title(session,country_name)
        statement = select(Movie).join(MovieCountryLink).where(MovieCountryLink.country_id == country.id)
        return list(session.exec(statement).all())


    @staticmethod
    @handle_db_errors("Get movie by Actor ID")
    def get_by_actor(session: Session, actor_id: int) -> List[Movie]:
        """Get all movies by actor"""
        statement = select(Movie).join(MovieActorLink).where(MovieActorLink.actor_id == actor_id)
        return list(session.exec(statement).all())
    

    @staticmethod
    @handle_db_errors("Get movie by Actor name")
    def get_by_actor_name(session: Session, actor_name: int) -> List[Movie]:
        """Get all movies by actor"""
        actor = ActorCRUD.get_by_name(session,actor_name)
        statement = select(Movie).join(MovieActorLink).where(MovieActorLink.actor_id == actor.id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Persian movies")
    def get_persian_movies(session: Session) -> List[Movie]:
        """Get all Persian movies"""
        statement = select(Movie).where(Movie.is_persian == True)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get movie by year")
    def get_by_year(session: Session, year: str) -> List[Movie]:
        """Get movies by year with (partial match)"""
        statement = select(Movie).where(Movie.year.contains(year))
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get movie by imdb")
    def get_by_imdb_rating(session: Session, min_rating: float) -> List[Movie]:
        """Get movies with IMDB rating above threshold"""
        statement = select(Movie).where(Movie.imdb >= min_rating)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Update movie by ID")
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
    @handle_db_errors("Delete movie by ID")
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
    @handle_db_errors("Add genre to movie")
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
    @handle_db_errors("Remove genre from movie")
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
    @handle_db_errors("Add country to movie")
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
    @handle_db_errors("Remove country from movie")
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
    @handle_db_errors("Add actor to movie")
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
    @handle_db_errors("Remove actor from movie")
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











# ============= SERIAL CRUD =============

class SerialCRUD:
    
    @staticmethod
    @handle_db_errors("Create Serial")
    def create(session: Session, serial_data: SerialBase) -> Serial:
        """Create a new Serial"""
        serial = Serial.model_validate(serial_data)
        session.add(serial)
        session.commit()
        session.refresh(serial)
        return serial
    
    @staticmethod
    @handle_db_errors("Get Serial by ID")
    def get_by_id(session: Session, serial_id: int) -> Optional[Serial]:
        """Get Serial by ID with all relationships"""
        return session.get(Serial, serial_id)
    
    @staticmethod
    @handle_db_errors("Get Serial by ID")
    def get_by_api_id(session: Session, serial_api_id: int) -> Optional[Serial]:
        """Get Serial by ID with all relationships"""
        statement = select(Serial).where(Serial.api_id == serial_api_id)
        return session.exec(statement).first()
    
    

    @staticmethod
    @handle_db_errors("Get Serial by Title")
    def get_by_title(session: Session, title: str) -> Optional[Serial]:
        """Get Serial by title"""
        statement = select(Serial).where(Serial.title == title)
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Get all Serials")
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Serial]:
        """Get all Serials with pagination"""
        statement = select(Serial).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Search Serial by Title")
    def search_by_title(session: Session, title: str) -> List[Serial]:
        """Search Serial by title (partial match)"""
        statement = select(Serial).where(Serial.title.contains(title))
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by genre ID")
    def get_by_genre(session: Session, genre_id: int) -> List[Serial]:
        """Get all Serials by genre's id"""
        statement = select(Serial).join(SerialGenreLink).where(SerialGenreLink.genre_id == genre_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by genre title")
    def get_by_genre_title(session: Session, genre_title: str):  
        """Get all Serials by genre's title"""
        from .db import GenreCRUD 
        
        genre_result = GenreCRUD.get_by_title(session, genre_title)
        if not genre_result.success or not genre_result.data:
            raise ValueError(f"Genre '{genre_title}' not found")
        
        genre = genre_result.data
        statement = select(Serial).join(SerialGenreLink).where(SerialGenreLink.genre_id == genre.id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by Country ID")
    def get_by_country(session: Session, country_id: int) -> List[Serial]:
        """Get all Serials by country"""
        statement = select(Serial).join(SerialCountryLink).where(SerialCountryLink.country_id == country_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by Country name")
    def get_by_country_name(session: Session, country_name: str) -> List[Serial]:  
        """Get all Serials by country's name"""
        from .db import CountryCRUD
        
        country_result = CountryCRUD.get_by_title(session, country_name)
        if not country_result.success or not country_result.data:
            raise ValueError(f"Country '{country_name}' not found")
        
        country = country_result.data
        statement = select(Serial).join(SerialCountryLink).where(SerialCountryLink.country_id == country.id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by Actor ID")
    def get_by_actor(session: Session, actor_id: int) -> List[Serial]:
        """Get all Serials by actor"""
        statement = select(Serial).join(SerialActorLink).where(SerialActorLink.actor_id == actor_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by Actor name")
    def get_by_actor_name(session: Session, actor_name: str) -> List[Serial]:
        """Get all Serials by actor name"""
        from .db import ActorCRUD
        
        actor_result = ActorCRUD.get_by_name(session, actor_name)
        if not actor_result.success or not actor_result.data:
            raise ValueError(f"Actor '{actor_name}' not found")
        
        actor = actor_result.data
        statement = select(Serial).join(SerialActorLink).where(SerialActorLink.actor_id == actor.id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Persian Serials")
    def get_persian_serials(session: Session) -> List[Serial]:  
        """Get all Persian Serials"""
        statement = select(Serial).where(Serial.is_persian == True)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by year")
    def get_by_year(session: Session, year: str) -> List[Serial]:
        """Get Serials by year with (partial match)"""
        statement = select(Serial).where(Serial.year.contains(year))
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Serial by IMDB rating")
    def get_by_imdb_rating(session: Session, min_rating: float) -> List[Serial]:
        """Get Serials with IMDB rating above threshold"""
        statement = select(Serial).where(Serial.imdb >= min_rating)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Update Serial by ID")
    def update(session: Session, serial_id: int, serial_data: dict) -> Optional[Serial]:
        """Update Serial"""
        serial = session.get(Serial, serial_id)
        if not serial:
            raise ValueError(f"Serial with ID {serial_id} not found")
        
        for key, value in serial_data.items():
            setattr(serial, key, value)
        
        session.add(serial)
        session.commit()
        session.refresh(serial)
        return serial
    
    @staticmethod
    @handle_db_errors("Delete serial by ID")
    def delete(session: Session, serial_id: int) -> bool:
        """Delete serial"""
        serial = session.get(Serial, serial_id)
        if not serial:
            raise ValueError(f"Serial with ID {serial_id} not found")
        
        session.delete(serial)
        session.commit()
        return True
    
    # ===== Relationship Management =====
    
    @staticmethod
    @handle_db_errors("Add genre to serial")
    def add_genre(session: Session, serial_id: int, genre_id: int) -> bool:
        """Add a genre to a serial"""
        link = SerialGenreLink(serial_id=serial_id, genre_id=genre_id)
        session.add(link)
        session.commit()
        return True
    
    @staticmethod
    @handle_db_errors("Remove genre from serial")
    def remove_genre(session: Session, serial_id: int, genre_id: int) -> bool:
        """Remove a genre from a serial"""
        statement = select(SerialGenreLink).where(
            SerialGenreLink.serial_id == serial_id,
            SerialGenreLink.genre_id == genre_id
        )
        link = session.exec(statement).first()
        if not link:
            raise ValueError("Genre-Serial link not found")
        
        session.delete(link)
        session.commit()
        return True
    
    @staticmethod
    @handle_db_errors("Add country to serial")
    def add_country(session: Session, serial_id: int, country_id: int) -> bool:
        """Add a country to a serial"""
        link = SerialCountryLink(serial_id=serial_id, country_id=country_id)
        session.add(link)
        session.commit()
        return True
    
    @staticmethod
    @handle_db_errors("Remove country from serial")
    def remove_country(session: Session, serial_id: int, country_id: int) -> bool:
        """Remove a country from a serial"""
        statement = select(SerialCountryLink).where(
            SerialCountryLink.serial_id == serial_id,
            SerialCountryLink.country_id == country_id
        )
        link = session.exec(statement).first()
        if not link:
            raise ValueError("Country-Serial link not found")
        
        session.delete(link)
        session.commit()
        return True
    
    @staticmethod
    @handle_db_errors("Add actor to serial")
    def add_actor(session: Session, serial_id: int, actor_id: int) -> bool:
        """Add an actor to a serial"""
        link = SerialActorLink(serial_id=serial_id, actor_id=actor_id)
        session.add(link)
        session.commit()
        return True
    
    @staticmethod
    @handle_db_errors("Remove actor from serial")
    def remove_actor(session: Session, serial_id: int, actor_id: int) -> bool:
        """Remove an actor from a serial"""
        statement = select(SerialActorLink).where(
            SerialActorLink.serial_id == serial_id,
            SerialActorLink.actor_id == actor_id
        )
        link = session.exec(statement).first()
        if not link:
            raise ValueError("Actor-Serial link not found")
        
        session.delete(link)
        session.commit()
        return True


# ============= EPISODE CRUD =============

class EpisodeCRUD:
    
    @staticmethod
    @handle_db_errors("Create Episode")
    def create(session: Session, episode_data: EpisodeBase) -> Episode: 
        """Create a new episode"""
        episode = Episode.model_validate(episode_data)
        session.add(episode)
        session.commit()
        session.refresh(episode)
        return episode
    
    @staticmethod
    @handle_db_errors("Get Episode by ID")
    def get_by_id(session: Session, episode_id: int) -> Optional[Episode]:
        """Get episode by ID with all relationships"""
        return session.get(Episode, episode_id)
    

    @staticmethod
    @handle_db_errors("Get Episode by ID")
    def get_by_api_id(session: Session, episode_api_id: int) -> Optional[Episode]:
        """Get episode by ID with all relationships"""
        statement = select(Episode).where(Episode.api_id == episode_api_id)
        return session.exec(statement).first()
    

    @staticmethod
    @handle_db_errors("Get Episode by Title")
    def get_by_title(session: Session, title: str) -> Optional[Episode]:
        """Get Episode by title"""
        statement = select(Episode).where(Episode.title == title)
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Get all Episodes")
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Episode]:
        """Get all Episodes with pagination"""
        statement = select(Episode).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Search Episode by Title")
    def search_by_title(session: Session, title: str) -> List[Episode]:
        """Search Episode by title (partial match)"""
        statement = select(Episode).where(Episode.title.contains(title))
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Episodes by Serial ID")
    def get_by_serial_id(session: Session, serial_id: int) -> List[Episode]:
        """Get all episodes for a serial"""
        statement = select(Episode).where(Episode.serial_id == serial_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Episodes by Season ID")
    def get_by_season_id(session: Session, season_id: int) -> List[Episode]:
        """Get all episodes for a season"""
        statement = select(Episode).where(Episode.season_id == season_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Episode by number")
    def get_by_episode_number(session: Session, serial_id: int, season_id: int, episode_number: int) -> Optional[Episode]:
        """Get specific episode by serial, season, and episode number"""
        statement = select(Episode).where(
            Episode.serial_id == serial_id,
            Episode.season_id == season_id,
            Episode.episode_number == episode_number
        )
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Update Episode by ID")
    def update(session: Session, episode_id: int, episode_data: dict) -> Optional[Episode]:
        """Update Episode"""
        episode = session.get(Episode, episode_id)
        if not episode:
            raise ValueError(f"Episode with ID {episode_id} not found")
        
        for key, value in episode_data.items():
            setattr(episode, key, value)
        
        session.add(episode)
        session.commit()
        session.refresh(episode)
        return episode
    
    @staticmethod
    @handle_db_errors("Delete Episode by ID")
    def delete(session: Session, episode_id: int) -> bool:
        """Delete Episode"""
        episode = session.get(Episode, episode_id)
        if not episode:
            raise ValueError(f"Episode with ID {episode_id} not found")
        
        session.delete(episode)
        session.commit()
        return True


# ============= SEASON CRUD =============

class SeasonCRUD:
    """CRUD operations for Season"""
    
    @staticmethod
    @handle_db_errors("Create Season")
    def create(session: Session, season_data: SeasonBase) -> Season:
        """Create a new season"""
        season = Season.model_validate(season_data)
        session.add(season)
        session.commit()
        session.refresh(season)
        return season
    
    @staticmethod
    @handle_db_errors("Get Season by ID")
    def get_by_id(session: Session, season_id: int) -> Optional[Season]:
        """Get season by ID"""
        return session.get(Season, season_id)
    

    @staticmethod
    @handle_db_errors("Get Season by ID")
    def get_by_api_id(session: Session, season_api_id: int) -> Optional[Season]:
        """Get season by Api ID"""
        statement = select(Season).where(Season.api_id == season_api_id)
        return session.exec(statement).first()
    

    @staticmethod
    @handle_db_errors("Get Seasons by Serial ID")
    def get_by_serial_id(session: Session, serial_id: int) -> List[Season]:
        """Get all seasons for a serial"""
        statement = select(Season).where(Season.serial_id == serial_id)
        return list(session.exec(statement).all())
    
    @staticmethod
    @handle_db_errors("Get Season by number")
    def get_by_season_number(session: Session, serial_id: int, season_number: int) -> Optional[Season]:
        """Get specific season by serial and season number"""
        statement = select(Season).where(
            Season.serial_id == serial_id,
            Season.season_number == season_number
        )
        return session.exec(statement).first()
    
    @staticmethod
    @handle_db_errors("Update Season")
    def update(session: Session, season_id: int, season_data: dict) -> Optional[Season]:
        """Update Season"""
        season = session.get(Season, season_id)
        if not season:
            raise ValueError(f"Season with ID {season_id} not found")
        
        for key, value in season_data.items():
            setattr(season, key, value)
        
        session.add(season)
        session.commit()
        session.refresh(season)
        return season
    
    @staticmethod
    @handle_db_errors("Delete Season")
    def delete(session: Session, season_id: int) -> bool:
        """Delete Season and all its episodes"""
        season = session.get(Season, season_id)
        if not season:
            raise ValueError(f"Season with ID {season_id} not found")
        
        # Delete all episodes in this season first
        statement = select(Episode).where(Episode.season_id == season_id)
        episodes = session.exec(statement).all()
        for episode in episodes:
            session.delete(episode)
        
        # Delete the season
        session.delete(season)
        session.commit()
        return True









class PostCRUD:
    """
     Class for Post CRUD actions
    """
    @staticmethod
    @handle_db_errors("Create post")
    def create(session: Session, post_data: PostBase) -> Post:
        
        """Create a new post"""
        post = Post.model_validate(post_data)
        session.add(post)
        session.commit()
        session.refresh(post)
        return post
    
    @staticmethod
    @handle_db_errors("Get post by ID")
    def get_by_id(session: Session, post_id: int) -> Optional[Post]:
        """
        Get post by ID
        returns None if News with id dose not exist
        """
        return session.get(Post, post_id)
    
    @staticmethod
    @handle_db_errors("Get all posts")
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get all post with pagination"""
        statement = select(Post).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    
    @staticmethod
    @handle_db_errors("Update post by ID")
    def update(session: Session, post_id: int, post_data: dict) -> Optional[Post]:
        """Update post"""
        post = session.get(Post, post_id)
        if not post:
            return None
        
        for key, value in post_data.items():
            setattr(post, key, value)
        
        session.add(post)
        session.commit()
        session.refresh(post)
        return post
    
    @staticmethod
    @handle_db_errors("Delete post by ID")
    def delete(session: Session, post_id: int) -> bool:
        """Delete post"""
        post = session.get(Post, post_id)
        if not post:
            return False
        
        session.delete(post)
        session.commit()
        return True

class Engine:

    @staticmethod
    def create_db(engine):
        """Create all database tables"""
        try:
            SQLModel.metadata.create_all(engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            return None


engine = create_engine("sqlite:///movies.db")
def create_db():
    Engine.create_db(engine)
    

