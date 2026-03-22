from agents import Runner, Agent
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

agent = Agent(name="test", instructions="test")

print(f"Runner attributes: {dir(Runner)}")
print(f"Runner.run signature: {Runner.run}")

# Try to see if there is a 'client' or 'session' related method
for attr in dir(Runner):
    if 'client' in attr.lower() or 'session' in attr.lower():
        print(f"Found related attribute: {attr}")

# Check if we can create a session with a client
try:
    from agents import Session
    print(f"Session attributes: {dir(Session)}")
except ImportError:
    print("No Session class found in agents")
