import streamlit as st

pages = {
    "Pages": [
        st.Page("./views/AboutPage.py", title="About", icon="⚠️", default=True),
        st.Page("./views/Page1.py", title="Population by prefecture and gender", icon="📊"),
        st.Page("./views/page2.py", title="Prefecture Boundary Viewer", icon="🗺️"),
       # st.Page("./views/page1.py", title="Togolese prefecture page", icon="🚰"),
       # st.Page("./views/page2.py", title="Resident Population by sexe", icon="⚖️"),
       
         #st.Page("./views/page4.py", title="sexe 2", icon="🆕"),
       
       # st.Page("./views/admin-page.py", title="Admin Page", icon="📝"),
         #st.Page("./views/KeyStat.py", title="Statistics", icon="📊")
    ],
}

pg = st.navigation(
    pages,
    expanded=True,
)

pg.run()
