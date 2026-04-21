import warnings

import nest_asyncio
from a2a.types import AgentCard
from dotenv import load_dotenv

# Guard IPython imports — only available in Jupyter/notebook environments
try:
    from IPython.display import Markdown, display
    _IPYTHON_AVAILABLE = True
except ImportError:
    _IPYTHON_AVAILABLE = False


def setup_env() -> None:
    """Initializes the environment by loading .env and applying nest_asyncio."""
    load_dotenv(override=True)
    nest_asyncio.apply()

    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)


def get_env(key: str, default: str | None = None) -> str:
    """
    Fetch an environment variable.
    Raises EnvironmentError if the key is missing and no default is provided.
    """
    import os
    val = os.getenv(key, default)
    if val is None:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return val


def display_agent_card(agent_card: AgentCard) -> None:
    """Nicely formats and displays an AgentCard."""
    if not _IPYTHON_AVAILABLE:
        # Fallback plain-text output when not in a notebook
        print(f"\n--- Agent Card: {agent_card.name} ---")
        print(f"  Description : {agent_card.description}")
        print(f"  Version     : {agent_card.version}")
        print(f"  URL         : {agent_card.url}")
        if agent_card.skills:
            print("  Skills:")
            for skill in agent_card.skills:
                print(f"    - {skill.name}: {skill.description}")
        return

    def esc(text: str) -> str:
        """Escapes pipe characters for Markdown table compatibility."""
        return str(text).replace("|", r"\|")

    md_parts = [
        "### Agent Card Details",
        "| Property | Value |",
        "| :--- | :--- |",
        f"| **Name** | {esc(agent_card.name)} |",
        f"| **Description** | {esc(agent_card.description)} |",
        f"| **Version** | `{esc(agent_card.version)}` |",
        f"| **URL** | [{esc(agent_card.url)}]({agent_card.url}) |",
        f"| **Protocol Version** | `{esc(agent_card.protocol_version)}` |",
    ]

    if agent_card.skills:
        md_parts.extend(
            [
                "\n#### Skills",
                "| Name | Description | Examples |",
                "| :--- | :--- | :--- |",
            ]
        )
        for skill in agent_card.skills:
            examples_str = (
                "<br>".join(f"• {esc(ex)}" for ex in skill.examples)
                if skill.examples
                else "N/A"
            )
            md_parts.append(
                f"| **{esc(skill.name)}** | {esc(skill.description)} | {examples_str} |"
            )

    display(Markdown("\n".join(md_parts)))