# /pages/test_page.py
import streamlit as st

def main():
    """Main function for the test page - required by Workbook.py"""
    # Create tabs for workbook-style navigation
    tabs = st.tabs(["📄 1. Hello Tab"])
    
    with tabs[0]:
        st.header("👋 Hello!")
        st.write("Hello! This is a simple test page.")
        
        # Add some basic interactive elements
        if st.button("Say Hello Again!", key="hello_btn"):
            st.balloons()
            st.success("Hello there! 🎉")

if __name__ == "__main__":
    main()
