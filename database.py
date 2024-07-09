from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import json
Base = declarative_base()

# Tabela associativa para a relação muitos-para-muitos entre Characters e Traits
character_trait = Table('character_trait', Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('trait_id', Integer, ForeignKey('traits.id'), primary_key=True)
)

# Modelo Game
class Game(Base):
    __tablename__ = 'games'
    chat_id = Column(Integer, primary_key=True)
    context = Column(String)
    characters = Column(String) #
    
# Modelo Character
class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    name = Column(String(255))
    background = Column(String(1024))
    strength = Column(Integer)
    intelligence = Column(Integer)
    agility = Column(Integer)
    magic = Column(Integer)
    charisma = Column(Integer)
    traits = relationship('Trait', secondary=character_trait, back_populates='characters')
    equipment = relationship('Equipment', back_populates='character')

# Modelo Trait
class Trait(Base):
    __tablename__ = 'traits'
    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    characters = relationship('Character', secondary=character_trait, back_populates='traits')

# Modelo Equipment
class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    enhancement = Column(String(255))
    character_id = Column(Integer, ForeignKey('characters.id'))
    character = relationship('Character', back_populates='equipment')

# Classe Database para gerenciar a sessão e o motor do banco de dados
class Database:
    def __init__(self, session):
        # Armazena a sessão passada ao construtor para ser usada nos métodos da classe
        self.session = session

    def create_character(self, user_id, name, background, strength, intelligence, agility, magic, charisma):
        # Cria um novo personagem utilizando a sessão armazenada
        new_char = Character(
            user_id=user_id, name=name, background=background, strength=strength, 
            intelligence=intelligence, agility=agility, magic=magic, charisma=charisma
        )
        self.session.add(new_char)
        try:
            self.session.commit()
            return new_char
        except Exception as e:
            print(f"Error: {e}")
            self.session.rollback()
            return None

    def get_character_by_user_id(self, user_id):
        return self.session.query(Character).filter_by(user_id=user_id).first()

    def update_character(self, user_id, updates):
        character = self.get_character_by_user_id(user_id)
        if character:
            for key, value in updates.items():
                setattr(character, key, value)
            self.session.commit()
            return character
        return None

    def delete_character(self, user_id):
        character = self.get_character_by_user_id(user_id)
        if character:
            self.session.delete(character)
            self.session.commit()
            return True
        return False
    
    def save_game(self, chat_id, context):
        game = self.session.query(Game).filter_by(chat_id=chat_id).first()
        if not game:
            game = Game(chat_id=chat_id, context=json.dumps(context))
            self.session.add(game)
        else:
            game.context = json.dumps(context)
        self.session.commit()

    def save_character(self, chat_id, context, characters):
        game = self.session.query(Game).filter_by(chat_id=chat_id).first()
        if not game:
            game = Game(chat_id=chat_id, context=json.dumps(context), characters=json.dumps(characters))
        else:
            game.characters = json.dumps(characters)
        self.session.commit()  
            
    def get_game(self, chat_id):
        game = self.session.query(Game).filter_by(chat_id=chat_id).first()
        if game:
            return json.loads(game.context)
        return None
    
    def get_characters(self, chat_id):
        game = self.session.query(Game).filter_by(chat_id=chat_id).first()
        if game:
            return json.loads(game.characters)
        return None


