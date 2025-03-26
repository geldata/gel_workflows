from pydantic import BaseModel, Field
import uuid


class CodeSnippet(BaseModel):
    """A piece of code. Can be an entire file or a snippet from a file."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str | None = None
    code: str | None = None
    language: str | None = None


class Example(BaseModel):
    """An example served to the agent via the MCP server to help it complete the workflow."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    code: list[CodeSnippet] = Field(default_factory=list)


class Test(BaseModel):
    """A test case to manually run against the agent"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_prompt: str | None = None
    expected_outcome: str | None = None
    initial_state: list[CodeSnippet] = Field(default_factory=list)


class Workflow(BaseModel):
    """A workflow that describes implementing an app feature using Gel"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str | None = None
    tests: list[Test] = Field(default_factory=list)
    examples: list[Example] = Field(default_factory=list)