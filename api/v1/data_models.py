from typing import Dict, List, Any
from pydantic import BaseModel



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




class Episode(BaseModel):
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
    episode : Dict[str,Any]



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

