import streamlit as st


st.title("List of all workflows")


workflows = ["a", "b", "c"]

for i, workflow in enumerate(workflows):
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.75, 0.1, 0.15])
        with col1:
            st.write("workflow name")
        with col2:
            st.button("Edit", key=f"edit_{i}")
        with col3:
            st.button("Delete", key=f"detele_{i}")

    st.sidebar.write("workflow name")



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
