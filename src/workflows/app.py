import streamlit as st
import json
import uuid
import os
from pydantic import BaseModel, Field

# File to save workflows
WORKFLOWS_FILE = "workflows.jsonl"


class GelState(BaseModel):
    description: str | None = None
    dbschema: str | None = None
    data: str | None = None
    queries: str | None = None


class TestCase(BaseModel):
    test_id: str
    prompt: str | None = None
    initial_state: GelState | None = None
    expected_steps: list[str] = []
    expected_outcome: GelState | None = None


class Workflow(BaseModel):
    workflow_id: str
    workflow_name: str | None = None
    description: str | None = None
    test_cases: list[TestCase] = Field(default_factory=list)


def load_workflows():
    """Load all workflows from the JSONL file"""
    workflows = []
    if os.path.exists(WORKFLOWS_FILE):
        with open(WORKFLOWS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        workflow_data = json.loads(line)
                        workflows.append(Workflow.model_validate(workflow_data))
                    except json.JSONDecodeError:
                        st.error(f"Error decoding line: {line}")
                    except Exception as e:
                        st.error(f"Error loading workflow: {e}")
    return workflows


def save_workflow(workflow):
    """Save a workflow to the JSONL file"""
    with open(WORKFLOWS_FILE, "a") as f:
        f.write(workflow.model_dump_json() + "\n")


def save_all_workflows(workflows):
    """Save all workflows, overwriting the file"""
    with open(WORKFLOWS_FILE, "w") as f:
        for workflow in workflows:
            f.write(workflow.model_dump_json() + "\n")


def list_workflows():
    """Show a list of all workflows with options to view/edit"""
    st.title("Workflow Manager")

    workflows = load_workflows()

    # Add workflow button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add New Workflow", key="add_workflow_btn"):
            st.session_state.page = "add_workflow"
            st.session_state.editing_workflow = None
            st.rerun()
    
    with col2:
        # Add download button for exporting workflows.jsonl
        if os.path.exists(WORKFLOWS_FILE):
            with open(WORKFLOWS_FILE, "r") as f:
                file_content = f.read()
            st.download_button(
                label="Export Workflows",
                data=file_content,
                file_name="workflows.jsonl",
                mime="application/json",
                key="export_workflows_btn"
            )

    if not workflows:
        st.info("No workflows found. Add a new workflow to get started.")
        return

    # Display existing workflows
    st.subheader("Existing Workflows")

    for i, workflow in enumerate(workflows):
        with st.expander(
            f"{workflow.workflow_name or 'Untitled'} ({workflow.workflow_id})"
        ):
            st.write(f"**ID:** {workflow.workflow_id}")
            st.write(f"**Name:** {workflow.workflow_name or 'Untitled'}")
            if workflow.description:
                st.write(f"**Description:** {workflow.description}")

            # Test cases
            st.write(f"**Test Cases:** {len(workflow.test_cases)}")
            for j, test_case in enumerate(workflow.test_cases):
                st.write(f"- Test Case {j + 1}: {test_case.test_id}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("View/Edit", key=f"edit_{i}"):
                    st.session_state.page = "edit_workflow"
                    st.session_state.editing_workflow = i
                    st.rerun()
            with col2:
                if st.button("Add Test Case", key=f"add_test_{i}"):
                    st.session_state.page = "add_test_case"
                    st.session_state.editing_workflow = i
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"delete_{i}"):
                    del workflows[i]
                    save_all_workflows(workflows)
                    st.success("Workflow deleted!")
                    st.rerun()


def create_workflow():
    """Create a new workflow"""
    st.title("Create New Workflow")

    # Generate UUID for new workflow
    if "new_workflow_id" not in st.session_state:
        st.session_state.new_workflow_id = str(uuid.uuid4())

    # Workflow basic info
    st.write(f"**Workflow ID:** {st.session_state.new_workflow_id}")
    workflow_name = st.text_input("Workflow Name")
    workflow_description = st.text_area("Workflow Description")

    if st.button("Save Workflow"):
        workflow = Workflow(
            workflow_id=st.session_state.new_workflow_id,
            workflow_name=workflow_name,
            description=workflow_description,
            test_cases=[],
        )
        save_workflow(workflow)
        st.success("Workflow created successfully!")
        # Clear the workflow ID for next time
        if "new_workflow_id" in st.session_state:
            del st.session_state.new_workflow_id
        # Go back to list
        st.session_state.page = "list"
        st.rerun()

    if st.button("Cancel"):
        if "new_workflow_id" in st.session_state:
            del st.session_state.new_workflow_id
        st.session_state.page = "list"
        st.rerun()


def edit_workflow():
    """Edit an existing workflow"""
    workflows = load_workflows()
    workflow_index = st.session_state.editing_workflow

    if workflow_index is None or workflow_index >= len(workflows):
        st.error("Workflow not found")
        st.session_state.page = "list"
        st.rerun()

    workflow = workflows[workflow_index]

    st.title(f"Edit Workflow: {workflow.workflow_name or 'Untitled'}")

    # Workflow basic info
    st.write(f"**Workflow ID:** {workflow.workflow_id}")
    workflow_name = st.text_input("Workflow Name", value=workflow.workflow_name or "")
    workflow_description = st.text_area(
        "Workflow Description", value=workflow.description or ""
    )

    # Test Cases
    st.subheader("Test Cases")

    if not workflow.test_cases:
        st.info("No test cases added yet.")
    else:
        # Display test cases with direct reordering controls
        for i, test_case in enumerate(workflow.test_cases):
            # Add reordering controls above each test case
            col1, col2, col3, col4 = st.columns([6, 1, 1, 1])

            with col1:
                st.write(f"**Test Case {i + 1}: {test_case.test_id}**")

            with col2:
                if st.button("↑", key=f"test_up_{i}") and i > 0:
                    # Swap with the previous test case
                    workflow.test_cases[i], workflow.test_cases[i - 1] = (
                        workflow.test_cases[i - 1],
                        workflow.test_cases[i],
                    )
                    # Update test IDs to reflect new order
                    for j, tc in enumerate(workflow.test_cases):
                        tc.test_id = f"test-{j + 1}"
                    workflows[workflow_index] = workflow
                    save_all_workflows(workflows)
                    st.success(f"Test case moved up")
                    st.rerun()

            with col3:
                if (
                    st.button("↓", key=f"test_down_{i}")
                    and i < len(workflow.test_cases) - 1
                ):
                    # Swap with the next test case
                    workflow.test_cases[i], workflow.test_cases[i + 1] = (
                        workflow.test_cases[i + 1],
                        workflow.test_cases[i],
                    )
                    # Update test IDs to reflect new order
                    for j, tc in enumerate(workflow.test_cases):
                        tc.test_id = f"test-{j + 1}"
                    workflows[workflow_index] = workflow
                    save_all_workflows(workflows)
                    st.success(f"Test case moved down")
                    st.rerun()

            with col4:
                if st.button("X", key=f"test_delete_{i}"):
                    # Remove this test case
                    workflow.test_cases.pop(i)
                    # Update test IDs for all remaining test cases to maintain order
                    for j, tc in enumerate(workflow.test_cases):
                        tc.test_id = f"test-{j + 1}"
                    workflows[workflow_index] = workflow
                    save_all_workflows(workflows)
                    st.success("Test case deleted!")
                    st.rerun()

            # The test case content in expander
            with st.expander(f"Edit Test Case {i + 1}"):
                st.write(f"**Test ID:** {test_case.test_id}")

                # Display prompt
                prompt = st.text_area(
                    f"Prompt", value=test_case.prompt or "", key=f"prompt_{i}"
                )

                # Initial State
                st.subheader("Initial State")
                initial_description = st.text_area(
                    "Description",
                    value=test_case.initial_state.description
                    if test_case.initial_state
                    else "",
                    key=f"initial_description_{i}",
                    height=150,
                )

                # Use monospace for schema
                st.write("Schema (code):")
                initial_schema = st.text_area(
                    "",
                    value=test_case.initial_state.dbschema
                    if test_case.initial_state
                    else "",
                    key=f"initial_schema_{i}",
                    height=150,
                    help="Enter schema code here",
                    label_visibility="collapsed",
                )

                # Use monospace for data
                st.write("Data (code):")
                initial_data = st.text_area(
                    "",
                    value=test_case.initial_state.data
                    if test_case.initial_state
                    else "",
                    key=f"initial_data_{i}",
                    height=250,
                    help="Enter data code here",
                    label_visibility="collapsed",
                )
                
                # Use monospace for queries
                st.write("Queries (code):")
                initial_queries = st.text_area(
                    "",
                    value=test_case.initial_state.queries
                    if test_case.initial_state and test_case.initial_state.queries
                    else "",
                    key=f"initial_queries_{i}",
                    height=150,
                    help="Enter queries here",
                    label_visibility="collapsed",
                )

                # Apply monospace styling
                st.markdown(
                    """<style>
                textarea {
                    font-family: monospace !important;
                }
                </style>""",
                    unsafe_allow_html=True,
                )

                # Expected Steps with improved management
                st.subheader("Expected Steps")

                # Initialize session state for this test case's steps if not present
                steps_key = f"test_case_{i}_steps"
                if steps_key not in st.session_state:
                    st.session_state[steps_key] = (
                        test_case.expected_steps.copy()
                        if test_case.expected_steps
                        else []
                    )

                # Step management
                for step_idx, step in enumerate(st.session_state[steps_key]):
                    col1, col2, col3, col4 = st.columns([6, 1, 1, 1])

                    with col1:
                        new_step = st.text_area(
                            f"Step {step_idx + 1}",
                            value=step,
                            key=f"step_{i}_{step_idx}",
                            height=100,
                        )
                        if new_step != step:
                            st.session_state[steps_key][step_idx] = new_step

                    with col2:
                        if st.button("↑", key=f"up_{i}_{step_idx}") and step_idx > 0:
                            (
                                st.session_state[steps_key][step_idx],
                                st.session_state[steps_key][step_idx - 1],
                            ) = (
                                st.session_state[steps_key][step_idx - 1],
                                st.session_state[steps_key][step_idx],
                            )
                            st.rerun()

                    with col3:
                        if (
                            st.button("↓", key=f"down_{i}_{step_idx}")
                            and step_idx < len(st.session_state[steps_key]) - 1
                        ):
                            (
                                st.session_state[steps_key][step_idx],
                                st.session_state[steps_key][step_idx + 1],
                            ) = (
                                st.session_state[steps_key][step_idx + 1],
                                st.session_state[steps_key][step_idx],
                            )
                            st.rerun()

                    with col4:
                        if st.button("X", key=f"delete_{i}_{step_idx}"):
                            st.session_state[steps_key].pop(step_idx)
                            st.rerun()

                if st.button("Add Step", key=f"add_step_{i}"):
                    st.session_state[steps_key].append("")
                    st.rerun()

                # Expected Outcome
                st.subheader("Expected Outcome")
                outcome_description = st.text_area(
                    "Description",
                    value=test_case.expected_outcome.description
                    if test_case.expected_outcome
                    else "",
                    key=f"outcome_description_{i}",
                    height=150,
                )

                # Use monospace for schema
                st.write("Schema (code):")
                outcome_schema = st.text_area(
                    "",
                    value=test_case.expected_outcome.dbschema
                    if test_case.expected_outcome
                    else "",
                    key=f"outcome_schema_{i}",
                    height=150,
                    help="Enter schema code here",
                    label_visibility="collapsed",
                )

                # Use monospace for data
                st.write("Data (code):")
                outcome_data = st.text_area(
                    "",
                    value=test_case.expected_outcome.data
                    if test_case.expected_outcome
                    else "",
                    key=f"outcome_data_{i}",
                    height=250,
                    help="Enter data code here",
                    label_visibility="collapsed",
                )
                
                # Use monospace for queries
                st.write("Queries (code):")
                outcome_queries = st.text_area(
                    "",
                    value=test_case.expected_outcome.queries
                    if test_case.expected_outcome and test_case.expected_outcome.queries
                    else "",
                    key=f"outcome_queries_{i}",
                    height=150,
                    help="Enter queries here",
                    label_visibility="collapsed",
                )

                # Apply monospace styling
                st.markdown(
                    """<style>
                textarea {
                    font-family: monospace !important;
                }
                </style>""",
                    unsafe_allow_html=True,
                )

                # Save changes to this test case
                if st.button("Save Test Case Changes", key=f"save_test_case_{i}"):
                    workflow.test_cases[i].prompt = prompt

                    # Update initial state
                    if any([initial_description, initial_schema, initial_data, initial_queries]):
                        workflow.test_cases[i].initial_state = GelState(
                            description=initial_description,
                            dbschema=initial_schema,
                            data=initial_data,
                            queries=initial_queries,
                        )
                    else:
                        workflow.test_cases[i].initial_state = None

                    # Update expected steps
                    workflow.test_cases[i].expected_steps = [
                        step for step in st.session_state[steps_key] if step
                    ]

                    # Update expected outcome
                    if any([outcome_description, outcome_schema, outcome_data, outcome_queries]):
                        workflow.test_cases[i].expected_outcome = GelState(
                            description=outcome_description,
                            dbschema=outcome_schema,
                            data=outcome_data,
                            queries=outcome_queries,
                        )
                    else:
                        workflow.test_cases[i].expected_outcome = None

                    workflows[workflow_index] = workflow
                    save_all_workflows(workflows)
                    st.success("Test case updated!")

    # Save changes button for workflow info
    if st.button("Save Workflow Changes"):
        workflow.workflow_name = workflow_name
        workflow.description = workflow_description
        workflows[workflow_index] = workflow
        save_all_workflows(workflows)
        st.success("Workflow updated successfully!")

    # Add test case button
    if st.button("Add Test Case"):
        st.session_state.page = "add_test_case"
        st.rerun()

    # Back button
    if st.button("Back to List"):
        st.session_state.page = "list"
        st.rerun()


def add_test_case():
    """Add a test case to an existing workflow"""
    workflows = load_workflows()
    workflow_index = st.session_state.editing_workflow

    if workflow_index is None or workflow_index >= len(workflows):
        st.error("Workflow not found")
        st.session_state.page = "list"
        st.rerun()

    workflow = workflows[workflow_index]

    st.title(f"Add Test Case to: {workflow.workflow_name or 'Untitled'}")

    # Generate test ID (simple incrementing number)
    test_id = f"test-{len(workflow.test_cases) + 1}"
    st.write(f"**Test ID:** {test_id}")

    prompt = st.text_area("Prompt")

    # Initial State
    st.subheader("Initial State")
    initial_description = st.text_area("Description", key="initial_description", height=150)

    # Use monospace for schema
    st.write("Schema (code):")
    initial_schema = st.text_area(
        "",
        key="initial_schema",
        height=150,
        help="Enter schema code here",
        label_visibility="collapsed",
    )

    # Use monospace for data
    st.write("Data (code):")
    initial_data = st.text_area(
        "",
        key="initial_data",
        height=250,
        help="Enter data code here",
        label_visibility="collapsed",
    )
    
    # Use monospace for queries
    st.write("Queries (code):")
    initial_queries = st.text_area(
        "",
        key="initial_queries",
        height=150,
        help="Enter queries here",
        label_visibility="collapsed",
    )

    # Apply monospace styling
    st.markdown(
        """<style>
    textarea {
        font-family: monospace !important;
    }
    </style>""",
        unsafe_allow_html=True,
    )

    # Expected Steps - dynamic management
    st.subheader("Expected Steps")

    # Initialize session state for steps if not present
    if "new_test_case_steps" not in st.session_state:
        st.session_state.new_test_case_steps = []

    # Display existing steps with controls
    for step_idx, step in enumerate(st.session_state.new_test_case_steps):
        col1, col2, col3, col4 = st.columns([6, 1, 1, 1])

        with col1:
            new_step = st.text_area(
                f"Step {step_idx + 1}", 
                value=step, 
                key=f"new_step_{step_idx}",
                height=100,
            )
            if new_step != step:
                st.session_state.new_test_case_steps[step_idx] = new_step

        with col2:
            if st.button("↑", key=f"new_up_{step_idx}") and step_idx > 0:
                (
                    st.session_state.new_test_case_steps[step_idx],
                    st.session_state.new_test_case_steps[step_idx - 1],
                ) = (
                    st.session_state.new_test_case_steps[step_idx - 1],
                    st.session_state.new_test_case_steps[step_idx],
                )
                st.rerun()

        with col3:
            if (
                st.button("↓", key=f"new_down_{step_idx}")
                and step_idx < len(st.session_state.new_test_case_steps) - 1
            ):
                (
                    st.session_state.new_test_case_steps[step_idx],
                    st.session_state.new_test_case_steps[step_idx + 1],
                ) = (
                    st.session_state.new_test_case_steps[step_idx + 1],
                    st.session_state.new_test_case_steps[step_idx],
                )
                st.rerun()

        with col4:
            if st.button("X", key=f"new_delete_{step_idx}"):
                st.session_state.new_test_case_steps.pop(step_idx)
                st.rerun()

    if st.button("Add Step"):
        st.session_state.new_test_case_steps.append("")
        st.rerun()

    # Expected Outcome
    st.subheader("Expected Outcome")
    outcome_description = st.text_area("Description", key="outcome_description", height=150)

    # Use monospace for schema
    st.write("Schema (code):")
    outcome_schema = st.text_area(
        "",
        key="outcome_schema",
        height=150,
        help="Enter schema code here",
        label_visibility="collapsed",
    )

    # Use monospace for data
    st.write("Data (code):")
    outcome_data = st.text_area(
        "",
        key="outcome_data",
        height=250,
        help="Enter data code here",
        label_visibility="collapsed",
    )
    
    # Use monospace for queries
    st.write("Queries (code):")
    outcome_queries = st.text_area(
        "",
        key="outcome_queries",
        height=150,
        help="Enter queries here",
        label_visibility="collapsed",
    )

    # Save button
    if st.button("Save Test Case"):
        test_case = TestCase(
            test_id=test_id,
            prompt=prompt,
            initial_state=GelState(
                description=initial_description,
                dbschema=initial_schema,
                data=initial_data,
                queries=initial_queries,
            )
            if any([initial_description, initial_schema, initial_data, initial_queries])
            else None,
            expected_steps=[
                step for step in st.session_state.new_test_case_steps if step
            ],
            expected_outcome=GelState(
                description=outcome_description,
                dbschema=outcome_schema,
                data=outcome_data,
                queries=outcome_queries,
            )
            if any([outcome_description, outcome_schema, outcome_data, outcome_queries])
            else None,
        )

        workflow.test_cases.append(test_case)
        workflows[workflow_index] = workflow
        save_all_workflows(workflows)

        # Clear steps for next test case
        st.session_state.new_test_case_steps = []

        st.success("Test case added successfully!")
        st.session_state.page = "edit_workflow"
        st.rerun()

    # Cancel button
    if st.button("Cancel"):
        # Clear steps
        st.session_state.new_test_case_steps = []
        st.session_state.page = "edit_workflow"
        st.rerun()


def main():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "list"
    if "editing_workflow" not in st.session_state:
        st.session_state.editing_workflow = None

    # Navigation based on session state
    if st.session_state.page == "list":
        list_workflows()
    elif st.session_state.page == "add_workflow":
        create_workflow()
    elif st.session_state.page == "edit_workflow":
        edit_workflow()
    elif st.session_state.page == "add_test_case":
        add_test_case()


if __name__ == "__main__":
    main()
