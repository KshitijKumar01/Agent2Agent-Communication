import asyncio
import os
from typing import Any
 
from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import EventMeta, GlobalTrajectoryMiddleware
 
from helpers import setup_env, get_env
 
 
class ConciseGlobalTrajectoryMiddleware(GlobalTrajectoryMiddleware):
    def _format_prefix(self, meta: EventMeta) -> str:
        prefix = super()._format_prefix(meta)
        return prefix.rstrip(": ")
 
    def _format_payload(self, value: Any) -> str:
        return ""
 
 
async def main() -> None:
    setup_env()
 
    host = get_env("AGENT_HOST")
    healthcare_agent_port = int(get_env("HEALTHCARE_AGENT_PORT"))
 
    agent = A2AAgent(
        url=f"http://{host}:{healthcare_agent_port}",
        memory=UnconstrainedMemory(),
    )
 
    response = await agent.run(
        "I'm based in Austin, TX (city=Austin, state=TX). "
        "Find me mental health providers with specialty=Psychiatry in my area. "
        "Also, what does my insurance policy cover for mental health therapy and psychiatry services?"
    ).middleware(ConciseGlobalTrajectoryMiddleware())
    # Guard against failed/empty response
    if response and response.last_message and response.last_message.text:
        print(response.last_message.text)
    else:
        print("Agent did not return a valid response. Check the server logs for details.")
 
 
if __name__ == "__main__":
    asyncio.run(main())