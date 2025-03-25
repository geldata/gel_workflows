import streamlit as st
from pages.types import Workflow

st.title("Welcome to the Workflow Editor 👋")

st.markdown(
    """
    It's meant to help you develop Gel MCP server content.

    **How to develop a workflow:**

    1. Chose the right scope: most workflows are about implementing an app feature using Gel.
    2. Add a test case: a test case containts the initial state of the app, the prompts for the agent, and the expected outcome.
    3. Use the testcase to develop examples: add and refine examples every time the agent fails to complete the workflow.
    4. Open a PR with the updated workflow JSON.

    Get started here 👇

    """
)

col1, col2 = st.columns([0.23, 0.77])

with col1:
    if st.button("New workflow", icon=":material/add:", key="new_workflow"):
        st.session_state.edit_workflow = Workflow()
        st.switch_page("pages/edit_workflow.py")

with col2:
    if st.button("Browse workflows", icon=":material/folder:", key="browse_workflows"):
        st.switch_page("pages/list_workflows.py")

st.divider()

st.subheader("Using Gel MCP server with Cursor")

st.markdown(
    """
    **Setup**

    > add setup instructions here

    **Import new examples**

    > add instructions here

    """
)

