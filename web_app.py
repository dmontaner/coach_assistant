# web1.py
# 2023-11-24 david.montaner@gmail.com
# streamlit web for the coach chat

import streamlit as st
from coach_assistant import MyConversation, interactive_greeting, agent_instructions

print('WEB STARTED', flush=True)

# Remove “Made with Streamlit” from bottom of app
# https://discuss.streamlit.io/t/remove-made-with-streamlit-from-bottom-of-app/1370

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# load conversation engine
if "conv" not in st.session_state:
    st.session_state.conv = MyConversation(
        agent_name="AIda",
        interactive_greeting=interactive_greeting,
        agent_instructions=agent_instructions,
        user_name="Participant",
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        verbose=True,
    )
    print(f'loaded thread: {st.session_state.conv.thread.id}', flush=True)

if "messages" in st.session_state:
    for m in st.session_state.messages:
        print(type(m))
        print(m, flush=True)

# WEB CONTENT STARTS HERE
st.title("AI Coach for SomeBank")
# st.title("AI Coach for SomeBank - 5<sup>Tm</sup> of December 2023")
# st.components.v1.html("AI Coach for SomeBank - 5<sup>th</sup> of December 2023")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi Participant!"},
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("What is up?"):

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)
        st.session_state.conv.user_ask(msg=user_input)

    with st.chat_message("assistant"):
        assistant_response = st.session_state.conv.get_last_message()["content"]
        st.markdown(assistant_response)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    print(f'\nIN THE LOOP WITH THREAD: {st.session_state.conv.thread.id}', flush=True)
