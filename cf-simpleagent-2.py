import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

openai_key = os.environ['OPENAI_API_KEY']
llm_name = 'gpt-3.5-turbo'
client = OpenAI(api_key=openai_key)

class Agent:
    def __init__(self, system_prompt=""):
        print ("inside init function")
        self.system_prompt = system_prompt
        self.messages = []
        #create the system prompt for the Agent class is initialized
        if system_prompt:
            print ("appending system prompt")
            self.messages.append({"role":"system", "content":system_prompt})
            print (self.messages)
    # def __init__(self, system=""):
    #     self.system = system
    #     self.messages = []
    #     if system:
    #         self.messages.append({"role": "system", "content": system})
            
    def __call__(self, query):
        print ("inside call function")

        #initalized class is called and given a query.
        self.messages.append({"role":"user","content":query})
        #send the query for execution
        result = self.execute()
        #Add the response to the message to give context to the next query.
        self.messages.append({"role":"assistant", "content":result})
        return result
    
    def execute(self):
        response = client.chat.completions.create(
            temperature=0.0,
            model=llm_name,
            messages=self.messages
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

# Functions for the agent to call
def calculate(what):
    return eval(what)
def planet_mass(planet):
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
    return f'{planet} has a mass of {masses[planet]} x 10^24kg'
known_actions = {"calculate":calculate, "planet_mass": planet_mass}

import re
action_re = re.compile(r"^Action: (\w+): (.*)$")

def query_interactive():
    print ("inside query_interactive")
    bot = Agent(prompt)
    max_turns = int(input("Enter the maximum number of turns: "))
    i=0

    while i < max_turns:
        i +=1
        question = input("You: ")
        result = bot(question)
        actions = [action_re.match(a) for a in result.split("\n") if action_re.match(a)]
        if actions:
            action, action_input = actions[0].groups()
            print (action)
            if action not in known_actions:
                print (f'unknown action {action}: {action_input}')
                continue
            print (f'---running {action} {action_input}')
                         #------function------- function input paramter
            observation = known_actions[action](action_input)
            print (f'Observation: {observation}')
            next_prompt = f'Observation: {observation}'
            result = bot(next_prompt)
            print ("Bot: ",result)
        else:
            print ("no more actions to run")
            break



if __name__ == "__main__":
    query_interactive()
