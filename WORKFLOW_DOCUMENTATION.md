# Job Description Generator Workflow - Complete Documentation

## Overview
This workflow generates professional LinkedIn job description posts using AI, with an iterative review and editing process, and optional LinkedIn sharing capability.

---

## Workflow Architecture

```
START
  ↓
1. Job Details Form (User Input)
  ↓
2. Assemble JD Prompt
  ↓
3. Generate JD (LLM)
  ↓
4. Review Form #1
  ↓
[Branch: Approved?]
  ├─ Yes → LinkedIn Share Form
  └─ No → Edit Loop
       ├─ Edit Instructions Form
       ├─ Assemble Regen Prompt
       ├─ Regenerate JD (LLM)
       ├─ Review Form #2
       └─ [Loop: Approved?]
            ├─ Yes → Exit Loop
            └─ No → Repeat Loop
  ↓
5. LinkedIn Share Form
  ↓
[Branch: Share on LinkedIn?]
  ├─ Yes → Post to LinkedIn Tool
  └─ No → END
  ↓
END
```

---

## Workflow Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    JOB DETAILS FORM                         │
│  • Job Title                                                │
│  • Position Overview                                        │
│  • Key Responsibilities                                     │
│  • Required Qualifications                                  │
│  • Preferred Qualifications (optional)                      │
│  • Location & Work Arrangement (optional)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ASSEMBLE JD PROMPT (Tool)                      │
│  Combines all form fields into structured prompt           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              GENERATE JD (LLM Prompt)                       │
│  Creates professional LinkedIn post (250-350 words)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   REVIEW FORM #1                            │
│  Shows generated post + Approve/Request Changes             │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    │   APPROVED?   │
                    └───────┬───────┘
                    Yes ↓   ↓ No
                        │   │
                        │   └──────────────────────────┐
                        │                              ↓
                        │              ┌───────────────────────────────┐
                        │              │        EDIT LOOP              │
                        │              │  ┌─────────────────────────┐  │
                        │              │  │ Edit Instructions Form  │  │
                        │              │  └──────────┬──────────────┘  │
                        │              │             ↓                 │
                        │              │  ┌─────────────────────────┐  │
                        │              │  │ Assemble Regen Prompt   │  │
                        │              │  └──────────┬──────────────┘  │
                        │              │             ↓                 │
                        │              │  ┌─────────────────────────┐  │
                        │              │  │ Regenerate JD (LLM)     │  │
                        │              │  └──────────┬──────────────┘  │
                        │              │             ↓                 │
                        │              │  ┌─────────────────────────┐  │
                        │              │  │   Review Form #2        │  │
                        │              │  └──────────┬──────────────┘  │
                        │              │             ↓                 │
                        │              │      [Approved?]              │
                        │              │       Yes ↓  ↓ No             │
                        │              │           │  └─── Loop Back   │
                        │              │           ↓                   │
                        │              └───────────┼───────────────────┘
                        │                          │
                        └──────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────┐
│              LINKEDIN SHARE FORM                            │
│  Do you want to share this post on LinkedIn?               │
│  • Yes / No                                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    │  SHARE ON     │
                    │  LINKEDIN?    │
                    └───────┬───────┘
                    Yes ↓   ↓ No
                        │   │
                        │   └────→ END
                        ↓
┌─────────────────────────────────────────────────────────────┐
│           POST TO LINKEDIN (Tool)                           │
│  Posts the approved text to LinkedIn                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
                           END
