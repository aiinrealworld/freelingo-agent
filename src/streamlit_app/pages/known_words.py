import streamlit as st
from api.known_words import list_known_words

st.title("\ud83d\udcda Your Known Words")

user_email = st.session_state.get("user_email")
if not user_email:
    st.warning("Please log in.")
    st.stop()

words = list_known_words(user_email)
edited_words = st.multiselect("Edit your known words:", words, default=words)

if st.button("Save"):
    st.success("Saved!")