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
                               for the selected theme "{theme}". Don't initiate any requets or events. Your goal is
                               exclusively to create a world and a narrative.
                               Use some real random seed mechanism to generate a completely new worlds for each task.
                               Send the full description to the group {chat_id} only once and finish your job.
                               """
                               ),
            expected_output=dedent(f"""A detailed, captivating and immersive description of a text-based RPG game sent to {chat_id}. 
                                Output only in Portuguese (pt-br) with maximum of 1000 tokens
                                """),
            tools=tools,
            agent=self.agent,
            context=context,
            callback=callback,
            human_input=False
        )
        
class BardTasks:
    def __init__(self, agent):
        self.agent = agent
        
    def narrate_event(self, tools, chat_id, user_id, game_chapter, event, callback):
        return Task(
            description=dedent(f"""
                               Narrate the event "{event}" based on the current game chapter event: {game_chapter}. 
                               Send it to the group {chat_id} to finish your job.
                               """
                               ),
            expected_output=dedent(f"""A vivid and engaging narrative that enhances the game experience with maximum of 
                                200 tokens. The output MUST be a JSON formatted dictionary structure for the event
                                containing the fields: an incremental event_id, user_id={user_id}, description, 
                                choices with fields choice_id and text. (max. of 3 actions choices). choices in description
                                must be enumarated and sent to {chat_id}.
                                Output only in Portuguese (pt-br).
                                """
                                ),
            tools=tools,
            agent=self.agent,
            output_file= "./outputs/event.txt",
            callback=callback,
            human_input=False
        )

    def action_event(self, tools, choice_id, chapter, callback):
        return Task(
            description=dedent(f"""
                                Resolve the user's choice (choice ID: {choice_id}) for 'event_id' in the chapter: '{chapter}' of the game. 
                                This task should conclusively address the outcomes based on the user's decision, ensuring that no new events are initiated as a result. 
                                Analyze the scenario to calculate outcomes, incorporating both positive and negative consequences with a probabilistic approach. 
                                It is essential that not all outcomes are favorable to the player; adverse consequences are also crucial for a balanced and 
                                engaging gameplay experience. 
                                """
                                ),
            expected_output=dedent(f"""The output MUST be ONLY a result JSON formatted dictionary structure for the events='event_id'
                                containing the fields: decision={choice_id}, consequence (an update in game history
                                using 200 maximum tokens) and stats_change containing fields: strength, 
                                intelligence, agility and magic with the respectives values defined by your
                                judgment from -4 to 4. It's not necessary to in all events apply stats changes, in suck
                                cases the value 0 must be attributted. Output only in Portuguese (pt-br) with maximum of 500 tokens.
                                Do not add any comments strings or thoughts.
                                """
                                ),
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
        
    def create_character(self, tools, chat_id, user_id, game_state, callback):
        return Task(
            description=dedent(f"""
                               Create a character for user_id={user_id} contextualized with the game world: {game_state}. 
                               The character must have ONLY user_id={user_id}, game_id={chat_id}, name, background, strength, intelligence, agility, and magic.
                               """),
            expected_output="The output MUST be ONLY a JSON formatted dictionary structure with the character data. Do not add any comments strings. use background field for this.",
            tools=tools,
            agent=self.agent,
            output_file= "./outputs/character.txt",
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