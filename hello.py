import streamlit as st

def main():
    # Setup
    st.set_page_config(page_title="Hello", layout="centered")

    # Navigation
    tabs = st.tabs(["📄 1. Hello Tab"])

    # Tab Text
    with tabs[0]:
        st.write("### ✨ Banner ✨")
        st.header("👋 Hello!", divider="rainbow")
        st.write("Hello! This is a simple test page.")

        # Button Action
        if st.button("Say Hello Again!", key="hello_btn"):
            st.balloons()
            st.success("Hello there! 🎉")
            st.toast("Nice to see you again!")

if __name__ == "__main__":
    main()
