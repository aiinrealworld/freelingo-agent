import streamlit as st
import urllib.parse

st.set_page_config(page_title="Login")

st.title("🔐 Login")

# 1. Check if token is in URL
query_params = st.query_params
token = query_params.get("token")

# 2. Store it
if token:
    st.session_state["token"] = token

# 3. Show login link or session
if "token" not in st.session_state:
    login_url = "http://localhost:8080/login.html"
    st.markdown(f"[Click here to log in with Google]({login_url})")
else:
    st.success("✅ Logged in")
    st.write(f"User ID token (truncated): {st.session_state['token'][:20]}...")

    if st.button("Check /me"):
        import requests
        res = requests.get(
            "http://localhost:8000/auth/me",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.error(f"Auth failed: {res.status_code} - {res.text}")