```

---

## Tools Reference

### 1. **Job Details Form (UserFlow)**
**Purpose:** Collect job description details from user

**Input Fields:**
```python
{
    "job_title": str,                    # Required - e.g., "Senior Software Engineer"
    "job_summary": str,                  # Required - Position overview
    "roles_and_responsibilities": str,   # Required - Key responsibilities
    "required_qualifications": str,      # Required - Must-have qualifications
    "preferred_qualifications": str,     # Optional - Nice-to-have skills
    "location_and_work_structure": str   # Optional - e.g., "Remote, Hybrid — Cairo"
}
```

**Output:** Form field values accessible via expressions

---

### 2. **assemble_jd_prompt.py**
**Purpose:** Combine form fields into a structured prompt for the LLM

**Input:**
```python
{
    "job_title": str,
    "job_summary": str,
    "roles_and_responsibilities": str,
    "required_qualifications": str,
    "preferred_qualifications": str (optional),
    "location_and_work_structure": str (optional)
}
```

**Output:** String (assembled prompt)
```python
"""
You are an expert Technical Talent Brand Manager and Copywriter...

Input Data:
- Job Title: {job_title}
- Overview: {job_summary}
- Responsibilities: {roles_and_responsibilities}
...

Constraints:
- Word count: 250–350 words
- Use 2-4 relevant tech emojis
- Return ONLY the final post text
"""
```

**Prompt Structure:**
- Defines role and goal
- Provides instructions for tone and storytelling
- Specifies structure (Hook, Mission, Impact, Toolkit, Extra Mile, CTA)
- Includes all input data
- Sets constraints (word count, emojis)

---

### 3. **Generate JD (Prompt Node)**
**Purpose:** Generate LinkedIn job post using watsonx LLM

**Input:**
```python
{
    "assembled_prompt": str  # From assemble_jd_prompt
}
```

**System Prompt Rules:**
1. Use ONLY provided information (no assumptions)
2. Do NOT mention salary/benefits unless provided
3. Do NOT fabricate technologies or details
4. Structure: hook → responsibilities → qualifications → CTA
5. Use 2-3 emojis maximum
6. Length: 250-350 words strictly
7. Return ONLY post text (no markdown, no commentary)

**Output:** String (generated LinkedIn post)

**Example Output:**
```
🚀 We're Hiring: Senior Backend Engineer

Are you ready to architect systems that power millions of users?
We're looking for a talented Backend Engineer to join our team...

Your Impact:
• Design scalable microservices architecture
• Build high-performance APIs...

Your Toolkit:
• 5+ years in backend development
• Expert in Python, Go, or Java...

