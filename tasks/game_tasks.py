from crewai import Task
from textwrap import dedent
from tools.game_tools import TelegramTools
import random

class GameMasterTasks:
    def __init__(self, agent):
        self.agent = agent
        
    def create_game_world(self, tools, chat_id, theme, context, callback):
        return Task(
            description=dedent(f"""
                               Generate a description of the game world, including geography, culture and history, 
                               for the selected theme "{theme}" and send it to the group {chat_id}. Use the random seed to generate 
                               completely new worlds each time: {random.randint(1, 100000000)}."""
                               ),
            expected_output="A detailed captivating and immersive text-based RPG game. Output only in Portuguese (pt-br) with maximum of 1000 tokens",
            tools=tools,
            agent=self.agent,
            context=context,
            callback=callback,
            human_input=False
        )
        
class BardTasks:
    def __init__(self, agent):
        self.agent = agent
        
    def narrate_event(self, tools, chat_id, game_context, event_description, callback):
        return Task(
            description=dedent(f"""
                               Narrate the event based on the current game context 'rolling': {game_context}, and player actions:
                               {event_description}. Send it to the group {chat_id}.
                               """),
            expected_output="""A vivid and engaging narrative that enhances the game experience with maximum of 200 tokens. 
                            Choices presented to the user must labeled by number (max. of 3 actions choices). Output only in Portuguese (pt-br).
                            """,
            tools=tools,
            agent=self.agent,
            callback=callback,
            human_input=False
        )

    def action_event(self, tools, chat_id, choice, game_context, callback):
        return Task(
            description=dedent(f"""
                           Resolve the user's choice: {choice}, based on the current game context: {game_context['rolling']}. 
                           This action should directly address the consequences of the user's last choice without initiating any new action requests.
                           """),
            expected_output="Description of the action's consequence, continuing the game narrative without requiring further immediate inputs from the user. Output in Portuguese (pt-br).",
            tools=tools,
            agent=self.agent,
            callback=callback,
            human_input=False
        )
        
    def describe_scene(self, tools, chat_id, location_description, context):
        return Task(
            description=dedent(f"""
                               Provide a detailed description of the location within the game world:
                               {location_description}. Send it to the group {chat_id}.
                               """),
            expected_output="A rich and immersive description of the scene that sets the atmosphere.",
            tools=tools,
            agent=self.agent,
            context=context,
            human_input=False
        )

class ArchivistTasks:
    def __init__(self, agent):
        self.agent = agent
        
    def create_character(self, tools, user_id, player_info, context, callback):
        return Task(
            description=dedent(f"""
                               Create a detailed character for user_id={user_id} contextualized with the game world: {player_info}. 
                               The character must have attributes name, user_id, background, traits, and initial stats 
                               including strength, intelligence, agility, magic, and charisma, along with special equipment.
                               """),
            expected_output="A fully detailed character with all attributes and initial stats using a json formatted dictionary structure.",
            tools=tools,
            agent=self.agent,
            context=context,
            callback=callback,
            human_input=False
        )

    def update_character_progress(self, agent, tools, user_id, updates, context):
        return Task(
            description=dedent(f"""
                               Update the character's progress based on their recent experiences and achievements,
                               based on the updates discription {updates}, and send the update privately to the player {user_id}.
                               """),
            expected_output="Updated character stats and inventory.",
            tools=tools,
            agent=agent,
            context=context,
            human_input=False
        )

    def manage_npc_interactions(self, agent, tools, chat_id, npc_info, context):
        return Task(
            description=dedent("""
                               Manage and update NPC data and interactions based on the game's evolving story,
                               and maintain a record in the system.
                               """),
            expected_output="NPC data updated with new interactions and dialogue options.",
            tools=tools,
            agent=agent,
            context=context,
            human_input=False
        )        