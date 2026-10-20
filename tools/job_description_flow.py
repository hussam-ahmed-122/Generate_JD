from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import END, Flow, START, flow
from ibm_watsonx_orchestrate.flow_builder.data_map import DataMap
from ibm_watsonx_orchestrate.flow_builder.types import Assignment
from assemble_jd_prompt import assemble_jd_prompt
from assemble_regen_prompt import assemble_regen_prompt
from post_to_linkedin import post_to_linkedin

class JobDescriptionOutput(BaseModel):
    job_title: str = Field(description="Job title")
    approved_post: str = Field(description="The final approved LinkedIn post")

class PromptInput(BaseModel):
    assembled_prompt: str = Field(description="Assembled prompt for LLM")

class RegenPromptInput(BaseModel):
    assembled_regen_prompt: str = Field(description="Regen prompt for LLM")

class LoopState(BaseModel):
    approved: bool = Field(default=False)

class LoopOutput(BaseModel):
    approved_post: str = Field(description="Final approved post")

@flow(
    name="job_description_workflow",
    display_name="Job Description Generator",
    description="Generate and review a LinkedIn Job Description post.",
    output_schema=JobDescriptionOutput
)
def build_job_description_flow(aflow: Flow = None) -> Flow:

    # ══════════════════════════════════════════════════════════════════════
    # STEP 1: FORM
    # ══════════════════════════════════════════════════════════════════════
    form_userflow = aflow.userflow(name="job_details_form")
    form_node = form_userflow.form(name="job_details_form_fields")
    form_node.text_input_field("job_title",                   "Job Title",                        required=True,  placeholder_text="e.g., Senior Software Engineer")
    form_node.text_input_field("job_summary",                 "Position Overview",                required=True,  single_line=False, placeholder_text="Provide a brief overview of the role and its purpose within the organization...")
    form_node.text_input_field("roles_and_responsibilities",  "Key Responsibilities",             required=True,  single_line=False, placeholder_text="• Lead the design and development of scalable systems...")
    form_node.text_input_field("required_qualifications",     "Required Qualifications",          required=True,  single_line=False, placeholder_text="• Bachelor's degree in Computer Science or equivalent...")
    form_node.text_input_field("preferred_qualifications",    "Preferred Qualifications",         required=False, single_line=False, placeholder_text="• Experience with cloud platforms such as AWS or IBM Cloud...")
    form_node.text_input_field("location_and_work_structure", "Location & Work Arrangement",      required=False, placeholder_text="e.g., Remote, Hybrid — Cairo, Egypt")
    form_userflow.edge(START, form_node)
    form_userflow.edge(form_node, END)

    # ══════════════════════════════════════════════════════════════════════
    # STEP 2: ASSEMBLE
    # ══════════════════════════════════════════════════════════════════════
    assemble_node = aflow.tool(assemble_jd_prompt)
    assemble_node.map_input(input_variable="job_title",
        expression='flow["job_details_form"]["job_details_form_fields"].output["Job Title"]')
    assemble_node.map_input(input_variable="job_summary",
        expression='flow["job_details_form"]["job_details_form_fields"].output["Position Overview"]')
    assemble_node.map_input(input_variable="roles_and_responsibilities",
        expression='flow["job_details_form"]["job_details_form_fields"].output["Key Responsibilities"]')
    assemble_node.map_input(input_variable="required_qualifications",
        expression='flow["job_details_form"]["job_details_form_fields"].output["Required Qualifications"]')
    assemble_node.map_input(input_variable="preferred_qualifications",
        expression='flow["job_details_form"]["job_details_form_fields"].output["Preferred Qualifications"]')
    assemble_node.map_input(input_variable="location_and_work_structure",
        expression='flow["job_details_form"]["job_details_form_fields"].output["Location & Work Arrangement"]')

    # ══════════════════════════════════════════════════════════════════════
    # STEP 3: GENERATE
    # ══════════════════════════════════════════════════════════════════════
    generate_node = aflow.prompt(
        name="generate_jd_prompt",
        display_name="Generate JD",
        input_schema=PromptInput,
        system_prompt=(
            "You are a professional HR copywriter specializing in LinkedIn job posts.\n"
            "STRICT RULES — violating any rule is not acceptable:\n"
            "1. Use ONLY the information explicitly provided in the prompt. "
            "Do NOT invent, assume, or add any detail that is not stated.\n"
            "2. Do NOT mention salary, compensation, benefits, or company culture "
            "unless the user explicitly provided them.\n"
            "3. Do NOT fabricate technologies, tools, team size, or company values.\n"
            "4. Structure: opening hook → responsibilities → qualifications → call-to-action.\n"
            "5. Use 2–3 emojis maximum. Keep paragraphs short and scannable.\n"
            "6. Length: 250–350 words strictly.\n"
            "7. Return ONLY the post text. "
            "No preamble, no commentary, no markdown headers, no explanations."
        ),
        user_prompt=["{assembled_prompt}"]
    )
    generate_node.map_input(input_variable="assembled_prompt",
        expression="flow.assemble_jd_prompt.output")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 4: REVIEW FORM #1
    # ══════════════════════════════════════════════════════════════════════
    review_userflow_1 = aflow.userflow(name="review_node_1")
    review_form_1 = review_userflow_1.form(name="review_form_1")

    post_map_1 = DataMap()
    post_map_1.add(Assignment(
        target_variable="self.input.value",
        value_expression="parent.parent.generate_jd_prompt.output"
    ))
    review_form_1.field_output_field(name="post", label="Generated LinkedIn Post", value=post_map_1)

    choices_1 = DataMap()
    choices_1.add(Assignment(target_variable="self.input.choices", value_expression='["Approve", "Request Changes"]'))
    review_form_1.single_choice_input_field(name="approval", label="Review Decision", required=True, choices=choices_1)

    review_userflow_1.edge(START, review_form_1)
    review_userflow_1.edge(review_form_1, END)

    # ══════════════════════════════════════════════════════════════════════
    # STEP 5: BRANCH
    # ══════════════════════════════════════════════════════════════════════
    branch_1 = aflow.branch(
        evaluator='flow["review_node_1"]["review_form_1"].output["Review Decision"] == "Approve"'
    )

    # ══════════════════════════════════════════════════════════════════════
    # STEP 6: LOOP
    # ══════════════════════════════════════════════════════════════════════
    edit_loop: Flow = aflow.loop(
        name="edit_loop",
        evaluator=(
            'not parent["review_node_2"]["review_form_2"].output.get("Review Decision") '
            'or parent["review_node_2"]["review_form_2"].output["Review Decision"] == "Request Changes"'
        ),
        input_schema=LoopState,
        output_schema=LoopOutput
    )

    # ── EDIT FORM ────────────────────────────────────────────────────
    loop_edit_userflow = edit_loop.userflow(name="edit_node")
    loop_edit_form = loop_edit_userflow.form(name="edit_form")
    loop_edit_form.text_input_field(
        name="edit_instructions", label="Revision Instructions",
        required=True, single_line=False,
        placeholder_text="Describe the specific changes required (e.g., shorten the responsibilities section, adjust tone to be more formal)..."
    )
    loop_edit_userflow.edge(START, loop_edit_form)
    loop_edit_userflow.edge(loop_edit_form, END)

    # ── ASSEMBLE REGEN ───────────────────────────────────────────────
    loop_assemble_regen = edit_loop.tool(assemble_regen_prompt)
    loop_assemble_regen.map_input(
        input_variable="original_post",
        expression="parent.parent.generate_jd_prompt.output"
    )
    loop_assemble_regen.map_input(
        input_variable="previous_post",
        expression=(
            'parent.regenerate_jd_prompt.output '
            'if parent.get("regenerate_jd_prompt") '
            'else parent.parent.generate_jd_prompt.output'
        )
    )
    loop_assemble_regen.map_input(
        input_variable="edit_instructions",
        expression='parent["edit_node"]["edit_form"].output["Revision Instructions"]'
    )

    # ── REGENERATE PROMPT ────────────────────────────────────────────
    loop_regenerate = edit_loop.prompt(
        name="regenerate_jd_prompt",
        display_name="Regenerate JD",
        input_schema=RegenPromptInput,
        system_prompt=(
            "You are a professional HR copywriter revising an existing LinkedIn job post.\n"
            "STRICT RULES — violating any rule is not acceptable:\n"
            "1. Apply ONLY the changes explicitly requested by the user. "
            "Do NOT rewrite sections that were not mentioned.\n"
            "2. Do NOT add any information that was not present in the original post "
            "or the user's instructions — no invented details, technologies, or benefits.\n"
            "3. Preserve all factual content from the original post unless the user "
            "explicitly asked to remove or change it.\n"
            "4. Do NOT mention salary, compensation, or company culture unless already "
            "present in the original post.\n"
            "5. Length: 250–350 words strictly.\n"
            "6. Return ONLY the complete revised post text. "
            "No commentary, no explanation, no markdown headers."
        ),
        user_prompt=["{assembled_regen_prompt}"]
    )
    loop_regenerate.map_input(input_variable="assembled_regen_prompt",
        expression="parent.assemble_regen_prompt.output")

    # ── REVIEW FORM #2 ───────────────────────────────────────────────
    loop_review_userflow = edit_loop.userflow(name="review_node_2")
    loop_review_form = loop_review_userflow.form(name="review_form_2")

    post_map_2 = DataMap()
    post_map_2.add(Assignment(
        target_variable="self.input.value",
        value_expression="parent.parent.regenerate_jd_prompt.output"
    ))
    loop_review_form.field_output_field(name="post", label="Revised LinkedIn Post", value=post_map_2)

    choices_2 = DataMap()
    choices_2.add(Assignment(target_variable="self.input.choices", value_expression='["Approve", "Request Changes"]'))
    loop_review_form.single_choice_input_field(name="approval", label="Review Decision", required=True, choices=choices_2)

    loop_review_userflow.edge(START, loop_review_form)
    loop_review_userflow.edge(loop_review_form, END)

    # ── WIRE EDGES (loop) ────────────────────────────────────────────
    edit_loop.sequence(
        START,
        loop_edit_userflow,
        loop_assemble_regen,
        loop_regenerate,
        loop_review_userflow,
        END
    )

    # ══════════════════════════════════════════════════════════════════════
    # STEP 7: LINKEDIN SHARING FORM
    # ══════════════════════════════════════════════════════════════════════
    linkedin_share_userflow = aflow.userflow(name="linkedin_share_form")
    linkedin_share_form = linkedin_share_userflow.form(name="linkedin_share_form_fields")
    
    linkedin_choices = DataMap()
    linkedin_choices.add(Assignment(target_variable="self.input.choices", value_expression='["Yes", "No"]'))
    linkedin_share_form.single_choice_input_field(
        name="share_decision",
        label="Do you want to share this post on LinkedIn?",
        required=True,
        choices=linkedin_choices
    )
    
    linkedin_share_userflow.edge(START, linkedin_share_form)
    linkedin_share_userflow.edge(linkedin_share_form, END)

    # ══════════════════════════════════════════════════════════════════════
    # STEP 8: LINKEDIN SHARING BRANCH
    # ══════════════════════════════════════════════════════════════════════
    linkedin_branch = aflow.branch(
        evaluator='flow["linkedin_share_form"]["linkedin_share_form_fields"].output["Do you want to share this post on LinkedIn?"] == "Yes"'
    )

    # ══════════════════════════════════════════════════════════════════════
    # STEP 9: POST TO LINKEDIN TOOL
    # ══════════════════════════════════════════════════════════════════════
    post_linkedin_node = aflow.tool(post_to_linkedin)
    post_linkedin_node.map_input(
        input_variable="post_text",
        expression=(
            'flow["edit_loop"].output["approved_post"] '
            'if flow["edit_loop"].output '
            'else flow["generate_jd_prompt"].output'
        )
    )

    # ══════════════════════════════════════════════════════════════════════
    # WIRE EDGES — main flow
    # ══════════════════════════════════════════════════════════════════════
    aflow.sequence(START, form_userflow, assemble_node, generate_node, review_userflow_1, branch_1)
    branch_1.case(True, linkedin_share_userflow).case(False, edit_loop)
    aflow.edge(edit_loop, linkedin_share_userflow)
    aflow.edge(linkedin_share_userflow, linkedin_branch)
    linkedin_branch.case(True, post_linkedin_node).case(False, END)
    aflow.edge(post_linkedin_node, END)

    # ══════════════════════════════════════════════════════════════════════
    # OUTPUT MAP
    # ══════════════════════════════════════════════════════════════════════
    aflow.map_output(
        output_variable="job_title",
        expression='flow["job_details_form"]["job_details_form_fields"].output["Job Title"]'
    )
    aflow.map_output(
        output_variable="approved_post",
        expression=(
            'flow["edit_loop"].output["approved_post"] '
            'if flow["edit_loop"].output '
            'else flow["generate_jd_prompt"].output'
        )
    )

    return aflow