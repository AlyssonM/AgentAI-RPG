from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .models import Base, Character, Game
import json

class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def save_game_state(self, chat_id, game_state):
        with self.session_scope() as session:
            # Fetch the game record by chat_id
            game = session.query(Game).filter_by(chat_id=chat_id).first()
            if not game:
                # If no game is found, this is an error or initialization scenario
                raise ValueError("Game not found for chat_id: {}".format(chat_id))
            # Update the game state
            game.state = json.dumps(game_state)  # Convert the dictionary to a JSON string
            session.add(game)  # Not necessary if only updating, but included for completeness
            session.commit()
            return game.state
    
    def save_game(self, chat_id, theme, context_dict, is_active=True):
        with self.session_scope() as session:
            game = session.query(Game).filter_by(chat_id=chat_id).first()
            context_json = json.dumps(context_dict)  # Serializa o dicionário para JSON
            if game is None:
                game = Game(chat_id=chat_id, theme=theme, state=context_json, is_active=is_active)
                session.add(game)
            else:
                game.state = context_json
                game.theme = theme
                game.is_active = is_active

            session.commit()
            
    def create_character(self, **kwargs):
        with self.session_scope() as session:
            character = session.query(Character).filter_by(user_id=kwargs.get('user_id')).first()
            if character is None:
                character = Character(**kwargs)
                session.add(character)
            session.commit()
            return character
      

    def get_game_state(self, chat_id):
        with self.session_scope() as session:
            game = session.query(Game).filter_by(chat_id=chat_id).first()
            if game:
                return json.loads(game.state) if game.state else {}
            return None
    
    
    def update_character_stats(self, user_id, stats_updates):
        with self.session_scope() as session:
            character = session.query(Character).filter_by(user_id=user_id).first()
            if character:
                for stat, value in stats_updates.items():
                    if hasattr(character, stat) and isinstance(value, (int, float)):
                        current_value = getattr(character, stat) or 0
                        setattr(character, stat, current_value + value)
                session.commit()
                return True
            return False
        
    
# Outros métodos de Database aqui, adaptados para usar session_scope
