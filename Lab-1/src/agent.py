"""Part B — the Claude Agent SDK.

Same input, different surface. Here Claude is given a working folder and its
built-in tools, and it decides its own steps: read the narrative, read the
rubric, work through the five C's, write a credit memo to disk.

The difference worth showing students is not the answer — both parts score the
same application. It is the *shape* of the work. Part A is one call you fully
specify. Part B is a loop the model drives, and you can watch it think.
"""

from __future__ import annotations

import os
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

MODEL = "claude-opus-5"

AGENT_SYSTEM_PROMPT = """You are a credit analyst working inside a folder.

Your job: read the loan application narrative and the rubric, score the \
application against the Five C's, and write a credit memo.

Method:
1. Read rubric.json to learn the weights, level descriptors and decision bands.
2. Read the narrative file.
3. Score each C from 1 to 5. Use null where the narrative gives no evidence.
4. Compute DSCR, LTV and equity injection % from the figures in the narrative \
rather than trusting any ratio it merely asserts.
5. Write your memo to credit_memo.md in the working folder.

Every score must quote the sentence from the narrative that supports it. If the \
narrative is silent on a criterion, say so rather than inferring a value.
"""


def build_options(workspace: Path) -> ClaudeAgentOptions:
    """Confine the agent to the lab folder and pre-approve the tools it needs."""
    return ClaudeAgentOptions(
        system_prompt=AGENT_SYSTEM_PROMPT,
        model=MODEL,
        cwd=str(workspace),
        # Read to load the inputs, Write to produce the memo, Glob to find files.
        allowed_tools=["Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=30,
    )


async def run_agent(narrative_path: Path, workspace: Path):
    """Drive the agent and yield readable progress lines as it works.

    Authentication: the Agent SDK reads ANTHROPIC_API_KEY from the environment.
    The caller sets it from the run-time prompt just before calling this, and
    clears it afterwards — see main.py.
    """
    prompt = (
        f"Score the loan application in {narrative_path.name} against rubric.json, "
        f"then write your credit memo to credit_memo.md."
    )

    async for message in query(prompt=prompt, options=build_options(workspace)):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    yield ("text", block.text)
                else:
                    # Tool calls surface here — this is the agent loop made visible.
                    name = getattr(block, "name", type(block).__name__)
                    yield ("tool", f"Using tool: {name}")
        elif isinstance(message, ResultMessage):
            yield ("result", str(message.result))


def set_api_key(api_key: str) -> None:
    """Hand the run-time key to the SDK for the duration of the run."""
    os.environ["ANTHROPIC_API_KEY"] = api_key.strip()


def clear_api_key() -> None:
    """Remove the key from the environment once the run is finished."""
    os.environ.pop("ANTHROPIC_API_KEY", None)
