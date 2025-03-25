import streamlit as st
from pages.types import Workflow


st.title("List of all workflows")

st.markdown(
    """
    From here you can browse, edit and delete existing workflows, and create new ones.

    All changes are reflected in the `workflows.jsonl` file that you can commit to the repo once you're done with the changes.
    """,
)

st.divider()

if st.button("New workflow", key="new_workflow", icon=":material/add:"):
    st.session_state.edit_workflow = Workflow()
    st.switch_page("pages/edit_workflow.py")

st.session_state.edit_workflow = None

workflows = []

with open(st.session_state.workflows_file, "r") as f:
    for line in f:
        workflows.append(Workflow.model_validate_json(line))


def save_all_workflows(workflows):
    with open(st.session_state.workflows_file, "w") as f:
        for workflow in workflows:
            f.write(workflow.model_dump_json() + "\n")


for i, workflow in enumerate(workflows):
    col1, col2, col3 = st.columns([0.86, 0.07, 0.07])
    with col1:
        with st.expander(
            f"{workflow.name or 'Untitled'} ({workflow.id})", icon=":material/code:"
        ):
            st.json(workflow.model_dump())

    with col2:
        if st.button("", icon=":material/edit:", key=f"edit_{i}"):
            st.session_state.edit_workflow = workflow
            st.switch_page("pages/edit_workflow.py")
    with col3:
        if st.button("", icon=":material/delete:", key=f"delete_{i}"):
            del workflows[i]
            save_all_workflows(workflows)
            st.rerun()

