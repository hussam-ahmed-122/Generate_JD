# Job Description Generator
 
An AI-powered workflow built on **IBM watsonx Orchestrate** that turns a short job-details form into a professional LinkedIn hiring post. You review the result, request edits as many times as you need, and optionally publish it straight to LinkedIn.
 
## Features
 
- **AI generation**: creates a 250–350 word LinkedIn post (hook, responsibilities, qualifications, call to action) using a watsonx LLM.
- **Iterative editing**: an edit loop lets you request changes until you are happy with the post.
- **Anti-hallucination rules**: the LLM is instructed to use only the information you provide, with no invented technologies, salary, or benefits.
- **Human in the loop**: every version is shown for approval before anything is posted.
- **Optional LinkedIn publishing**: posts the approved text directly to your LinkedIn profile.
 
## How It Works
 
```
Job Details Form
      ↓
Assemble JD Prompt  →  Generate JD (LLM)  →  Review
                                               │
                         ┌─────────────────────┴───────────────┐
                      Approve                           Request Changes
                         │                                     ↓
                         │                          ┌─── Edit Loop ───────────┐
                         │                          │ Edit Instructions Form  │
                         │                          │ Assemble Regen Prompt   │
                         │                          │ Regenerate JD (LLM)     │
                         │                          │ Review (repeat if needed)│
                         │                          └────────────┬────────────┘
                         └───────────────┬───────────────────────┘
                                         ↓
                              LinkedIn Share Form
                                         ↓
                          Yes → Post to LinkedIn   |   No → End
```
 
### Steps
 
1. **Job Details Form**: you enter the job information.
2. **Assemble JD Prompt** (`assemble_jd_prompt.py`): combines the form fields into one structured prompt.
3. **Generate JD**: the LLM writes the LinkedIn post.
4. **Review**: you approve the post or request changes.
5. **Edit Loop** (only if changes are requested): you describe the changes, `assemble_regen_prompt.py` builds a revision prompt, and the LLM applies only the requested edits. This repeats until you approve.
6. **LinkedIn Share Form**: you choose whether to publish.
7. **Post to LinkedIn** (`post_to_linkedin.py`): publishes the approved text via the LinkedIn API.
 
## Input Fields
 
| Field | Required | Example |
|---|---|---|
| Job title | Yes | Senior Backend Engineer |
| Job summary | Yes | Position overview |
| Roles and responsibilities | Yes | Key responsibilities |
| Required qualifications | Yes | Must-have skills |
| Preferred qualifications | No | Nice-to-have skills |
| Location and work structure | No | Remote, Hybrid (Cairo) |
 
## Output
 
```python
{
    "job_title": str,
    "approved_post": str   # final approved LinkedIn post
}
```
 
## Project Structure
 
```
Generate_JD/
└── tools/
    ├── assemble_jd_prompt.py      # builds the initial generation prompt
    ├── assemble_regen_prompt.py   # builds the revision prompt for the edit loop
    ├── post_to_linkedin.py        # publishes the post to LinkedIn
    └── job_description_flow.py    # the workflow definition
```
 
## Getting Started
 
### Prerequisites
 
- Python 3.x
- Access to IBM watsonx Orchestrate (ADK / `orchestrate` CLI)
- (Optional) A LinkedIn developer app, for the posting feature
 
### 1. Install dependencies
 
```bash
pip install ibm-watsonx-orchestrate requests
```
 
### 2. Configure LinkedIn (optional)
 
Only needed if you want to publish posts from the workflow.
 
1. Create an app at <https://www.linkedin.com/developers/>.
2. Request the `w_member_social` permission.
3. Complete the OAuth 2.0 flow to get an access token.
4. Get your LinkedIn person URN.
 
Then set them as environment variables (never commit them to the repository):
 
```bash
export LINKEDIN_ACCESS_TOKEN="your_token"
export LINKEDIN_AUTHOR_URN="urn:li:person:your_id"
```
 
and read them in `post_to_linkedin.py`:
 
```python
import os
 
access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
author_urn = os.environ.get("LINKEDIN_AUTHOR_URN")
```
 
### 3. Import the tools
 
```bash
orchestrate tools import -k python -f Generate_JD/tools/assemble_jd_prompt.py
orchestrate tools import -k python -f Generate_JD/tools/assemble_regen_prompt.py
orchestrate tools import -k python -f Generate_JD/tools/post_to_linkedin.py
```
 
### 4. Import the workflow
 
```bash
orchestrate flows import -k python -f Generate_JD/tools/job_description_flow.py
```
 
## Usage Tips
 
**Job details**
- Be specific and use bullet points; it helps the LLM structure the post.
- Include technical keywords relevant to the role.
 
**Edit instructions**
- Be precise: "Shorten the responsibilities section to 3 bullets" works better than "make it better".
- Make one change at a time, and avoid contradictory requests.
- Don't ask for information you didn't provide (for example salary); the LLM is instructed not to invent it.
 
**Publishing**
- Posts are published with **public** visibility, so review carefully.
- Choose "No" at the share step if you only want to generate and review.
 
## Troubleshooting
 
| Problem | What to check |
|---|---|
| LLM adds information you didn't provide | Form fields are mapped correctly; review the assembled prompt |
| Post is outside 250–350 words | Lower the LLM temperature, or state the word count in your edit instructions |
| Edits are lost between iterations | `previous_post` is passed correctly to `assemble_regen_prompt` |
| LinkedIn posting fails | Token not expired, author URN correct, `w_member_social` granted |
| Form values not mapping | Expression syntax, e.g. `flow["job_details_form"]["job_details_form_fields"].output["Job Title"]` |
