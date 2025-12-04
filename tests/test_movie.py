from database.models import MovieBase
from database.db import MovieCRUD


# ============= MOVIE TESTS =============

class TestMovieCRUD:
    """Test suite for Movie CRUD operations"""
    
    def test_create_movie(self, session):
        """Test creating a new movie"""
        movie_data = MovieBase(
            title="Inception",
            type_="Movie",
            description="A thief who steals corporate secrets through dream-sharing technology.",
            year="2010",
            duration=148,
            imdb=8.8,
            is_persian=False,
            image_url="https://example.com/inception.jpg",
            cover_url="https://example.com/inception-cover.jpg"
        )
        movie = MovieCRUD.create(session, movie_data)
        
        assert movie.id is not None
        assert movie.title == "Inception"
        assert movie.duration == 148
        assert movie.imdb == 8.8
    
    def test_get_movie_by_id(self, session, sample_movie):
        """Test retrieving movie by ID"""
        movie = MovieCRUD.get_by_id(session, sample_movie.id)
        assert movie is not None
        assert movie.title == sample_movie.title
    
    def test_get_movie_by_title(self, session, sample_movie):
        """Test retrieving movie by title"""
        movie = MovieCRUD.get_by_title(session, "The Matrix")
        assert movie is not None
        assert movie.title == "The Matrix"
    
    def test_search_movies_by_title(self, session):
        """Test searching movies with partial title match"""
        # Create multiple movies
        MovieCRUD.create(session, MovieBase(
            title="The Matrix", type_="Movie", description="Test",
            year="1999", duration=136, imdb=8.7, is_persian=False,
            image_url="url", cover_url="url"
        ))
        MovieCRUD.create(session, MovieBase(
            title="The Matrix Reloaded", type_="Movie", description="Test",
            year="2003", duration=138, imdb=7.2, is_persian=False,
            image_url="url", cover_url="url"
        ))
        
        results = MovieCRUD.search_by_title(session, "Matrix")
        assert len(results) >= 2
        assert all("Matrix" in movie.title for movie in results)
    
    def test_get_movies_with_pagination(self, session):
        """Test pagination for movies"""
        # Create 10 movies
        for i in range(10):
            MovieCRUD.create(session, MovieBase(
                title=f"Movie {i}", type_="Movie", description="Test",
                year="2020", duration=120, imdb=7.0, is_persian=False,
                image_url="url", cover_url="url"
            ))
        
        page1 = MovieCRUD.get_all(session, skip=0, limit=5)
        page2 = MovieCRUD.get_all(session, skip=5, limit=5)
        
        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id
    
    def test_get_persian_movies(self, session):
        """Test filtering Persian movies"""
        MovieCRUD.create(session, MovieBase(
            title="Persian Movie", type_="Movie", description="Test",
            year="2020", duration=120, imdb=7.0, is_persian=True,
            image_url="url", cover_url="url"
        ))
        MovieCRUD.create(session, MovieBase(
            title="Hollywood Movie", type_="Movie", description="Test",
            year="2020", duration=120, imdb=7.0, is_persian=False,
            image_url="url", cover_url="url"
        ))
        
        persian_movies = MovieCRUD.get_persian_movies(session)
        assert all(movie.is_persian for movie in persian_movies)
    
    def test_get_movies_by_year(self, session):
        """Test filtering movies by year"""
        MovieCRUD.create(session, MovieBase(
            title="2020 Movie", type_="Movie", description="Test",
            year="2020", duration=120, imdb=7.0, is_persian=False,
            image_url="url", cover_url="url"
        ))
        
        movies_2020 = MovieCRUD.get_by_year(session, "2020")
        assert all(movie.year == "2020" for movie in movies_2020)
    
    def test_get_movies_by_imdb_rating(self, session):
        """Test filtering movies by IMDB rating"""
        MovieCRUD.create(session, MovieBase(
            title="High Rated", type_="Movie", description="Test",
            year="2020", duration=120, imdb=9.0, is_persian=False,
            image_url="url", cover_url="url"
        ))
        MovieCRUD.create(session, MovieBase(
            title="Low Rated", type_="Movie", description="Test",
            year="2020", duration=120, imdb=5.0, is_persian=False,
            image_url="url", cover_url="url"
        ))
        
        high_rated = MovieCRUD.get_by_imdb_rating(session, 8.0)
        assert all(movie.imdb >= 8.0 for movie in high_rated)
    
    def test_update_movie(self, session, sample_movie):
        """Test updating movie information"""
        update_data = {
            "imdb": 9.0,
            "description": "Updated description"
        }
        updated = MovieCRUD.update(session, sample_movie.id, update_data)
        
        assert updated.imdb == 9.0
        assert updated.description == "Updated description"
        assert updated.title == sample_movie.title  # Unchanged
    
    def test_delete_movie(self, session, sample_movie):
        """Test deleting a movie"""
        movie_id = sample_movie.id
        result = MovieCRUD.delete(session, movie_id)
        
        assert result is True
        assert MovieCRUD.get_by_id(session, movie_id) is None