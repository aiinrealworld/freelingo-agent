import streamlit as st

st.set_page_config(page_title="Language Tutor", page_icon="📚")

st.title("📚 Language Tutor AI")
st.markdown("Welcome to your personal AI-powered language tutor!")

# Show login status
if "token" in st.session_state:
    st.success("✅ Logged in")
    st.write(f"User ID token (truncated): {st.session_state['token'][:20]}...")
else:
    login_url = "http://localhost:8080/login.html"
    st.markdown(f"[🔐 Click here to log in with Google]({login_url})")

# Show app links (conditionally if you want)
st.page_link("pages/known_words.py", label="📝 Manage Known Words")

if "token" in st.session_state and st.button("Logout"):
    del st.session_state["token"]
    st.experimental_rerun()