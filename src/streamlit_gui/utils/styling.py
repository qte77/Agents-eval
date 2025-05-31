import src.streamlit as st


def add_custom_styling(page_title):
    st.set_page_config(
        page_title=f"{page_title}",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    custom_css = """
    <style>    
    /* Hide the default radio button circles */
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
