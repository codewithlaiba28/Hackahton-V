import os
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["OPENAI_BASE_URL"] = "https://test.api/v1"

from agents import Runner, Agent
# Some SDKs have a global config object
try:
    import agents
    print(f"Agents version: {getattr(agents, 'version', 'unknown')}")
except:
    pass

# Try to run a dummy to see where it hits
# (We can't easily see where it hits without a mock server or traffic sniffing)

# But we can check if there's a way to SET the client explicitly.
# Based on my earlier grep, I can't read the files.
