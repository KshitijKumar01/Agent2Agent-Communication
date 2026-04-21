import os
 
import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
 
from helpers import setup_env, get_env
 
 
def main() -> None:
    # ✅ setup_env() must be called INSIDE main(), not at module level.
    # Calling it at module level runs on import, before .env is reliably loaded,
    # and causes int(None) crashes if env vars are missing.
    setup_env()
 
    PORT = int(get_env("RESEARCH_AGENT_PORT"))
    HOST = get_env("AGENT_HOST")
 
    root_agent = LlmAgent(
        model="gemini-2.5-flash-lite",
        name="HealthResearchAgent",
        tools=[google_search],
        description="Provides healthcare information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
        instruction=(
            "You are a healthcare research agent tasked with providing information about health conditions. "
            "Use the google_search tool to find information on the web about options, symptoms, treatments, "
            "and procedures. Cite your sources in your responses. Output all of the information you find."
        ),
    )
 
    print("Running Health Research Agent")
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    uvicorn.run(a2a_app, host=HOST, port=PORT)
 
 
if __name__ == "__main__":
    main()