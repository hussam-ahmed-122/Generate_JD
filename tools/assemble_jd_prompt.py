from typing import Optional
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool(
    name="assemble_jd_prompt",
    description="Assembles job description form fields into a single prompt string for the LLM"
)
def assemble_jd_prompt(
    job_title: str,
    job_summary: str,
    roles_and_responsibilities: str,
    required_qualifications: str,
    preferred_qualifications: Optional[str] = "",
    location_and_work_structure: Optional[str] = ""
) -> str:
    return (
        f"""
        You are an expert Technical Talent Brand Manager and Copywriter. 
        Your goal is to transform the provided raw job details into a high-converting, professional, and engaging LinkedIn Job Post that attracts top-tier {job_title} candidates.

        Instructions:
        1. Tone: Professional yet energetic and innovative. Use "Action Verbs".
        2. Storytelling: Don't just list tasks; describe the impact and the technical challenges.
        3. Structure: 
        - A 'Hook' that grabs attention immediately.
        - 'The Mission' (Contextualize the summary).
        - 'Your Impact' (Rephrase responsibilities to focus on outcomes).
        - 'Your Toolkit' (Qualifications).
        - 'The Extra Mile' (Preferred skills).
        - 'Call to Action' (Encouraging application).
        4. Keywords: Seamlessly integrate technical terms like Python, Go, Kubernetes, and Milvus to ensure SEO visibility.

        Input Data:
        - Job Title: {job_title}
        - Overview: {job_summary}
        - Responsibilities: {roles_and_responsibilities}
        - Qualifications: {required_qualifications}
        - Bonus Points (Preferred): {preferred_qualifications or 'Standard industry bonuses'}
        - Location: {location_and_work_structure or 'Flexible'}

        Constraints:
        - Word count: 250–350 words.
        - Use 2-4 relevant tech emojis.
        - Return ONLY the final post text.
        """
    )