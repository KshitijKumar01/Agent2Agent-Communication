import json
from pathlib import Path
 
from mcp.server.fastmcp import FastMCP
 
# Initialize the server
mcp = FastMCP("doctorserver")
 
# ✅ Resolve data path relative to THIS file's location,
# not the working directory — prevents FileNotFoundError
# when the server is launched as a subprocess from a different directory.
_DATA_PATH = Path(__file__).parent / "data" / "doctors.json"
 
if not _DATA_PATH.is_file():
    raise FileNotFoundError(
        f"doctors.json not found at expected path: {_DATA_PATH}\n"
        "Make sure the 'data/' directory is in the same folder as mcpserver.py."
    )
 
doctors: list = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
 
 
@mcp.tool()
def list_doctors(
    state: str | None = None,
    city: str | None = None,
    specialty: str | None = None,  # ✅ add this
) -> list[dict]:
    """Returns a list of doctors in a specific location, optionally filtered by specialty.

    Args:
        state: Two-letter state code (e.g., "TX" for Texas).
        city: City name (e.g., "Austin").
        specialty: Medical specialty (e.g., "Psychiatrist", "Therapist", "Pediatrician").

    Returns:
        A list of matching doctor records.
    """
    if not state and not city and not specialty:
        return [{"error": "Please provide at least a state, city, or specialty."}]

    target_state = state.strip().lower() if state else None
    target_city = city.strip().lower() if city else None
    target_specialty = specialty.strip().lower() if specialty else None

    results = [
        doc for doc in doctors
        if (not target_state or doc["address"]["state"].lower() == target_state)
        and (not target_city or doc["address"]["city"].lower() == target_city)
        and (not target_specialty or doc.get("specialty", "").lower() == target_specialty)
    ]

    if not results:
        return [{"message": f"No doctors found for state={state}, city={city}, specialty={specialty}."}]

    return results
 
 
if __name__ == "__main__":
    mcp.run(transport="stdio")