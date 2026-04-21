import os
 
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from a2a.utils import new_agent_text_message
 
from agents import PolicyAgent
from helpers import setup_env, get_env, display_agent_card  # use shared helpers for consistency
 
# Path to the insurance PDF — set via env var or fall back to default
POLICY_PDF_PATH = os.getenv("POLICY_PDF_PATH", "data/2026AnthemgHIPSBC.pdf")
 
 
class PolicyAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = PolicyAgent()
 
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        prompt = context.get_user_input()
        try:
            response = self.agent.answer_query(prompt, POLICY_PDF_PATH)
        except FileNotFoundError as e:
            response = f"Error: Policy document not found. ({e})"
        except Exception as e:
            response = f"Error processing your request: {e}"
 
        message = new_agent_text_message(response)
        await event_queue.enqueue_event(message)
 
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        pass
 
 
def main() -> None:
    print("Running A2A Health Insurance Policy Agent")
    setup_env()  # consistent with other agents — loads .env + nest_asyncio
 
    PORT = int(get_env("POLICY_AGENT_PORT"))
    HOST = get_env("AGENT_HOST")
 
    skill = AgentSkill(
        id="insurance_coverage",
        name="Insurance coverage",
        description="Provides information about insurance coverage options and details.",
        tags=["insurance", "coverage"],
        examples=[
            "What does my policy cover?",   # ✅ removed stray backtick that was here
            "Are mental health services included?",
        ],
    )
 
    agent_card = AgentCard(
        name="InsurancePolicyCoverageAgent",
        description="Provides information about insurance policy coverage options and details.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    display_agent_card(agent_card)
 
    request_handler = DefaultRequestHandler(
        agent_executor=PolicyAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
 
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
 
    uvicorn.run(server.build(), host=HOST, port=PORT)
 
 
if __name__ == "__main__":
    main()