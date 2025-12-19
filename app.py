import streamlit as st

pages = {
    "Pages": [
        st.Page("./views/AboutPage.py", title="About", icon="⚠️", default=True),
        st.Page("./views/page1.py", title="Population by prefecture and gender", icon="📊"),
        st.Page("./views/page2.py", title="Prefecture Boundary Viewer", icon="🗺️"),
        st.Page("./views/Page3.py", title="Prefecture Boundary xxx", icon="🗺️"),
    ],
}

pg = st.navigation(
    pages,
    expanded=True,
)

pg.run()
