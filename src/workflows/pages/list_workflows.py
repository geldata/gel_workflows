import streamlit as st
from pages.types import Workflow


st.title("List of all workflows")

st.session_state.edit_workflow = None

workflows = []

with open(st.session_state.workflows_file, "r") as f:
    for line in f:
        workflows.append(Workflow.model_validate_json(line))


for i, workflow in enumerate(workflows):
    col1, col2, col3 = st.columns([0.86, 0.07, 0.07])
    with col1:
        with st.expander(
            f"{workflow.name or 'Untitled'} ({workflow.id})", icon=":material/code:"
        ):
            st.json(workflow.model_dump())

    with col2:
        # def set_edit_workflow(edit_workflow: Workflow):
        #     st.session_state.edit_workflow = edit_workflow
        # st.switch_page("pages/edit_workflow.py")
        # st.button("", icon=":material/edit:", key=f"edit_{i}", on_click=set_edit_workflow, args=[workflow])
        if st.button("", icon=":material/edit:", key=f"edit_{i}"):
            st.session_state.edit_workflow = workflow
            st.switch_page("pages/edit_workflow.py")
    with col3:
        st.button("", icon=":material/delete:", key=f"delete_{i}")

    # st.sidebar.page_link("workflow name")

if "edit_workflow" in st.session_state and st.session_state.edit_workflow:
    print("edit_workflow", st.session_state.edit_workflow)
    # st.switch_page("pages/edit_workflow.py")

# def load_workflows():
#     return []
#
#
# def list_workflows():
#     """Show a list of all workflows with options to view/edit"""
#     st.title("Workflow Manager")
#
#     workflows = load_workflows()
#
#     # Add workflow button
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Add New Workflow", key="add_workflow_btn"):
#             st.session_state.page = "add_workflow"
#             st.session_state.editing_workflow = None
#             st.rerun()
#
#     with col2:
#         # Add download button for exporting workflows.jsonl
#         if os.path.exists(WORKFLOWS_FILE):
#             with open(WORKFLOWS_FILE, "r") as f:
#                 file_content = f.read()
#             st.download_button(
#                 label="Export Workflows",
#                 data=file_content,
#                 file_name="workflows.jsonl",
#                 mime="application/json",
#                 key="export_workflows_btn",
#             )
#
#     if not workflows:
#         st.info("No workflows found. Add a new workflow to get started.")
#         return
#
#     # Display existing workflows
#     st.subheader("Existing Workflows")
#
#     for i, workflow in enumerate(workflows):
#         with st.expander(
#             f"{workflow.workflow_name or 'Untitled'} ({workflow.workflow_id})"
#         ):
#             st.write(f"**ID:** {workflow.workflow_id}")
#             st.write(f"**Name:** {workflow.workflow_name or 'Untitled'}")
#             if workflow.description:
#                 st.write(f"**Description:** {workflow.description}")
#
#             # Test cases
#             st.write(f"**Test Cases:** {len(workflow.test_cases)}")
#             for j, test_case in enumerate(workflow.test_cases):
#                 st.write(f"- Test Case {j + 1}: {test_case.test_id}")
#
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 if st.button("View/Edit", key=f"edit_{i}"):
#                     st.session_state.page = "edit_workflow"
#                     st.session_state.editing_workflow = i
#                     st.rerun()
#             with col2:
#                 if st.button("Add Test Case", key=f"add_test_{i}"):
#                     st.session_state.page = "add_test_case"
#                     st.session_state.editing_workflow = i
#                     st.rerun()
#             with col3:
#                 if st.button("Delete", key=f"delete_{i}"):
#                     del workflows[i]
#                     save_all_workflows(workflows)
#                     st.success("Workflow deleted!")
#                     st.rerun()
