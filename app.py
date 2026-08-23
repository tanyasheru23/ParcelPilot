import streamlit as st
import uuid

from src.auth import authenticate_user
from src.agent import graph

from langchain.messages import AIMessage, ToolMessage

from langgraph.types import Command


def render_escalation_confirmation(config):
    """
    Render the Confirm/Cancel controls for a pending escalation and
    handle whichever action the user takes.

    Uses fixed, explicit widget keys so this can be called from more
    than one place in the script — inline, right when the interrupt
    is first detected (same run, no extra st.rerun()), or from the
    top-of-script recovery block on a later rerun (e.g. after a
    button click or a page reload) — while Streamlit still correctly
    tracks which button was clicked.
    """

    st.warning(
        "⚠️ ParcelPilot needs your confirmation before creating "
        "the escalation."
    )

    col1, col2 = st.columns(2)

    with col1:
        confirm_clicked = st.button(
            "✅ Confirm Escalation",
            key="confirm_escalation_btn",
        )

    with col2:
        cancel_clicked = st.button(
            "❌ Cancel",
            key="cancel_escalation_btn",
        )

    if confirm_clicked:

        st.session_state.pending_escalation = False

        response_text = ""

        with st.chat_message("assistant"):

            with st.status(
                "🔧 Creating escalation...",
                expanded=True,
            ):

                response_placeholder = st.empty()

                for chunk in graph.stream(
                    Command(resume=True),
                    config=config,
                    stream_mode=["updates", "messages"],
                    version="v2",
                ):

                    if chunk["type"] == "messages":

                        token, metadata = chunk["data"]

                        if (
                            metadata.get("langgraph_node") == "chatbot"
                            and token.content
                        ):
                            response_text += token.content
                            response_placeholder.markdown(
                                response_text
                            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
        })

        st.rerun()

    if cancel_clicked:

        st.session_state.pending_escalation = False

        # Start a fresh conversation rather than leaving
        # the interrupted escalation checkpoint suspended.
        st.session_state.thread_id = str(uuid.uuid4())

        st.session_state.messages.append({
            "role": "assistant",
            "content": "Okay, I won't create the escalation.",
        })

        st.rerun()


# Config

st.set_page_config(
    page_title="ParcelPilot",
    page_icon="📦",
    layout="wide",
)

# Widen the chat column beyond Streamlit's narrow default, but keep
# it centered rather than stretching edge-to-edge.
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Authentication
def login(email: str, password: str):
    return authenticate_user(email, password)

# # Login Page

# if "user_context" not in st.session_state:

#     st.title("📦 ParcelPilot")
#     st.subheader("Customer Support")

#     email = st.text_input("Email")
#     password = st.text_input(
#         "Password",
#         type="password",
#     )

#     if st.button("Login"):

#         if not email or not password:
#             st.warning("Please enter your email and password.")
#             st.stop()

#         user_context = login(email, password)

#         if user_context is None:
#             st.error("Invalid credentials.")
#         else:
#             # Store authenticated session information
#             st.session_state.user_context = user_context
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.session_state.messages = []

#             st.rerun()

#     st.stop()

# --------------------------------------------------
# Login Page
# --------------------------------------------------

if "user_context" not in st.session_state:

    st.title("📦 ParcelPilot")
    st.subheader("Customer Support")

    # Quick demo login
    st.markdown("### 🚀 Quick Demo Login")

    demo_users = {
        "Northstar Logistics — Sara": "ops@northstar.com",
        "LumenWorks — Jay": "ops@lumenworks.com",
        "Beacon Retail — Maya": "ops@beaconretail.com",
        "Axis Labs — Emmy": "ops@axislabs.com",
    }

    selected_demo = st.selectbox(
        "Choose a demo account",
        list(demo_users.keys())
    )

    if st.button("Login as Demo User"):
        email = demo_users[selected_demo]

        # Use your existing authentication mechanism.
        # If your demo accounts have fixed credentials,
        # put the password in Streamlit secrets rather than here.
        password = st.secrets["DEMO_PASSWORDS"][email]

        user_context = authenticate_user(email, password)

        if user_context is None:
            st.error("Demo account authentication failed.")
        else:
            st.session_state.user_context = user_context
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # Normal login
    st.markdown("### 🔐 Login")

    email = st.text_input("Email")
    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button("Login"):

        if not email or not password:
            st.warning("Please enter your email and password.")
            st.stop()

        user_context = authenticate_user(email, password)

        if user_context is None:
            st.error("Invalid credentials.")
        else:
            st.session_state.user_context = user_context
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

    st.stop()


