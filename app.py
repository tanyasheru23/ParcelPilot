import streamlit as st
import uuid

from src.auth import authenticate_user
from src.agent import graph

# Config

st.set_page_config(
    page_title="ParcelPilot",
    page_icon="📦",
)

# Authentication
def login(email: str, password: str):
    return authenticate_user(email, password)

# Login Page

if "user_context" not in st.session_state:

    st.title("📦 ParcelPilot")
    st.subheader("Customer Support")

    email = st.text_input("Email")
    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button("Login"):

        if not email or not password:
            st.warning("Please enter your email and password.")
            st.stop()

        user_context = login(email, password)

        if user_context is None:
            st.error("Invalid credentials.")
        else:
            # Store authenticated session information
            st.session_state.user_context = user_context
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []

            st.rerun()

    st.stop()


# Logged-in state

user_context = st.session_state.user_context

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header

st.title("📦 ParcelPilot")

st.success("Logged in successfully!")

st.write(f"**Account:** {user_context.account_name}")
st.write(f"**User:** {user_context.name}")

# Chat History & Interface

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat Input

if prompt := st.chat_input("Ask ParcelPilot..."):

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.write(prompt)

    # Show agent activity while graph is running
    with st.chat_message("assistant"):

        with st.status("🤖 ParcelPilot is working...", expanded=True) as status:

            # Invoke LangGraph agent
            result = graph.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "user_context": st.session_state.user_context,
                },
                config={
                    "configurable": {
                        "thread_id": st.session_state.thread_id,
                    }
                },
            )

            # Find tools used during this turn
            tools_used = []

            for message in result["messages"]:

                if hasattr(message, "tool_calls") and message.tool_calls:

                    for tool_call in message.tool_calls:

                        tool_name = tool_call["name"]

                        if tool_name not in tools_used:
                            tools_used.append(tool_name)

            # Display tools used
            if tools_used:

                st.write("🔧 **Tools used:**")

                for tool_name in tools_used:
                    st.write(f"✓ `{tool_name}`")

            status.update(
                label="✅ Response generated",
                state="complete",
                expanded=False,
            )

        # Final response
        response = result["messages"][-1].content

        st.write(response)

    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })