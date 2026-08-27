"""AI chat mode: natural-language INSERT/SELECT, backed by Claude tool use.

Claude never touches the database directly. Every action it can take is one
of the same seven HTTP calls the Manual UI makes to api/ — so every safety
property already built there (parameterized queries via repository/,
insert/select only, the six reject reasons, no UPDATE/DELETE anywhere)
holds regardless of what the model decides to do. This module only ever
translates a tool call into an HTTP request against api/main.py; it holds
no SQL and no direct database access.
"""

from __future__ import annotations

import json
import uuid

import anthropic
import requests
import streamlit as st

import api_client
import components

MODEL = "claude-opus-5"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """You are the assistant for DB_Operations, a small database of \
customers, products, and sales.

Ground rules, non-negotiable:
- You can only INSERT new rows and SELECT existing ones, through the tools \
provided. There is no way to update or delete anything, for you or the \
user — if something was entered wrong, say so plainly; it cannot be \
corrected here.
- Never invent a value the user did not give you — not an email, not a \
SKU, not a price, and especially never a timestamp. If a tool needs \
something you don't have, or the request could mean more than one thing, \
ask exactly one specific clarifying question and wait for the answer. Do \
not guess and proceed.
- A sale's price is whatever the user says it was at the time of that \
sale — it does not have to match the product's current price, and you \
must never substitute the current price for it.
- customer_email and sku for a sale must refer to rows that already \
exist; you do not create them implicitly. If a tool reports either \
unknown, tell the user plainly rather than trying something else.

Style: keep replies short and conversational. After an insert, confirm \
what was recorded in one line. After a lookup, summarize in plain \
language (mention the row count) rather than dumping raw rows — the user \
can switch to Manual mode to see full tables."""