# Logged-in state

user_context = st.session_state.user_context

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_escalation" not in st.session_state:
    st.session_state.pending_escalation = False

# Sidebar: account info + chat/session controls

with st.sidebar:

    st.subheader("📦 ParcelPilot")

    st.write(f"**Account:** {user_context.account_name}")
    st.write(f"**User:** {user_context.name}")

    st.divider()

    if st.button("🆕 New Chat", use_container_width=True):

        # Fresh thread — also clears any pending escalation, since
        # the old interrupted checkpoint belongs to the old thread.
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.pending_escalation = False

        st.rerun()

    if st.button("🔁 Switch Account", use_container_width=True):

        # Clear the authenticated session so the login screen shows
        # again, without needing a full page reload/server restart.
        for key in (
            "user_context",
            "thread_id",
            "messages",
            "pending_escalation",
        ):
            st.session_state.pop(key, None)

        st.rerun()

# Header

st.title("📦 ParcelPilot")

# Chat History & Interface

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.pending_escalation:

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id,
        }
    }

    render_escalation_confirmation(config)

    st.stop()

# Chat Input

if prompt := st.chat_input("Ask ParcelPilot..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.write(prompt)

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id,
        }
    }

    interrupted = False

    with st.chat_message("assistant"):

        status = st.status(
            "🤖 ParcelPilot is working...",
            expanded=True,
        )

        response_placeholder = st.empty()

        tools_used = []
        response_text = ""

        for chunk in graph.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "user_context": st.session_state.user_context,
            },
            config=config,
            stream_mode=["updates", "messages"],
            version="v2",
        ):

            # ------------------------------------------
            # LLM tokens
            # ------------------------------------------

            if chunk["type"] == "messages":

                token, metadata = chunk["data"]

                # Only display tokens generated by the chatbot node.
                # Tool outputs are intentionally hidden.
                if (
                    metadata.get("langgraph_node") == "chatbot"
                    and token.content
                ):
                    response_text += token.content
                    response_placeholder.markdown(response_text)

            # ------------------------------------------
            # Graph / tool updates
            # ------------------------------------------

            elif chunk["type"] == "updates":

                data = chunk["data"]

                for node_name, update in data.items():

                    if node_name == "chatbot":

                        for message in update.get("messages", []):

                            if hasattr(message, "tool_calls"):

                                for tool_call in message.tool_calls:

                                    tool_name = tool_call["name"]

                                    if tool_name not in tools_used:
                                        tools_used.append(tool_name)

                                        status.write(
                                            f"🔧 Calling `{tool_name}`..."
                                        )

                    elif node_name == "tools":

                        for message in update.get("messages", []):

                            tool_name = getattr(
                                message,
                                "name",
                                None,
                            )

                            if tool_name:
                                status.write(
                                    f"✓ `{tool_name}` completed"
                                )

        # Check whether LangGraph paused for escalation confirmation
        snapshot = graph.get_state(config)

        if snapshot.interrupts:

            interrupted = True

            st.session_state.pending_escalation = True

            status.update(
                label="⏸️ Waiting for confirmation",
                state="complete",
                expanded=False,
            )

        else:

            status.update(
                label="✅ Response generated",
                state="complete",
                expanded=False,
            )

    if interrupted:

        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "This issue requires escalation to the support team. "
                "Please confirm below."
            ),
        })

        # Render the confirm/cancel controls right here, in this same
        # script run, instead of setting a flag and calling
        # st.rerun(). Since nothing forces the page to redraw from
        # scratch, the browser stays exactly where it already is —
        # right after the streamed response — so the buttons just
        # appear in place instead of the page jumping back to the
        # top.
        render_escalation_confirmation(config)

        st.stop()

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
    })