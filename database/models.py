from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()

# Modelo Game
class Game(Base):
    __tablename__ = 'games'
    chat_id = Column(Integer, primary_key=True)
    theme = Column(String(255), nullable=False)
    state = Column(JSON)
    is_active = Column(Boolean, default=True)
    
    # Relação um-para-muitos com Character
    characters = relationship('Character', backref='game', lazy='dynamic')
    
    def __repr__(self):
        return f"<Game(id={self.id}, theme='{self.theme}', active={self.is_active})>"
    
# Modelo Character
class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.chat_id'))  # Chave estrangeira para vincular ao Game
    user_id = Column(Integer, unique=True)
    name = Column(String(255))
    background = Column(String(1024))
    strength = Column(Integer)
    intelligence = Column(Integer)
    agility = Column(Integer)
    magic = Column(Integer)
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', game_id={self.game_id})>"
