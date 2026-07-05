import streamlit as st # type: ignore
from tools.fetch_stock_info import Anazlyze_stock, chat_follow_up

st.title("📈 AI Stock Analysis Assistant")
st.write("Ask about any stock (e.g., 'Should I invest in TCS?'), and then ask follow-up questions!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter your query here..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            if len(st.session_state.messages) == 1:
                response = Anazlyze_stock(prompt)
            else:
                response = chat_follow_up(st.session_state.messages)
            
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
