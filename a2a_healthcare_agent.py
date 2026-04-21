import asyncio
import os
from typing import Any

from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.adapters.a2a.serve.server import A2AServer, A2AServerConfig
from beeai_framework.adapters.gemini import GeminiChatModel
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.requirements.conditional import (
    ConditionalRequirement,
)
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import EventMeta, GlobalTrajectoryMiddleware
from beeai_framework.serve.utils import LRUMemoryManager
from beeai_framework.tools import Tool
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools.think import ThinkTool

from helpers import setup_env


class ConciseGlobalTrajectoryMiddleware(GlobalTrajectoryMiddleware):
    def _format_prefix(self, meta: EventMeta) -> str:
        prefix = super()._format_prefix(meta)
        return prefix.rstrip(": ")

    def _format_payload(self, value: Any) -> str:
        return ""


def get_env(key: str) -> str:
    """Fetch a required environment variable or raise a clear error."""
    val = os.getenv(key)
    if val is None:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return val


async def initialize_agents(*agents: A2AAgent) -> None:
    """Initialize all A2A agents concurrently in a single event loop."""
    await asyncio.gather(*[agent.check_agent_exists() for agent in agents])


def main() -> None:
    print("Running A2A Orchestrator Agent")
    setup_env()

    # --- Environment Variables ---
    host = get_env("AGENT_HOST")
    policy_agent_port = int(get_env("POLICY_AGENT_PORT"))
    research_agent_port = int(get_env("RESEARCH_AGENT_PORT"))
    provider_agent_port = int(get_env("PROVIDER_AGENT_PORT"))
    healthcare_agent_port = int(get_env("HEALTHCARE_AGENT_PORT"))

    # --- Sub-Agents ---
    policy_agent = A2AAgent(
        url=f"http://{host}:{policy_agent_port}",
        memory=UnconstrainedMemory(),
    )

    research_agent = A2AAgent(
        url=f"http://{host}:{research_agent_port}",
        memory=UnconstrainedMemory(),
    )

    provider_agent = A2AAgent(
        url=f"http://{host}:{provider_agent_port}",
        memory=UnconstrainedMemory(),
    )

    # Initialize all agents in a single event loop (avoids repeated asyncio.run())
    asyncio.run(initialize_agents(policy_agent, research_agent, provider_agent))

    print("\tℹ️", f"{policy_agent.name} initialized")
    print("\tℹ️", f"{research_agent.name} initialized")
    print("\tℹ️", f"{provider_agent.name} initialized")

    # --- Tools ---
    thinktool = ThinkTool()
    policy_tool = HandoffTool(
        target=policy_agent,
        name=policy_agent.name,
        description=policy_agent.agent_card.description,
    )
    research_tool = HandoffTool(
        target=research_agent,
        name=research_agent.name,
        description=research_agent.agent_card.description,
    )
    provider_tool = HandoffTool(
        target=provider_agent,
        name=provider_agent.name,
        description=provider_agent.agent_card.description,
    )

    # --- Orchestrator Agent ---
    healthcare_agent = RequirementAgent(
        name="Healthcare Agent",
        description="A personal concierge for Healthcare Information, customized to your policy.",
        llm=GeminiChatModel(
            "gemini-2.5-flash-lite",
            allow_parallel_tool_calls=True,
        ),
        tools=[thinktool, policy_tool, research_tool, provider_tool],
        requirements=[
            ConditionalRequirement(
                thinktool,
                force_at_step=1,
                force_after=Tool,
                consecutive_allowed=False,
            ),
            ConditionalRequirement(
                policy_tool,
                consecutive_allowed=False,
                max_invocations=1,
            ),
            ConditionalRequirement(
                research_tool,
                consecutive_allowed=False,
                max_invocations=1,
            ),
            ConditionalRequirement(
                provider_tool,
                consecutive_allowed=False,
                max_invocations=1,
            ),
        ],
        role="Healthcare Concierge",
        instructions=(
            f"""You are a concierge for healthcare services. For EVERY user query you MUST call ALL THREE agents before responding:

            1. ALWAYS call `{provider_agent.name}` to find healthcare providers near the user's location.
            
            2. ALWAYS call `{policy_agent.name}` to check what the insurance policy covers for the user's query.
            
            3. ALWAYS call `{research_agent.name}` to search the web for additional information about:
            - How to access the requested healthcare services
            - What the treatment involves
            - Any relevant health tips or recommendations
            
            Combine all three answers into a single detailed response.
            Clearly label which agent provided which information.
            
            IMPORTANT:
            - Only list providers returned by `{provider_agent.name}`
            - Only state insurance details from `{policy_agent.name}`
            - Use `{research_agent.name}` for general health research and how-to guidance"""
        ),
    )

    print("\tℹ️", f"{healthcare_agent.meta.name} initialized")

    # --- Start A2A Server ---
    A2AServer(
        config=A2AServerConfig(
            port=healthcare_agent_port,
            protocol="jsonrpc",
            host=host,
        ),
        memory_manager=LRUMemoryManager(maxsize=100),
    ).register(healthcare_agent, send_trajectory=True).serve()


if __name__ == "__main__":
    main()