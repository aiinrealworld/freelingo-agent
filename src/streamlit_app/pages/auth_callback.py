import streamlit as st

# Modern query param API
token = st.query_params.get("token")

if token:
    st.session_state["token"] = token

    # Clear query string from URL
    st.query_params.clear()

    # Show login confirmation
    st.success("✅ Login successful!")

    # Show link as a reliable fallback
    st.markdown("[👉 Click here to continue to the app](/)", unsafe_allow_html=True)

    # Attempt full redirect via JS (may fail in iframe, works when deployed)
    st.markdown("""
        <script>
            setTimeout(() => {
                window.top.location.href = "/";
            }, 100);  // delay ensures Streamlit finishes rendering
        </script>
    """, unsafe_allow_html=True)

    st.stop()
else:
    st.warning("❌ No token found in URL.")