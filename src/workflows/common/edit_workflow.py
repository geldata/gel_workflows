import streamlit as st
from pathlib import Path
from common.types import Workflow, Test, Example, CodeExample, StepsExample, CodeSnippet


WORKFLOW_FILE = Path("workflow.json")
WORKFLOW_FILE.touch(exist_ok=True)
with WORKFLOW_FILE.open("r") as f:
    content = f.read()
    if content:
        st.session_state.edit_workflow = Workflow.model_validate_json(content)
    else:
        st.session_state.edit_workflow = Workflow()


def save_workflow():
    with WORKFLOW_FILE.open("w") as f:
        f.write(st.session_state.edit_workflow.model_dump_json())


def upsert_test(edit_test: Test):
    for i, test in enumerate(st.session_state.edit_workflow.tests):
        if test.id == edit_test.id:
            st.session_state.edit_workflow.tests[i] = edit_test
            break
    else:
        st.session_state.edit_workflow.tests.append(edit_test)


def upsert_code_snippet(edit_code_snippet: CodeSnippet):
    for i, code_snippet in enumerate(st.session_state.edit_test.initial_state):
        if code_snippet.id == edit_code_snippet.id:
            st.session_state.edit_test.initial_state[i] = edit_code_snippet
            break
    else:
        st.session_state.edit_test.initial_state.append(edit_code_snippet)


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
                    save_workflow()
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
                    save_workflow()
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
        st.session_state.edit_test.test_prompt = st.text_area(
            "Test prompt", value=st.session_state.edit_test.test_prompt
        )
        st.session_state.edit_test.expected_outcome = st.text_area(
            "Expected outcome", value=st.session_state.edit_test.expected_outcome
        )

        st.write("Initial state")

        if (
            "edit_code_snippet" in st.session_state
            and st.session_state.edit_code_snippet is not None
        ):
            with st.container(border=True):
                st.session_state.edit_code_snippet.url = st.text_input(
                    "URL", value=st.session_state.edit_code_snippet.url
                )
                st.session_state.edit_code_snippet.code = st.text_area(
                    "Code", value=st.session_state.edit_code_snippet.code
                )
                st.session_state.edit_code_snippet.language = st.text_input(
                    "Language", value=st.session_state.edit_code_snippet.language
                )

                def submit_code_snippet():
                    upsert_code_snippet(st.session_state.edit_code_snippet)
                    upsert_test(st.session_state.edit_test)
                    save_workflow()
                    st.session_state.edit_code_snippet = None

                def cancel_code_snippet():
                    st.session_state.edit_code_snippet = None

                col1, col2 = st.columns([0.5, 0.5])

                with col1:
                    st.button(
                        "Save code snippet",
                        icon=":material/save:",
                        on_click=submit_code_snippet,
                        use_container_width=True,
                    )

                with col2:
                    st.button(
                        "Cancel",
                        icon=":material/cancel:",
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
            save_workflow()
            st.session_state.edit_test = None
            st.session_state.edit_code_snippet = None

        def cancel_test():
            st.session_state.edit_test = None
            st.session_state.edit_code_snippet = None

        _, col1, col2 = st.columns([0.68, 0.15, 0.17])

        with col1:
            st.button("Save", icon=":material/save:", on_click=submit_test)

        with col2:
            st.button("Cancel", icon=":material/cancel:", on_click=cancel_test)


def render_tests():
    st.title("Edit workflow")

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

    st.session_state.edit_workflow.name = st.text_input("Name")

    st.subheader("Tests")

    if "edit_test" in st.session_state and st.session_state.edit_test is not None:
        render_edit_test()
    else:
        render_list_tests()

    def add_test():
        st.session_state.edit_test = Test()

    st.button("New test", key="add_test", icon=":material/add:", on_click=add_test)


# st.subheader("MCP examples")

# examples = st.session_state.workflow.examples

# for example in examples:
#     st.json(example.model_dump())

# if not examples:
#     st.info("No examples have been added yet")

# if st.button("Add", key="add_example", icon=":material/add:"):
#     with st.form(key="add_example"):
#         name = st.text_input("Name")
#         slug = st.text_input("Slug")
#         description = st.text_input("Description")
#         st.form_submit_button()

render_tests()