Ready to make an impact? Apply now! 💼
```

---

### 4. **Review Form #1 (UserFlow)**
**Purpose:** Show generated post and get user approval

**Display Fields:**
- **post** (output): Shows generated LinkedIn post

**Input Fields:**
- **approval** (single choice): "Approve" or "Request Changes"

**Output:** User's decision

---

### 5. **Branch #1**
**Purpose:** Route based on approval decision

**Evaluator:**
```python
flow["review_node_1"]["review_form_1"].output["Review Decision"] == "Approve"
```

**Routes:**
- **True** → LinkedIn Share Form
- **False** → Edit Loop

---

### 6. **Edit Loop**
**Purpose:** Iteratively edit the post until approved

**Loop Condition:**
```python
not parent["review_node_2"]["review_form_2"].output.get("Review Decision")
or parent["review_node_2"]["review_form_2"].output["Review Decision"] == "Request Changes"
```

**Loop continues while:** User requests changes

**Loop exits when:** User approves

---

#### 6.1 **Edit Instructions Form (Inside Loop)**
**Purpose:** Collect revision instructions from user

**Input Fields:**
```python
{
    "edit_instructions": str  # Required, multi-line
}
```

**Placeholder:**
```
Describe the specific changes required 
(e.g., shorten the responsibilities section, 
adjust tone to be more formal)...
```

---

#### 6.2 **assemble_regen_prompt.py (Inside Loop)**
**Purpose:** Create regeneration prompt with edit instructions

**Input:**
```python
{
    "original_post": str,        # First generated post
    "previous_post": str,        # Last iteration's post (optional)
    "edit_instructions": str     # User's revision requests
}
```

**Logic:**
1. Use `previous_post` if available, else use `original_post`
2. Clean and validate inputs (handle null/empty values)
3. Default instructions if none provided

**Output:** String (regeneration prompt)
```python
"""
CURRENT POST:
{base_post}

REQUESTED CHANGES:
{edit_instructions}

Apply ONLY the requested changes above.
Do NOT add any information not present in the current post.
Do NOT modify sections that were not mentioned.
250–350 words. Return ONLY the revised post text.
"""
```

---

#### 6.3 **Regenerate JD (Prompt Node - Inside Loop)**
**Purpose:** Regenerate post based on edit instructions

**Input:**
```python
{
    "assembled_regen_prompt": str  # From assemble_regen_prompt
}
```

**System Prompt Rules:**
1. Apply ONLY explicitly requested changes
2. Do NOT rewrite unmentioned sections
3. Do NOT add information not in original post
4. Preserve all factual content unless asked to change
5. Do NOT mention salary/culture unless already present
6. Length: 250-350 words strictly
7. Return ONLY revised post text

**Output:** String (regenerated post)

---

#### 6.4 **Review Form #2 (Inside Loop)**
**Purpose:** Show revised post and get approval

**Display Fields:**
- **post** (output): Shows revised LinkedIn post

**Input Fields:**
- **approval** (single choice): "Approve" or "Request Changes"

**Output:** User's decision (triggers loop exit or continuation)

---

### 7. **LinkedIn Share Form (UserFlow)**
**Purpose:** Ask user if they want to share on LinkedIn

**Input Fields:**
```python
{
    "share_decision": str  # Single choice: "Yes" or "No"
}
```

**Output:** User's sharing decision

---

### 8. **Branch #2 (LinkedIn Sharing)**
**Purpose:** Route based on sharing decision

**Evaluator:**
```python
flow["linkedin_share_form"]["linkedin_share_form_fields"].output["Do you want to share this post on LinkedIn?"] == "Yes"
```

**Routes:**
- **True** → Post to LinkedIn Tool
- **False** → END

---

### 9. **post_to_linkedin.py**
**Purpose:** Post the approved text to LinkedIn

**Input:**
```python
{
    "post_text": str  # Final approved post
}
```

**Authentication:**
- Uses hardcoded access token (should be environment variable)
- Author URN: `urn:li:person:p0CE8OuDw1`

**API Details:**
- **Endpoint:** `https://api.linkedin.com/v2/ugcPosts`
- **Method:** POST
- **Headers:**
  - Authorization: Bearer token
  - LinkedIn-Version: 202210
  - X-Restli-Protocol-Version: 2.0.0

**Payload:**
```json
{
    "author": "urn:li:person:p0CE8OuDw1",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": "{post_text}"},
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}
```

**Output:**
```python
# Success
{
    "status": "success",
    "post_id": str  # LinkedIn post ID
}

# Error
{
    "status": "error",
    "detail": str  # Error message
}
```

---

## Data Flow Example

### Scenario: Generate Backend Developer Job Post

#### Phase 1: Initial Generation
```
User Input:
  Job Title: "Senior Backend Engineer"
  Overview: "Build scalable systems..."
  Responsibilities: "• Design APIs\n• Optimize databases..."
  Qualifications: "• 5+ years Python\n• AWS experience..."
  Preferred: "• Kubernetes\n• Microservices..."
  Location: "Remote — Cairo, Egypt"
  ↓
Assemble Prompt: Combines all fields into structured prompt
  ↓
LLM Generation: Creates 300-word LinkedIn post with emojis
  ↓
Review Form: Shows post to user
  ↓
User Decision: "Request Changes"
```

