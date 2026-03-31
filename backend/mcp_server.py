"""
MCP Server for Customer Success FTE (Hackathon Exercise 1.4).

This server implementation follows the Model Context Protocol (MCP) 
to expose agent tools to any LLM.
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from enum import Enum
from typing import Optional

# Reuse existing tool logic from the specialization phase
from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
    KnowledgeSearchInput,
    TicketInput,
    CustomerHistoryInput,
    EscalationInput,
    ResponseInput,
    Channel
)

# Initialize MCP Server
server = Server("customer-success-fte")

@server.tool("search_knowledge_base")
async def mcp_search_kb(query: str, max_results: int = 5, category: Optional[str] = None) -> str:
    """Search product documentation for relevant information."""
    return await search_knowledge_base(
        KnowledgeSearchInput(query=query, max_results=max_results, category=category)
    )

@server.tool("create_ticket")
async def mcp_create_ticket(
    customer_id: str, 
    issue: str, 
    priority: str = "medium", 
    channel: str = "web_form"
) -> str:
    """Create a support ticket in the CRM system."""
    # Map string channel to Enum
    chan_enum = Channel.WEB_FORM
    if channel == "email": chan_enum = Channel.EMAIL
    elif channel == "whatsapp": chan_enum = Channel.WHATSAPP
    
    return await create_ticket(
        TicketInput(
            customer_id=customer_id,
            issue=issue,
            priority=priority,
            channel=chan_enum
        )
    )

@server.tool("get_customer_history")
async def mcp_get_customer_history(customer_id: str, limit: int = 10) -> str:
    """Get customer's interaction history across ALL channels."""
    return await get_customer_history(
        CustomerHistoryInput(customer_id=customer_id, limit=limit)
    )

@server.tool("escalate_to_human")
async def mcp_escalate(ticket_id: str, reason: str, context: str, urgency: str = "normal") -> str:
    """Escalate a complex ticket to human support."""
    return await escalate_to_human(
        EscalationInput(
            ticket_id=ticket_id,
            reason=reason,
            context=context,
            urgency=urgency
        )
    )

@server.tool("send_response")
async def mcp_send_response(
    ticket_id: str, 
    message: str, 
    channel: str,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None
) -> str:
    """Send response via intended channel."""
    chan_enum = Channel.WEB_FORM
    if channel == "email": chan_enum = Channel.EMAIL
    elif channel == "whatsapp": chan_enum = Channel.WHATSAPP
    
    return await send_response(
        ResponseInput(
            ticket_id=ticket_id,
            message=message,
            channel=chan_enum,
            customer_email=customer_email,
            customer_phone=customer_phone
        )
    )

if __name__ == "__main__":
    # To run: python mcp_server.py
    # By default, uses stdio transport
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    asyncio.run(main())