TOOLS = [
    {
        "name": "insert_customer",
        "description": "Register a new customer. Insert-only — cannot be edited or removed afterward.",
        "input_schema": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string"},
                "email": {
                    "type": "string",
                    "description": "Exactly one @, at least one dot after it, no whitespace.",
                },
                "country_code": {
                    "type": "string",
                    "description": "Two-letter ISO country code, e.g. US.",
                },
                "city": {"type": "string", "description": "Optional."},
            },
            "required": ["full_name", "email", "country_code"],
        },
    },
    {
        "name": "insert_product",
        "description": "Add a new product to the catalog. Insert-only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "4-32 chars, uppercase letters, digits, hyphens only.",
                },
                "name": {"type": "string"},
                "category": {"type": "string"},
                "unit_price": {
                    "type": "string",
                    "description": 'Current list price as a string, e.g. "19.99" — never a float.',
                },
                "is_active": {"type": "boolean", "description": "Defaults to true if omitted."},
            },
            "required": ["sku", "name", "category", "unit_price"],
        },
    },
    {
        "name": "record_sale",
        "description": (
            "Record a sale: an existing customer buying a quantity of an existing "
            "product, at a specific price, at a specific time. The customer and "
            "product must already exist — this never creates them. The price is "
            "frozen at the time of the sale, not looked up from the product's "
            "current price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_email": {"type": "string"},
                "sku": {"type": "string"},
                "quantity": {"type": "integer", "description": "A positive integer."},
                "unit_price": {
                    "type": "string",
                    "description": 'The price at the time of this sale, e.g. "189.00".',
                },
                "sold_at": {
                    "type": "string",
                    "description": (
                        "ISO 8601 timestamp, e.g. 2026-01-05T10:15:00Z. Never invent "
                        "this — ask the user if they did not give one."
                    ),
                },
            },
            "required": ["customer_email", "sku", "quantity", "unit_price", "sold_at"],
        },
    },
    {
        "name": "list_customers",
        "description": "Return every customer on file, ordered by email.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_products",
        "description": "Return every product on file, ordered by SKU.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_sales",
        "description": "Return every sale on file, ordered by sale time.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_sales_detail",
        "description": (
            "Return every sale joined with its customer and product details "
            "(names, SKU, category). The most useful read for questions like "
            "'what has this customer bought' or 'how much revenue from this "
            "product'."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]

_GET_TOOLS = {
    "list_customers": "/customers",
    "list_products": "/products",
    "list_sales": "/sales",
    "list_sales_detail": "/sales/detail",
}
_POST_TOOLS = {
    "insert_customer": "/customers",
    "insert_product": "/products",
    "record_sale": "/sales",
}


def _execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Runs one tool call over HTTP against api/main.py. Returns
    (content_for_claude, is_error) — never touches the database directly.
    """
    try:
        if name in _GET_TOOLS:
            response = api_client.get(_GET_TOOLS[name])
            success = 200
        elif name in _POST_TOOLS:
            response = api_client.post(_POST_TOOLS[name], json=tool_input)
            success = 201
        else:
            return f"Unknown tool: {name}", True
    except requests.RequestException as exc:
        return f"Could not reach the API: {exc}", True

    if response.status_code == success:
        return json.dumps(response.json(), default=str), False
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    return json.dumps({"error": detail}), True


def _block_type(block) -> str:
    if isinstance(block, str):
        return "text"
    return block.type if hasattr(block, "type") else block.get("type")


def _blocks(content) -> list:
    """Normalizes a message's content to a list of blocks. Assistant
    content is usually a list from response.content, but an error path
    stores a plain string — iterating that string character-by-character
    would crash the whole transcript render, so wrap it.
    """
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return list(content)


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for block in _blocks(content):
        if _block_type(block) == "text":
            parts.append(block.text if hasattr(block, "text") else block.get("text", ""))
    return "\n".join(p for p in parts if p)


# ---------------------------------------------------------------------
# Conversations — the chat history sidebar's backing store
# ---------------------------------------------------------------------
def _new_conversation() -> dict:
    return {"id": uuid.uuid4().hex, "title": "New chat", "messages": []}


def ensure_state() -> None:
    """Creates the conversation store if absent. Safe to call from either
    the sidebar or the main pane, in any order.
    """
    if not st.session_state.get("conversations"):
        first = _new_conversation()
        st.session_state.conversations = [first]
        st.session_state.active_conversation_id = first["id"]
    if not st.session_state.get("active_conversation_id"):
        st.session_state.active_conversation_id = st.session_state.conversations[0]["id"]


def active_conversation() -> dict:
    ensure_state()
    for conversation in st.session_state.conversations:
        if conversation["id"] == st.session_state.active_conversation_id:
            return conversation
    # Active id pointed at something no longer present — fall back to the
    # newest rather than raising.
    st.session_state.active_conversation_id = st.session_state.conversations[0]["id"]
    return st.session_state.conversations[0]


def start_new_conversation() -> None:
    """Adds a fresh conversation and makes it active — unless the current
    one is still empty, in which case reuse it rather than stacking up
    identical blank entries.
    """
    ensure_state()
    current = active_conversation()
    if not current["messages"]:
        return
    conversation = _new_conversation()
    st.session_state.conversations.insert(0, conversation)
    st.session_state.active_conversation_id = conversation["id"]


def _title_from(prompt: str) -> str:
    prompt = " ".join(prompt.split())
    return prompt if len(prompt) <= 38 else prompt[:37].rstrip() + "…"


def _run_turn(client: anthropic.Anthropic) -> None:
    """Extends the active conversation with the model's turn, executing
    tool calls in a loop, until Claude produces a final text reply — the
    manual agentic loop (no beta dependency).
    """
    messages = active_conversation()["messages"]
    while True:
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            messages.append(
                {"role": "assistant", "content": "Your Claude API key was rejected. Please reconnect with a valid key."}
            )
            return
        except anthropic.APIError as exc:
            messages.append({"role": "assistant", "content": f"Claude API error: {exc}"})
            return

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return

        tool_results = []
        for block in response.content:
            if _block_type(block) != "tool_use":
                continue
            content, is_error = _execute_tool(block.name, block.input)
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": content, "is_error": is_error}
            )
        messages.append({"role": "user", "content": tool_results})


def render(api_key: str) -> None:
    ensure_state()
    conversation = active_conversation()

    components.section_header(
        "AI", "Ask about your data",
        "Insert or look up customers, products, and sales in plain language. "
        "If something's unclear, it'll ask before doing anything.",
    )

    if not conversation["messages"]:
        st.markdown(
            '<div class="empty-state">Nothing here yet — ask a question below to start.<br>'
            '<span style="font-size:0.85rem;">Try "what has Ava bought?" or "add a product '
            'MN-32C-OLED, 32-inch OLED, Displays, 899.00"</span></div>',
            unsafe_allow_html=True,
        )

    for message in conversation["messages"]:
        role = message["role"]
        content = message["content"]
        if role == "user":
            # A user entry whose content is a list is a tool_result batch,
            # not something the person typed — never shown.
            if isinstance(content, str):
                with st.chat_message("user"):
                    st.markdown(content)
            continue
        blocks = _blocks(content)
        tool_calls = [b for b in blocks if _block_type(b) == "tool_use"]
        text = _extract_text(content)
        if not tool_calls and not text:
            continue
        with st.chat_message("assistant"):
            for call in tool_calls:
                name = call.name if hasattr(call, "name") else call.get("name")
                st.caption(f"→ {name.replace('_', ' ')}")
            if text:
                st.markdown(text)

    prompt = st.chat_input('e.g. "add a customer named Ava, ava@example.com, US"')
    if not prompt:
        return

    if not conversation["messages"]:
        conversation["title"] = _title_from(prompt)
    conversation["messages"].append({"role": "user", "content": prompt})

    client = anthropic.Anthropic(api_key=api_key)
    with st.spinner("Thinking…"):
        _run_turn(client)
    st.rerun()