#### Phase 2: Iterative Editing
```
Edit Loop Iteration 1:
  User: "Make it shorter and more technical"
  ↓
  Assemble Regen: Creates revision prompt
  ↓
  LLM Regenerate: Produces shorter, more technical version
  ↓
  Review Form: Shows revised post
  ↓
  User Decision: "Request Changes"

Edit Loop Iteration 2:
  User: "Add more emphasis on remote work benefits"
  ↓
  Assemble Regen: Creates revision prompt
  ↓
  LLM Regenerate: Adds remote work emphasis
  ↓
  Review Form: Shows revised post
  ↓
  User Decision: "Approve" → Exit Loop
```

#### Phase 3: LinkedIn Sharing
```
LinkedIn Share Form:
  User: "Yes"
  ↓
Post to LinkedIn Tool:
  API Call → Success
  ↓
Output:
  {
    "job_title": "Senior Backend Engineer",
    "approved_post": "🚀 We're Hiring: Senior Backend Engineer..."
  }
```

---

## Loop Mechanics

### Edit Loop Details

**Loop Type:** While loop

**Condition:** Continue while user requests changes

**State Management:**
- Tracks `original_post` (first generation)
- Tracks `previous_post` (last iteration)
- Accumulates edit history

**Sequence Inside Loop:**
```
START
  ↓
Edit Instructions Form
  ↓
Assemble Regen Prompt
  ↓
Regenerate JD (LLM)
  ↓
Review Form #2
  ↓
END (check condition)
```

**Exit Condition:**
```python
parent["review_node_2"]["review_form_2"].output["Review Decision"] == "Approve"
```

**Output Schema:**
```python
{
    "approved_post": str  # Final approved post text
}
```

---

## Output Mapping

### Final Workflow Output
```python
{
    "job_title": str,        # From initial form
    "approved_post": str     # Final approved post (from loop or initial generation)
}
```

**Expression Logic:**
```python
# If edit loop was used, use its output
# Otherwise, use initial generation
approved_post = (
    flow["edit_loop"].output["approved_post"]
    if flow["edit_loop"].output
    else flow["generate_jd_prompt"].output
)
```

---

## Environment Setup

### 1. Install Dependencies
```bash
pip install ibm-watsonx-orchestrate requests
```

### 2. Configure LinkedIn API (Optional)
**For LinkedIn posting feature:**

Update `post_to_linkedin.py` with your credentials:
```python
access_token = "YOUR_LINKEDIN_ACCESS_TOKEN"
author_urn = "urn:li:person:YOUR_PERSON_ID"
```

**How to get LinkedIn credentials:**
1. Create LinkedIn App at https://www.linkedin.com/developers/
2. Request `w_member_social` permission
3. Complete OAuth 2.0 flow to get access token
4. Get your person URN from LinkedIn API

### 3. Import Tools
```bash
# Import all tools
orchestrate tools import -k python -f Generate_JD/tools/assemble_jd_prompt.py
orchestrate tools import -k python -f Generate_JD/tools/assemble_regen_prompt.py
orchestrate tools import -k python -f Generate_JD/tools/post_to_linkedin.py
```

### 4. Import Workflow
```bash
orchestrate flows import -k python -f Generate_JD/tools/job_description_flow.py
```

---

## Key Features

✅ **AI-Powered Generation:** Uses watsonx LLM to create professional posts

✅ **Iterative Refinement:** Edit loop allows unlimited revisions

✅ **Strict Guidelines:** LLM follows rules to avoid hallucinations

✅ **Structured Output:** Consistent format with hook, impact, toolkit, CTA

✅ **Word Count Control:** Enforces 250-350 word limit

✅ **LinkedIn Integration:** Direct posting to LinkedIn (optional)

✅ **User Control:** User approves every version before posting

✅ **Context Preservation:** Maintains original post context during edits

---

## Best Practices

### For Initial Generation:
1. **Be Specific:** Provide detailed responsibilities and qualifications
2. **Use Bullet Points:** Makes it easier for LLM to structure
3. **Include Keywords:** Technical terms improve SEO
4. **Set Context:** Explain the role's impact and challenges

