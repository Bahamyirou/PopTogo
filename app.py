import streamlit as st

pages = {
    "Pages": [
        st.Page("./views/page1.py", title="Togolese prefecture page 1", icon="🚰", default=True),
        st.Page("./views/page2.py", title="Togolese prefecture page 2", icon="⚖️"),
        st.Page("./views/page3.py", title="Prefecture Boundary Viewer 1", icon="🗺️"),
        st.Page("./views/page4.py", title="Prefecture Boundary Viewer 2", icon="🆕"),
        #st.Page("./views/large-jumps.py", title="Large Jumps", icon="⚠️"),
       # st.Page("./views/admin-page.py", title="Admin Page", icon="📝"),
         #st.Page("./views/KeyStat.py", title="Statistics", icon="📊")
    ],
}

pg = st.navigation(
    pages,
    expanded=True,
)

pg.run()
