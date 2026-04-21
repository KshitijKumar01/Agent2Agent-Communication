import asyncio
import os
from typing import TYPE_CHECKING
 
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from langgraph.prebuilt import create_react_agent
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langgraph_a2a_server import A2AServer
 
from helpers import setup_env, get_env, display_agent_card
 
if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph
 
 
async def build_agent() -> "CompiledStateGraph":
    """
    Builds the LangGraph ReAct agent asynchronously.
    Awaiting get_tools() avoids calling asyncio.run() inside an
    already-running event loop (which causes errors on Python 3.13 / Windows).
    """
    mcp_client = MultiServerMCPClient(
        {
            "find_healthcare_providers": StdioConnection(
                transport="stdio",
                command="python",
                args=["mcpserver.py"],
            )
        }
    )
 
    tools = await mcp_client.get_tools()  # ✅ await directly instead of asyncio.run()
 
    return create_react_agent(
        model=ChatLiteLLM(
            model="gemini/gemini-2.5-flash-lite",
            max_tokens=1000,
        ),
        tools=tools,
        name="HealthcareProviderAgent",
        prompt=(
            "You are a healthcare provider finder. Use the list_doctors tool to search for doctors. "
            "Extract the city and state from the user's message and pass them to the tool. "
            "If the user mentions a specialty (e.g., therapist, psychiatrist, pediatrician), pass it as the specialty parameter. "
            "Always call the tool — never say you cannot search. "
            "Present all results returned by the tool with their name, specialty, and address. "
            "Only share information returned by the tool."
        ),
    )
 
 
def main() -> None:
    print("Running Healthcare Provider Agent")
    setup_env()  # loads .env and applies nest_asyncio
 
    HOST = get_env("AGENT_HOST")
    PORT = int(get_env("PROVIDER_AGENT_PORT"))
 
    # Build the agent using a clean async call
    agent: CompiledStateGraph = asyncio.run(build_agent())
 
    agent_card = AgentCard(
        name="HealthcareProviderAgent",
        description="Find healthcare providers by location and specialty.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="find_healthcare_providers",
                name="Find Healthcare Providers",
                description="Finds providers based on location/specialty.",
                tags=["healthcare", "providers", "doctor", "psychiatrist"],
                examples=[
                    "Are there any Psychiatrists near me in Boston, MA?",
                    "Find a pediatrician in Springfield, IL.",
                ],
            )
        ],
    )

    display_agent_card(agent_card)
 
    server = A2AServer(
        graph=agent,
        agent_card=agent_card,
        host=HOST,
        port=PORT,
    )
 
    server.serve(app_type="starlette")
 
 
if __name__ == "__main__":
    main()