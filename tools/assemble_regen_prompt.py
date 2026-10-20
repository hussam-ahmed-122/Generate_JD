from typing import Optional
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool(
    name="assemble_regen_prompt",
    description="Assembles the regeneration prompt from the previous post and revision instructions"
)
def assemble_regen_prompt(
    original_post: str,
    previous_post: Optional[str] = "",
    edit_instructions: Optional[str] = ""
) -> str:
    clean_previous = ""
    if previous_post and isinstance(previous_post, str) and previous_post.strip():
        if previous_post.strip() not in ("null", "None", "{}", "[]"):
            clean_previous = previous_post.strip()

    clean_instructions = ""
    if edit_instructions and isinstance(edit_instructions, str) and edit_instructions.strip():
        if edit_instructions.strip() not in ("null", "None", "{}", "[]"):
            clean_instructions = edit_instructions.strip()

    base_post = clean_previous if clean_previous else original_post

    if not clean_instructions:
        clean_instructions = "Improve clarity and flow while preserving all factual details."

    return (
        f"CURRENT POST:\n{base_post}\n\n"
        f"REQUESTED CHANGES:\n{clean_instructions}\n\n"
        "Apply ONLY the requested changes above. "
        "Do NOT add any information not present in the current post. "
        "Do NOT modify sections that were not mentioned. "
        "250–350 words. Return ONLY the revised post text."
    )