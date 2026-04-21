# 🏥 A2A Healthcare Multi-Agent System

A production-style **multi-agent AI system** built using the **Agent-to-Agent (A2A) Protocol**, where specialized AI agents collaborate in real-time to answer complex healthcare queries — finding providers, checking insurance coverage, and researching treatments simultaneously.

> Built after completing **"A2A: The Agent2Agent Protocol"** by Google Cloud & IBM Research (instructors: Holt Skinner, Ivan Nardini, Sandi Besen)

---

## 🎯 What It Does

Ask a single question like:
> *"I'm based in Austin, TX. Find me a mental health therapist and what does my insurance cover?"*

And 4 specialized agents collaborate to answer it:

| Agent | Role | Technology |
|-------|------|------------|
| 🧠 **Healthcare Orchestrator** | Receives query, delegates to sub-agents, synthesizes final answer | BeeAI + Gemini |
| 🏨 **Healthcare Provider Agent** | Finds doctors by location and specialty | LangGraph + FastMCP |
| 📄 **Insurance Policy Agent** | Reads PDF policy and answers coverage questions | Google Genai SDK |
| 🔍 **Health Research Agent** | Searches the web for treatment info and how-to guidance | Google ADK + Google Search |

---

## 🏗️ Architecture

```
                        ┌─────────────────────────┐
                        │     A2A Client           │
                        │  (a2a_healthcare_client) │
                        └────────────┬────────────┘
                                     │ JSON-RPC
                                     ▼
                        ┌─────────────────────────┐
                        │  Healthcare Orchestrator │
                        │  (RequirementAgent)      │
                        │  Port: HEALTHCARE_PORT   │
                        └────┬──────┬──────┬──────┘
                             │      │      │
               HandoffTool   │      │      │   HandoffTool
                    ┌────────┘      │      └────────┐
                    ▼               │               ▼
        ┌───────────────────┐       │   ┌───────────────────┐
        │  Provider Agent   │       │   │  Research Agent   │
        │  (LangGraph+MCP)  │       │   │  (Google ADK)     │
        │  Port: PROVIDER   │       │   │  Port: RESEARCH   │
        └─────────┬─────────┘       │   └───────────────────┘
                  │                 │ HandoffTool
           MCP stdio               ▼
                  │   ┌───────────────────┐
        ┌─────────┴─┐ │   Policy Agent    │
        │ mcpserver │ │  (Gemini + PDF)   │
        │ doctors   │ │  Port: POLICY     │
        │ .json     │ └───────────────────┘
        └───────────┘
```

---

## 🛠️ Tech Stack

- **[BeeAI Framework](https://github.com/i-am-bee/beeai-framework)** — Orchestrator agent and A2A server
- **[LangGraph](https://github.com/langchain-ai/langgraph)** — ReAct agent for provider search
- **[Google ADK](https://google.github.io/adk-docs/)** — Research agent with Google Search
- **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP server for doctor database
- **[LiteLLM](https://github.com/BerriAI/litellm)** — Unified LLM interface
- **[Google Gemini 2.5 Flash Lite](https://deepmind.google/technologies/gemini/)** — LLM across all agents
- **A2A Protocol** — Agent-to-agent communication via JSON-RPC
- **Starlette + Uvicorn** — HTTP microservices for each agent

---

## 📁 Project Structure

```
A2A_agent/
├── data/
│   ├── doctors.json              # Doctor database (location + specialty)
│   └── 2026AnthemgHIPSBC.pdf    # Insurance policy document
│
├── a2a_healthcare_agent.py       # Orchestrator — main entry point
├── a2a_healthcare_client.py      # Client to query the orchestrator
├── a2a_policy_agent.py           # Insurance policy agent (HTTP server)
├── a2a_provider_agent.py         # Healthcare provider agent (HTTP server)
├── a2a_research_agent.py         # Health research agent (HTTP server)
├── agents.py                     # PolicyAgent class (Gemini + PDF)
├── mcpserver.py                  # MCP server exposing list_doctors tool
├── helpers.py                    # Shared utilities (setup_env, display_agent_card)
└── .env                          # Environment variables
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/a2a-healthcare-agent.git
cd a2a-healthcare-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Agent Network
AGENT_HOST=localhost
POLICY_AGENT_PORT=9999
RESEARCH_AGENT_PORT=9998
PROVIDER_AGENT_PORT=9997
HEALTHCARE_AGENT_PORT=9996

# Optional: Custom PDF path
POLICY_PDF_PATH=data/2026AnthemgHIPSBC.pdf
```

Get your Gemini API key at: https://aistudio.google.com/app/apikey

---

## 🚀 Running the System

Each agent runs as an independent process. Open **4 separate terminals**:

**Terminal 1 — Policy Agent**
```bash
python a2a_policy_agent.py
```

**Terminal 2 — Research Agent**
```bash
python a2a_research_agent.py
```

**Terminal 3 — Provider Agent**
```bash
python a2a_provider_agent.py
```

**Terminal 4 — Healthcare Orchestrator**
```bash
python a2a_healthcare_agent.py
```

**Terminal 5 — Run the Client**
```bash
python a2a_healthcare_client.py
```

> ⚠️ Start agents in the order above. The orchestrator must start last as it connects to all sub-agents on startup.

---

## 💬 Example Query

```python
# In a2a_healthcare_client.py
response = await agent.run(
    "I'm based in Austin, TX (city=Austin, state=TX). "
    "Find me mental health providers with specialty=Psychiatry in my area. "
    "Also, what does my insurance policy cover for mental health therapy?"
)
```

**Expected output combines:**
- ✅ List of psychiatrists in Austin, TX from the doctor database
- ✅ Insurance coverage details extracted from the PDF policy
- ✅ Web research on how to access mental health services

---

## 🔗 Agent Cards

Once all agents are running, view their capabilities at:

```
GET http://localhost:9999/.well-known/agent-card.json   # Policy Agent
GET http://localhost:9998/.well-known/agent-card.json   # Research Agent
GET http://localhost:9997/.well-known/agent-card.json   # Provider Agent
GET http://localhost:9996/.well-known/agent-card.json   # Healthcare Orchestrator
```

---

## 🧠 Key Concepts Demonstrated

- **Agent-to-Agent (A2A) Protocol** — Standardized communication between independent AI agents
- **Agent Cards** — Self-describing capability manifests for agent discovery
- **HandoffTool** — Delegating tasks from orchestrator to specialist agents
- **MCP (Model Context Protocol)** — Structured tool serving via stdio
- **ReAct Agent Pattern** — Reasoning + Acting loop for tool-use decisions
- **Multi-agent Orchestration** — Coordinating parallel agent calls and synthesizing results

---

## 📚 Learning Resources

- [A2A Protocol Specification](https://google.github.io/A2A/)
- [BeeAI Framework Docs](https://i-am-bee.github.io/beeai-framework/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Google ADK Docs](https://google.github.io/adk-docs/)
- [FastMCP Docs](https://gofastmcp.com/)
- 🎓 Course: **"A2A: The Agent2Agent Protocol"** — Google Cloud & IBM Research on DeepLearning.AI

---

## 🙏 Acknowledgements

This project was built after completing the **A2A: The Agent2Agent Protocol** short course by:
- **Holt Skinner** — Google Cloud
- **Ivan Nardini** — Google Cloud
- **Sandi Besen** — IBM Research

Available at [DeepLearning.AI](https://www.deeplearning.ai/)

---

## 📄 License

MIT License — feel free to use, modify, and build on this project.
