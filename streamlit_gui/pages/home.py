import streamlit as st


def render_home():
    st.header("Welcome to the Multi-Agent Research System")

    st.markdown("""
    This system allows you to:
    
    - Run research queries using multiple specialized agents
    - Configure agent settings and prompts
    - View detailed results from your research
    
    Use the sidebar to navigate between different sections of the application.
    """)

    st.info("Select 'App' to start using the system")
