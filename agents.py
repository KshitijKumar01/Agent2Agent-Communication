from pathlib import Path
 
from google import genai
from google.genai import types
 
 
class PolicyAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        """
        Initializes the PolicyAgent.
        GEMINI_API_KEY is picked up automatically from the environment
        (loaded by setup_env() / load_dotenv() in the calling agent).
        """
        self.client = genai.Client()
        self.model_name = model_name
 
        self.system_instruction = (
            "You are an expert insurance agent. You have been provided with a health insurance policy document. "
            "Answer the user's question using ONLY the information in this document. "
            "Do NOT ask the user for their insurance details, member ID, or plan type — you already have the policy document. "
            "If the answer is not in the document, say 'This information is not covered in the provided policy document.'"
        )
 
    def answer_query(self, prompt: str, pdf_path: str) -> str:
        """
        Reads a local PDF and sends it to Gemini to answer the given prompt.
 
        Raises:
            FileNotFoundError: If the PDF does not exist at the given path.
            RuntimeError: If the Gemini API returns an empty response.
        """
        path = Path(pdf_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF document not found at: {pdf_path}")
 
        with path.open("rb") as file:
            pdf_data = file.read()
 
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    max_output_tokens=1024,  # ✅ raised from 300 — complex policy answers need more tokens
                ),
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}") from e
 
        if not response or not response.text:
            raise RuntimeError("Gemini returned an empty response.")
 
        return response.text
 
 
# ---------------------------------------------------------
# Example Usage (Only runs if this file is executed directly)
# ---------------------------------------------------------
if __name__ == "__main__":
    from helpers import setup_env
    setup_env()
 
    agent = PolicyAgent()
    question = "How much would I pay for mental health therapy?"
    doc_path = "data/2026AnthemgHIPSBC.pdf"
 
    print(f"Asking: '{question}' based on {doc_path}...")
 
    try:
        answer = agent.answer_query(prompt=question, pdf_path=doc_path)
        print("\n--- Gemini Response ---")
        print(answer)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"\nError: {e}")