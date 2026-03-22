import sys
import os
# Add current dir to path
sys.path.append(os.getcwd())

from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)

tools = [
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
]

for t in tools:
    name = getattr(t, 'name', 'MISSING')
    print(f"Tool {t.__name__}: name={name}")
    # Also check if it's a Tool object from the SDK
    print(f"  Type: {type(t)}")
