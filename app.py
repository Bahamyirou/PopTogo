import streamlit as st
##publish add
pages = {
    "Pages": [
        st.Page("./views/AboutPage.py", title="About", icon="⚠️", default=True),
        st.Page("./views/page4.py", title="Population Distribution", icon="🗺️"),
        st.Page("./views/page3.py", title="Population Distribution2", icon="🗺️"),
    ],
}

pg = st.navigation(
    pages,
    expanded=True,
)

pg.run()
