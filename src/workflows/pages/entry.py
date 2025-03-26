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

st.subheader("Testing with Gel MCP server")

st.markdown(
    """
    You can find the source code, as well as more general details about the Gel MCP server in its [repository](https://github.com/geldata/gel-mcp).
    Here we will focus on running the server with Cursor and MCP inspector and loading custom examples.

    #### Setup in Cursor

    Detailed instructions can be found in Cursor's [documentation](https://docs.cursor.com/context/model-context-protocol#configuration-locations).

    1. Create a `.cursor` directory in the root of your project.
    2. In it, create a `mcp.json` file and put the following configuration in it:
    ```json
    {
        "mcpServers": {
            "gel": {
                "command": "uvx",
                "args": [
                    "--refresh",
                    "--directory",
                    "path/to/project/root",
                    "--from",
                    "git+https://github.com/geldata/gel-mcp.git",
                    "gel-mcp",
                    "--workflows-file",
                    "path/to/workflows.jsonl"
                ]
            }
        }
    }
    ```

    You can find the location of the `workflows.jsonl` file by clicking the "folder" button on the **Workflows** page of the Workflow Editor.

    3. Enable the server in **Cursor Settings** (cmd+shift+J) -> **MCP**.
    4. We also recommend using the **Gel's Rules for AI** file to set some basic behaviours for the agent. You can copy this file from [here](https://github.com/geldata/gel-mcp/blob/main/.cursor/rules/gel-rules.mdc) and put it in the `.cursor/rules` directory.
    
    #### Use MCP Inspector

    [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) is the official standalone MCP client that allows you to manually call server's endpoints.
    Use it to make sure the server is working and custom examples get loaded correctly.

    To use it, run:
    ```bash
    npx @modelcontextprotocol/inspector \\
        uvx \\
        --refresh \\
        --directory path/to/project/root \\
        --from git+https://github.com/geldata/gel-mcp \\
        gel-mcp \\
        --workflows-file /path/to/workflows.jsonl
    ```

    #### Import new examples

    When you run the server with `--workflows-file` argument, it will update the examples on startup.
    To see the changes, toggle the server off and on in the settings.
    """
)
