from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os

# Create database directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Database URL
DATABASE_URL = "sqlite:///./data/chess_game.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    salt = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    games_created = relationship("Game", back_populates="creator", foreign_keys="Game.creator_id")
    game_players = relationship("GamePlayer", back_populates="user")

class Game(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, index=True)
    creator_id = Column(String, ForeignKey("users.id"))
    joiner_id = Column(String, ForeignKey("users.id"), nullable=True)
    creator_color = Column(String)  # 'white' or 'black'
    status = Column(String, default="waiting")  # 'waiting', 'active', 'completed'
    result = Column(String, nullable=True)  # 'checkmate', 'stalemate', 'draw', etc.
    winner_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="games_created", foreign_keys=[creator_id])
    players = relationship("GamePlayer", back_populates="game")
    moves = relationship("GameMove", back_populates="game", order_by="GameMove.move_number")

class GamePlayer(Base):
    __tablename__ = "game_players"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, ForeignKey("games.id"))
    user_id = Column(String, ForeignKey("users.id"))
    color = Column(String)  # 'white' or 'black'
    joined_at = Column(DateTime, default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="players")
    user = relationship("User", back_populates="game_players")

class GameMove(Base):
    __tablename__ = "game_moves"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, ForeignKey("games.id"))
    player_id = Column(String, ForeignKey("users.id"))
    move_number = Column(Integer)
    move_uci = Column(String)  # UCI format (e.g., "e2e4")
    move_san = Column(String)  # SAN format (e.g., "e4")
    fen_after = Column(Text)  # FEN after this move
    is_check = Column(Boolean, default=False)
    is_checkmate = Column(Boolean, default=False)
    is_stalemate = Column(Boolean, default=False)
    is_draw = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="moves")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
create_tables() 