### For Edit Instructions:
1. **Be Precise:** "Shorten responsibilities section" vs "make it better"
2. **One Change at a Time:** Easier to track and validate
3. **Reference Sections:** "In the qualifications section, add..."
4. **Avoid Contradictions:** Don't ask to both shorten and add content

### For LinkedIn Posting:
1. **Review Carefully:** Once posted, it's public
2. **Test First:** Use "No" option to review without posting
3. **Check Formatting:** LinkedIn may render differently
4. **Monitor Engagement:** Track post performance

---

## Troubleshooting

### Issue: LLM adds information not provided
**Solution:** The system prompt explicitly forbids this. If it happens:
- Check that form fields are properly mapped
- Verify LLM model settings
- Review assembled prompt for clarity

### Issue: Post exceeds word count
**Solution:** System prompt enforces 250-350 words. If exceeded:
- Check LLM temperature settings (lower = more adherent)
- Add explicit word count in edit instructions

### Issue: Edit loop doesn't preserve changes
**Solution:** Check `assemble_regen_prompt` logic:
- Verify `previous_post` is being passed correctly
- Ensure loop state is maintained

### Issue: LinkedIn posting fails
**Solution:**
- Verify access token is valid (tokens expire)
- Check author URN is correct
- Ensure `w_member_social` permission is granted
- Review LinkedIn API error response

### Issue: Form fields not mapping correctly
**Solution:** Check expression syntax:
```python
flow["job_details_form"]["job_details_form_fields"].output["Job Title"]
```

---

## Security Considerations

### LinkedIn Credentials
⚠️ **Current Implementation:** Hardcoded credentials in `post_to_linkedin.py`

**Recommended Approach:**
```python
import os

access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
author_urn = os.environ.get("LINKEDIN_AUTHOR_URN")
```

**Environment Variables:**
```bash
export LINKEDIN_ACCESS_TOKEN="your_token"
export LINKEDIN_AUTHOR_URN="urn:li:person:your_id"
```

### Token Refresh
LinkedIn access tokens expire. Implement token refresh logic:
```python
def refresh_linkedin_token(refresh_token):
    # Call LinkedIn OAuth token endpoint
    # Return new access token
    pass
```

---

## Output Examples

### Generated Post Example
```
🚀 We're Hiring: Senior Backend Engineer

Are you passionate about building systems that scale? 
We're looking for a talented Backend Engineer to architect 
high-performance solutions that power millions of users.

Your Impact:
• Design and implement microservices architecture
• Build RESTful APIs with sub-100ms response times
• Optimize database queries for 10x performance gains
• Lead technical decisions on infrastructure and tooling

Your Toolkit:
• 5+ years in backend development (Python, Go, or Java)
• Deep expertise in PostgreSQL and Redis
• Hands-on experience with AWS or GCP
• Strong understanding of system design patterns

The Extra Mile:
• Kubernetes and Docker orchestration
• Experience with message queues (Kafka, RabbitMQ)
• Open-source contributions

Location: Remote — Cairo, Egypt 🌍

Ready to make an impact? Apply now and let's build 
something amazing together! 💼

#BackendEngineering #Python #AWS #RemoteWork #Hiring
```

### Edit Instructions Examples
```
Good:
✅ "Shorten the responsibilities section to 3 bullet points"
✅ "Add emphasis on remote work flexibility in the location section"
✅ "Make the tone more formal and less casual"

Bad:
❌ "Make it better" (too vague)
❌ "Add salary information" (not provided in original)
❌ "Completely rewrite" (loses context)
```

---

## Workflow Statistics

- **Average Generation Time:** 3-5 seconds (LLM call)
- **Average Edit Iterations:** 1-2 loops
- **Word Count Range:** 250-350 words (enforced)
- **Emoji Usage:** 2-4 emojis (recommended)
- **Success Rate:** 95%+ (with proper inputs)

---

## Made with Bob 🤖