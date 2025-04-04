import streamlit as st
from pathlib import Path
from pages.types import Workflow, Test, Example, CodeSnippet


if "edit_workflow" not in st.session_state or not st.session_state.edit_workflow:
    st.session_state.edit_workflow = Workflow()


if "reset_editor" in st.session_state and st.session_state.reset_editor:
    st.session_state.edit_test = None
    st.session_state.edit_example = None
    st.session_state.edit_code_snippet = None
    for key in st.session_state:
        if key.startswith("tmp_"):
            del st.session_state[key]
    st.session_state.reset_editor = False


def clear_tmp_state(key: str):
    for tmp_key in st.session_state:
        if tmp_key.startswith(f"tmp_state_key_{key}"):
            del st.session_state[tmp_key]
        if tmp_key.startswith(f"tmp_widget_key_{key}"):
            del st.session_state[tmp_key]



st.markdown(
    """
    <style>
    textarea {
        font-family: monospace !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def upsert_test(edit_test: Test):
    for i, test in enumerate(st.session_state.edit_workflow.tests):
        if test.id == edit_test.id:
            st.session_state.edit_workflow.tests[i] = edit_test
            break
    else:
        st.session_state.edit_workflow.tests.append(edit_test)


def upsert_test_code_snippet(edit_code_snippet: CodeSnippet):
    for i, code_snippet in enumerate(st.session_state.edit_test.initial_state):
        if code_snippet.id == edit_code_snippet.id:
            st.session_state.edit_test.initial_state[i] = edit_code_snippet
            break
    else:
        st.session_state.edit_test.initial_state.append(edit_code_snippet)


def get_text_input(name: str, value, key: str, label_visibility: str = "visible"):
    state_key = f"tmp_state_key_{key}"
    widget_key = f"tmp_widget_key_{key}"
    return st.text_input(
        name,
        value=st.session_state[state_key] if state_key in st.session_state else value,
        key=widget_key,
        label_visibility=label_visibility,
        on_change=save_text(state_key=state_key, widget_key=widget_key),
    )


def get_text_area(name: str, value, key: str, label_visibility: str = "visible"):
    state_key = f"tmp_state_key_{key}"
    widget_key = f"tmp_widget_key_{key}"
    return st.text_area(
        name,
        value=st.session_state[state_key] if state_key in st.session_state else value,
        key=widget_key,
        on_change=save_text(state_key=state_key, widget_key=widget_key),
        label_visibility=label_visibility,
    )


def save_text(state_key: str, widget_key: str):
    def save_text_callback():
        st.session_state[state_key] = st.session_state[widget_key]

    return save_text_callback


def render_list_tests():
    tests = st.session_state.edit_workflow.tests

    for test in tests:
        with st.container():
            col1, col2 = st.columns([0.07, 0.93])

            with col1:
                if st.button(
                    "", key=f"delete_test_{test.id}", icon=":material/delete:"
                ):
                    st.session_state.edit_workflow.tests.remove(test)
                    st.rerun()
            with col2:

                def set_edit_test(edit_test: Test):
                    st.session_state.edit_test = edit_test

                st.button(
                    "",
                    key=f"edit_test_{test.id}",
                    icon=":material/edit:",
                    on_click=set_edit_test,
                    args=[test],
                )

            st.json(test.model_dump())
    if not tests:
        st.info("No tests have been added yet")


def render_list_initial_state():
    initial_state = st.session_state.edit_test.initial_state

    for code_snippet in initial_state:
        with st.container():
            col1, col2 = st.columns([0.07, 0.93])

            with col1:
                if st.button(
                    "",
                    key=f"delete_code_snippet_{code_snippet.id}",
                    icon=":material/delete:",
                ):
                    st.session_state.edit_test.initial_state.remove(code_snippet)
                    st.rerun()

            with col2:

                def set_edit_code_snippet(edit_code_snippet: CodeSnippet):
                    st.session_state.edit_code_snippet = edit_code_snippet

                st.button(
                    "",
                    key=f"edit_code_snippet_{code_snippet.id}",
                    icon=":material/edit:",
                    on_click=set_edit_code_snippet,
                    args=[code_snippet],
                )

            st.json(code_snippet.model_dump())
    if not initial_state:
        st.info("No code snippets have been added yet")


def render_edit_test():
    with st.container(border=True):
        st.session_state.edit_test.test_prompt = get_text_area(
            "Test prompt",
            value=st.session_state.edit_test.test_prompt,
            key="edit_test_test_prompt",
        )
        st.session_state.edit_test.expected_outcome = get_text_area(
            "Expected outcome",
            value=st.session_state.edit_test.expected_outcome,
            key="edit_test_expected_outcome",
        )

        st.write("Initial state")
        st.caption("""
            Everything that is relevant for the workflow that needs to be there **before** the agent takes over.
            This includes schemas, queries, inserts, any client code, etc. 
        """)

        if (
            "edit_code_snippet" in st.session_state
            and st.session_state.edit_code_snippet is not None
        ):
            with st.container(border=True):
                st.session_state.edit_code_snippet.url = get_text_input(
                    "URL",
                    value=st.session_state.edit_code_snippet.url,
                    key="edit_test_code_snippet_url",
                )
                st.session_state.edit_code_snippet.code = get_text_area(
                    "Code",
                    value=st.session_state.edit_code_snippet.code,
                    key="edit_test_code_snippet_code",
                )
                st.session_state.edit_code_snippet.language = get_text_input(
                    "Language",
                    value=st.session_state.edit_code_snippet.language,
                    key="edit_test_code_snippet_language",
                )

                def submit_code_snippet():
                    upsert_test_code_snippet(st.session_state.edit_code_snippet)
                    upsert_test(st.session_state.edit_test)
                    clear_tmp_state(key="edit_test_code_snippet")
                    st.session_state.edit_code_snippet = None

                def cancel_code_snippet():
                    st.session_state.edit_code_snippet = None
                    clear_tmp_state(key="edit_test_code_snippet")

                col1, col2 = st.columns([0.5, 0.5])

                with col1:
                    st.button(
                        "Save code snippet",
                        icon=":material/save:",
                        key="save_code_snippet",
                        on_click=submit_code_snippet,
                        use_container_width=True,
                    )

                with col2:
                    st.button(
                        "Cancel",
                        icon=":material/cancel:",
                        key="cancel_code_snippet",
                        on_click=cancel_code_snippet,
                        use_container_width=True,
                    )
        else:
            render_list_initial_state()

        def add_code_snippet():
            st.session_state.edit_code_snippet = CodeSnippet()

        st.button(
            "New code snippet",
            key="add_code_snippet",
            icon=":material/add:",
            on_click=add_code_snippet,
        )

        def submit_test():
            upsert_test(st.session_state.edit_test)
            st.session_state.edit_test = None
            st.session_state.edit_code_snippet = None
            clear_tmp_state(key="edit_test")

        def cancel_test():
            st.session_state.edit_test = None
            st.session_state.edit_code_snippet = None
            clear_tmp_state(key="edit_test")

        _, col1, col2 = st.columns([0.68, 0.15, 0.17])

        with col1:
            st.button(
                "Save", icon=":material/save:", key="save_test", on_click=submit_test
            )

        with col2:
            st.button(
                "Cancel",
                icon=":material/cancel:",
                key="cancel_test",
                on_click=cancel_test,
            )


def render_tests():
    if "edit_test" in st.session_state and st.session_state.edit_test is not None:
        render_edit_test()
    else:
        render_list_tests()

    def add_test():
        st.session_state.edit_test = Test()

    st.button("New test", key="add_test", icon=":material/add:", on_click=add_test)


def upsert_example(edit_example: Example):
    for i, example in enumerate(st.session_state.edit_workflow.examples):
        if example.id == edit_example.id:
            st.session_state.edit_workflow.examples[i] = edit_example
            break
    else:
        st.session_state.edit_workflow.examples.append(edit_example)


def upsert_example_code_snippet(edit_code_snippet: CodeSnippet):
    for i, code_snippet in enumerate(st.session_state.edit_example.code):
        if code_snippet.id == edit_code_snippet.id:
            st.session_state.edit_example.code[i] = edit_code_snippet
            break
    else:
        st.session_state.edit_example.code.append(edit_code_snippet)


def render_list_examples():
    examples = st.session_state.edit_workflow.examples

    for example in examples:
        with st.container():
            col1, col2 = st.columns([0.07, 0.93])

            with col1:
                if st.button(
                    "", key=f"delete_example_{example.id}", icon=":material/delete:"
                ):
                    st.session_state.edit_workflow.examples.remove(example)
                    st.rerun()
            with col2:

                def set_edit_example(edit_example: Example):
                    st.session_state.edit_example = edit_example

                st.button(
                    "",
                    key=f"edit_example_{example.id}",
                    icon=":material/edit:",
                    on_click=set_edit_example,
                    args=[example],
                )

            st.json(example.model_dump())
    if not examples:
        st.info("No examples have been added yet")


def render_edit_example():
    with st.container(border=True):
        st.session_state.edit_example.name = get_text_input(
            "Name", value=st.session_state.edit_example.name, key="edit_example_name"
        )

        st.write("Description")
        st.caption("""
            This is the description of the example.
            The agent will use it to figure out if it wants to fetch this example.
        """)

        st.session_state.edit_example.description = get_text_area(
            "Description",
            value=st.session_state.edit_example.description,
            key="edit_example_description",
            label_visibility="hidden",
        )

        st.write("Instructions")
        st.caption("""
            These are natural language instructions for the agent on how to complete the workflow.
            Should look something like: (1) import foo, (2) run bar, (3) prompt the user for baz.
        """)
        st.session_state.edit_example.instructions = get_text_area(
            "Instructions",
            value=st.session_state.edit_example.instructions,
            key="edit_example_instructions",
            label_visibility="hidden",
        )

        st.write("Code")
        st.caption("""
            This is the code that the agent will reference.

            Can be any relevant piece of code found within the project: a query, a schema, client code, etc.
            Can be the whole file, or only the relevant snippet.
        """)

        if (
            "edit_code_snippet" in st.session_state
            and st.session_state.edit_code_snippet is not None
        ):
            with st.container(border=True):
                st.session_state.edit_code_snippet.url = get_text_input(
                    "URL",
                    value=st.session_state.edit_code_snippet.url,
                    key="edit_example_code_snippet_url",
                )
                st.session_state.edit_code_snippet.code = get_text_area(
                    "Code",
                    value=st.session_state.edit_code_snippet.code,
                    key="edit_example_code_snippet_code",
                )
                st.session_state.edit_code_snippet.language = get_text_input(
                    "Language",
                    value=st.session_state.edit_code_snippet.language,
                    key="edit_example_code_snippet_language",
                )

                def submit_code_snippet():
                    upsert_example_code_snippet(st.session_state.edit_code_snippet)
                    upsert_example(st.session_state.edit_example)
                    clear_tmp_state(key="edit_example_code_snippet")
                    st.session_state.edit_code_snippet = None

                def cancel_code_snippet():
                    st.session_state.edit_code_snippet = None
                    clear_tmp_state(key="edit_example_code_snippet")

                col1, col2 = st.columns([0.5, 0.5])

                with col1:
                    st.button(
                        "Save code snippet",
                        icon=":material/save:",
                        key="save_code_snippet",
                        on_click=submit_code_snippet,
                        use_container_width=True,
                    )

                with col2:
                    st.button(
                        "Cancel",
                        icon=":material/cancel:",
                        key="cancel_code_snippet",
                        on_click=cancel_code_snippet,
                        use_container_width=True,
                    )
        else:
            code = st.session_state.edit_example.code

            for code_snippet in code:
                with st.container():
                    col1, col2 = st.columns([0.07, 0.93])

                    with col1:
                        if st.button(
                            "",
                            key=f"delete_code_snippet_{code_snippet.id}",
                            icon=":material/delete:",
                        ):
                            st.session_state.edit_example.code.remove(code_snippet)
                            st.rerun()

                    with col2:

                        def set_edit_code_snippet(edit_code_snippet: CodeSnippet):
                            st.session_state.edit_code_snippet = edit_code_snippet

                        st.button(
                            "",
                            key=f"edit_code_snippet_{code_snippet.id}",
                            icon=":material/edit:",
                            on_click=set_edit_code_snippet,
                            args=[code_snippet],
                        )

                    st.json(code_snippet.model_dump())
            if not code:
                st.info("No code snippets have been added yet")

        def add_code_snippet():
            st.session_state.edit_code_snippet = CodeSnippet()

        st.button(
            "New code snippet",
            key="add_code_snippet",
            icon=":material/add:",
            on_click=add_code_snippet,
        )

        def submit_example():
            upsert_example(st.session_state.edit_example)
            st.session_state.edit_example = None
            st.session_state.edit_code_snippet = None
            clear_tmp_state(key="edit_example")

        def cancel_example():
            st.session_state.edit_example = None
            st.session_state.edit_code_snippet = None
            clear_tmp_state(key="edit_example")

        _, col1, col2 = st.columns([0.68, 0.15, 0.17])

        with col1:
            st.button(
                "Save",
                icon=":material/save:",
                key="save_example",
                on_click=submit_example,
            )

        with col2:
            st.button(
                "Cancel",
                icon=":material/cancel:",
                key="cancel_example",
                on_click=cancel_example,
            )


def render_examples():
    if "edit_example" in st.session_state and st.session_state.edit_example is not None:
        render_edit_example()
    else:
        render_list_examples()

    def add_example():
        st.session_state.edit_example = Example()

    st.button(
        "New example", key="add_example", icon=":material/add:", on_click=add_example
    )


st.title("Edit workflow")


def upsert_workflow():
    workflows_file = st.session_state.workflows_file
    with workflows_file.open("r") as f:
        all_workflows = [Workflow.model_validate_json(line) for line in f]

    for i, workflow in enumerate(all_workflows):
        if workflow.id == st.session_state.edit_workflow.id:
            all_workflows[i] = st.session_state.edit_workflow
            break
    else:
        all_workflows.append(st.session_state.edit_workflow)

    with workflows_file.open("w") as f:
        for workflow in all_workflows:
            f.write(workflow.model_dump_json() + "\n")

    st.toast("Workflow saved!", icon=":material/check:")


col1, col2, col3 = st.columns([0.07, 0.15, 0.78], vertical_alignment="center")

with col1:
    if st.button(
        "",
        icon=":material/arrow_back:",
        help="Discard unsaved changes and go back to the list",
        key="back_to_list",
    ):
        st.session_state.edit_workflow = None
        st.session_state.edit_test = None
        st.session_state.edit_example = None
        st.session_state.edit_code_snippet = None
        st.switch_page("pages/list_workflows.py")

with col2:
    st.button(
        "Save",
        icon=":material/save:",
        key="save_workflow",
        on_click=upsert_workflow,
        use_container_width=True,
    )

with col3:
    st.write(f"**Workflow ID**: {st.session_state.edit_workflow.id}")


st.session_state.edit_workflow.name = get_text_input(
    "Name", value=st.session_state.edit_workflow.name, key="edit_workflow_name"
)

st.subheader("Tests")
st.caption("""
    This part of the worflow is **for the humans**.

    Tests are what the human tester is putting into the agent as inputs.
    Use any format you want, as long as it would be clear to a human.
""")
render_tests()

st.subheader("MCP examples")
st.caption("""
    This part of the workflow is **for the agent**.

    MCP examples are what the agent will use on its own volition as reference to complete the workflow.
    - A perfect MCP example is brief, atomic, composable and does exactly what it says on the tin.
    - Try to stick to putting a single set of instructions or a code snippet per example, unless it makes sense to have more.
""")
render_examples()
