import src.streamlit as st


def render_sidebar(sidebar_title: str):
    st.sidebar.title(sidebar_title)
    pages = ["Home", "Settings", "Prompts", "App"]
    selected_page = st.sidebar.radio(" ", pages)

    # st.sidebar.divider()
    # st.sidebar.info(" ")
    return selected_page
