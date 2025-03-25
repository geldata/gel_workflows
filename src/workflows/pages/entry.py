import streamlit as st

st.markdown(
    """
    This is an app to create and manage Gel MCP server content.

    How to use:

    1. Add a new workflow: most workflows involve implementing an app feature using Gel.
    2. Add a test case: a test case containts the initial state of the app, the prompts for the agent, and the expected outcome.
    3. Use the testcase to develop examples: add and refine examples every time the agent fails to complete the workflow.

    How to set up the MCP server:

    > add setup instructions here

    How to import new examples into the MCP server:

    > add instructions here

    """
)

st.sidebar.button("Add New Workflow", icon=":material/add:")
