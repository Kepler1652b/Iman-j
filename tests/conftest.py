"""
Test suite for Movie Database CRUD operations
Following pytest best practices and industry standards
"""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from database.models import (
    User, UserBase,
    Movie, MovieBase,
    Genre, GenreBase,
    Country, CountryBase,
    Actor, ActorBase,

)
from database.db import (
    UserCRUD,
    GenreCRUD,
    CountryCRUD,
    ActorCRUD,
    MovieCRUD
)

"""
Tracemalloc configuration for detecting database connection leaks
and memory issues
"""

import tracemalloc
import pytest
from sqlmodel import Session




# Add this to your conftest.py file

def pytest_configure(config):
    """Enable tracemalloc when pytest starts"""
    tracemalloc.start(25)  # Keep 25 frames in the traceback


def pytest_unconfigure(config):
    """Stop tracemalloc and display memory report"""
    snapshot = tracemalloc.take_snapshot()
    display_top_memory_usage(snapshot)
    tracemalloc.stop()


def display_top_memory_usage(snapshot, key_type='lineno', limit=10):
    """Display top memory consumers"""
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    
    top_stats = snapshot.statistics(key_type)
    
    print("\n" + "="*80)
    print(f"Top {limit} memory allocations:")
    print("="*80)
    
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        print(f"#{index}: {frame.filename}:{frame.lineno}")
        print(f"    Size: {stat.size / 1024:.1f} KiB")
        print(f"    Count: {stat.count} blocks")
        print()


# ============= FIXTURES =============

@pytest.fixture(name="engine")
def engine_fixture():
    """Create in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a new database session for each test"""
    with Session(engine) as session:
        yield session
        session.rollback()  # Rollback any uncommitted changes


@pytest.fixture(name="sample_user")
def sample_user_fixture(session):
    """Create a sample user for testing"""
    user_data = UserBase(
        username="test_user",
        telegram_id=123456789,
        is_active=True,
        is_admin=False
    )
    return UserCRUD.create(session, user_data)


@pytest.fixture(name="sample_genre")
def sample_genre_fixture(session):
    """Create a sample genre for testing"""
    genre_data = GenreBase(title="Action")
    return GenreCRUD.create(session, genre_data)


@pytest.fixture(name="sample_country")
def sample_country_fixture(session):
    """Create a sample country for testing"""
    country_data = CountryBase(
        title="USA",
        image_url="https://example.com/usa.png"
    )
    return CountryCRUD.create(session, country_data)


@pytest.fixture(name="sample_actor")
def sample_actor_fixture(session):
    """Create a sample actor for testing"""
    actor_data = ActorBase(
        name="Keanu Reeves",
        image_url="https://example.com/keanu.jpg"
    )
    return ActorCRUD.create(session, actor_data)


@pytest.fixture(name="sample_movie")
def sample_movie_fixture(session):
    """Create a sample movie for testing"""
    movie_data = MovieBase(
        title="The Matrix",
        type_="Movie",
        description="A computer hacker learns about the true nature of reality.",
        year="1999",
        duration=136,
        imdb=8.7,
        is_persian=False,
        image_url="https://example.com/matrix.jpg",
        cover_url="https://example.com/matrix-cover.jpg"
    )
    return MovieCRUD.create(session, movie_data)



