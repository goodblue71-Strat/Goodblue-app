# main.py — GoodBlue Strategy App (Navbar fixed top, Footer fixed bottom)
import streamlit as st
import importlib
from navbar import render_navbar
from footer import render_footer

# --- PAGE CONFIG ---
st.set_page_config(page_title="GoodBlue Strategy App", page_icon="images/favicon.ico", layout="centered")

# --- LAYOUT CSS: pin navbar and footer, reserve space for content ---
st.markdown("""
<style>
/* Make the inner Streamlit page container full-height */
[data-testid="stAppViewContainer"] > .main {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Remove Streamlit's default padding so header touches the very top */
.block-container {
  padding-top: 84px;   /* reserve space for fixed navbar */
  padding-bottom: 72px;/* reserve space for fixed footer */
}

/* ----- FIX NAVBAR TO TOP ----- */
/* Your navbar markup is: .gb-wrap > .gb-nav ... */
.gb-nav {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 1120px;   /* match your gb-wrap width */
  background: #ffffff;
  z-index: 1000;
  padding: 16px 16px;  /* ensure padding remains when detached from gb-wrap */
  box-sizing: border-box;
}

/* ----- FIX FOOTER TO BOTTOM ----- */
.gb-footer {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 1120px;   /* match your gb-wrap width */
  background: #ffffff;
  z-index: 1000;
  padding: 16px 16px;  /* same vertical rhythm as header */
  box-sizing: border-box;
}

/* Optional: subtle separators (comment out if not desired) */
/*
.gb-nav { border-bottom: 1px solid #e5e7eb; }
.gb-footer { border-top: 1px solid #e5e7eb; }
*/
</style>
""", unsafe_allow_html=True)

# --- NAVBAR (now fixed to top via CSS) ---
render_navbar(sticky=False)  # sticky flag not needed; CSS above fixes it

# --- CONTENT (fills space between fixed navbar & footer) ---
# No special wrapper needed; the .block-container padding handles it

# ---------------------------
# PAGE ROUTING HELPERS
# ---------------------------
def goto(page_key: str):
    """Switch between pages using Streamlit session state."""
    st.session_state["_page"] = page_key
    st.query_params["page"] = page_key

def init_page_state():
    if "_page" not in st.session_state:
        qp = st.query_params
        st.session_state["_page"] = qp.get("page", "Home")

init_page_state()
current = st.session_state["_page"]
