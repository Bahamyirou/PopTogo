import streamlit as st

pages = {
    "Pages": [
        st.Page("./views/AboutPage.py", title="About", icon="⚠️", default=True),
<<<<<<< HEAD
        ## st.Page("./views/page2.py", title="Prefecture Boundary Viewer", icon="🗺️"),
        st.Page("./views/page4.py", title="Population Distribution", icon="🗺️"),
=======
        st.Page("./views/page1.py", title="Population by prefecture and gender", icon="📊"),
        st.Page("./views/page2.py", title="Prefecture Boundary Viewer", icon="🗺️")
>>>>>>> 45baab05b73844ad4071b8ab5b464bacf9a1cfe6
    ],
}

pg = st.navigation(
    pages,
    expanded=True,
)

pg.run()
