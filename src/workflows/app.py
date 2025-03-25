import streamlit as st
from pathlib import Path
from pages.types import Workflow, Example, Test


WORKFLOWS_FILE = Path("workflows.jsonl").resolve()

st.session_state.workflows_file = WORKFLOWS_FILE

st.set_page_config(
    page_title="Workflow Creator",
    page_icon=":material/code:",
)

entry = st.Page("pages/entry.py", title="Instructions", icon=":material/code:")
list_workflows = st.Page("pages/list_workflows.py", title="Workflows", icon=":material/code:")
edit_workflow = st.Page("pages/edit_workflow.py", title="Editor", icon=":material/code:")


def main():
    pg = st.navigation([entry, list_workflows, edit_workflow])
    pg.run()


if __name__ == "__main__":
    main()
