import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

llm_name = 'gpt-3.5-turbo'

client = OpenAI(api_key=openai_key)

# response = client.chat.completions.create(
#     model=llm_name,
#     messages=[
#         {"role":"system", "content":"you are a helpful assistant"},
#         {"role":"user","content":"who is Mahatma Gandhi?"}
#     ]
# )
# print (response.choices[0].message.content)


class Agent:
    def __init__(self, system=""):
        self.system = system
        self.message = []
        if system:
            self.message.append({"role":"system","content":system})


    def __call__(self, message):
       self.message.append({"role":"user","content":message})
       result =  self.execute()
       self.message.append({"role":"system", "content":result})
       return result

    
    def execute(self):
        response = client.chat.completions.create(
            model=llm_name,
            temperature=0.0,
            messages = self.message
        )
        return response.choices[0].message.content

prompt = """ 
        You run in a loop of thought, action, PAUSE, observation.
        At the end of the loop you output the answer.
        Use thought to describe your thoughts about the question you have been asked.
        Use Action to run one of the actions available to you - then return PAUSE.
        Observation will be the result of running those actions.

        Your available actions are:

        calculate:
        e.g calculate 4 * 7 / 3
        Run a calculation and return the number - uses Python so be sure of using floating point syntax if necessary.
        
        planet_mass:
        e.g. planet_mass: Earth
        returns the mass of the planet in the solar system

        Example session:

        Question: What is the combined mass of Earth and Mars?
        Thought: I should find the mass of each planet using plant_mass.
        Action: plant_mass: Earth
        PAUSE

        You will be called again with this:
        
        Observation: Earth has a mass of 5.972 x 10^24 kg

        You then output:
        
        Answer: Earth has a mass of 5.972 x 10^24 kg

        Next call the agent again with:

        Action: planet_mass: Mars
        PAUSE

        Observation: Mars has a mass of 0.6471 x 10^24 kg

        You then output:

        Answer: Mars has a mass of 0.64171 x 10^24 kg

        Finally, calculate the combined mass.

        Action: calculate: 5.972 + 0.64171
        PAUSE

        Observation: The combined mass is 6.61371 x 10^24 kg

        Answer: The combined mass of Earth and Mars is 6.61371 x 10^24 kg

    """.strip()

def calculate(what):
    return eval(what)

def planet_mass(name):
    masses = {
        "Mercury": 0.33011,
        "Venus": 4.8675,
        "Earth": 5.972,
        "Mars": 0.64171,
        "Jupiter": 1898.19,
        "Saturn": 568.34,
        "Uranus": 86.813,
        "Neptune": 102.413,
    }
    return f'{name} has a mass of {masses[name]} x 10^24 kg'
    
known_actions = {'calculate': calculate, 'planet_mass':planet_mass}

# agent = Agent(system=prompt)
# response = agent("what is the mass of Earth")
# print (response)

# response = planet_mass("Earth")
# print (response)

# next_response = f'Observation: {response}'
# print (next_response)

# response = agent(next_response)
# print (response)

# #all_messages

# print (agent.message)

import re

action_re = re.compile(r"^Action: (\w+): (.*)$")

def query(question, max_turns=5):
    bot = Agent(prompt)
    next_prompt = question
    print (next_prompt)
    i=0
    while i < max_turns:
        i +=1
        result = bot(next_prompt)
        print (result)
        actions = [action_re.match(a) for a in result.split("\n") if action_re.match(a)]
        print (f'Action: {actions}')
        if actions:
            action, action_input = actions[0].groups()
            print (f'action: {action}')
            print (f'action_input: {action_input}')

            if action not in known_actions:
                raise Exception ("Unknown action: {}: {}".format(action, action_input))
            print ("-- running {} {}".format (action, action_input))
            observation = known_actions[action](action_input)
            print ("Observation: ", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return

query("What is the combined mass of Earth and Jupiter and Saturn and Venus")
