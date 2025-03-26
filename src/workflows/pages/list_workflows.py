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

col1, col2, col3 = st.columns([0.23, 0.07, 0.7])

with col1:
    if st.button("New workflow", key="new_workflow", icon=":material/add:"):
        st.session_state.edit_workflow = Workflow()
        st.switch_page("pages/edit_workflow.py")

with col2:
    st.download_button(
        "",
        key="export_workflows",
        icon=":material/download:",
        data=st.session_state.workflows_file.read_bytes(),
        file_name="workflows.jsonl",
        mime="application/jsonl",
        help="Export all workflows to a JSONL file",
    )
with col3:

    def show_workflows_path():
        if (
            "show_workflows_path" in st.session_state
            and st.session_state.show_workflows_path
        ):
            st.session_state.show_workflows_path = False
        else:
            st.session_state.show_workflows_path = True

    st.button(
        "",
        icon=":material/folder:",
        key="show_workflows_file_path",
        help="Show the path to the workflows.jsonl file",
        on_click=show_workflows_path,
    )

if "show_workflows_path" in st.session_state and st.session_state.show_workflows_path:
    st.code(st.session_state.workflows_file, language="bash")

st.session_state.edit_workflow = None

workflows = []

with open(st.session_state.workflows_file, "r") as f:
    for line in f:
        workflows.append(Workflow.model_validate_json(line))


def save_all_workflows(workflows):
    with open(st.session_state.workflows_file, "w") as f:
        for workflow in workflows:
            f.write(workflow.model_dump_json() + "\n")


if workflows:
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
else:
    st.info("No workflows have been added yet.")
