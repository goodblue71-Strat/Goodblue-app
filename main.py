# main.py — GoodBlue Strategy App (responsive layout)
import streamlit as st
import importlib
from navbar import render_navbar
from footer import render_footer

st.set_page_config(page_title="GoodBlue Strategy App", page_icon="images/favicon.ico", layout="centered")

# ---- RESPONSIVE LAYOUT CSS ----
st.markdown("""
<style>
  /* Reset Streamlit's default padding */
  .block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1200px !important;
  }
  
  /* Main app wrapper - flexbox layout */
  .stApp {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  
  /* Content area grows to fill available space */
  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  /* Better spacing for title and caption */
  h1 {
    margin-bottom: 0.5rem !important;
    margin-top: 1rem !important;
  }
  
  .stCaption {
    margin-bottom: 2rem !important;
  }
  
  /* Button spacing improvements */
  .stButton {
    margin-bottom: 0.5rem !important;
  }
  
  .stButton > button {
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    height: auto !important;
    min-height: 3rem !important;
  }
  
  /* Column spacing */
  [data-testid="column"] {
    padding: 0 0.5rem !important;
  }
  
  /* Responsive padding adjustments for mobile */
  @media (max-width: 768px) {
    .block-container {
      padding-top: 1rem !important;
      padding-bottom: 2rem !important;
      padding-left: 1rem !important;
      padding-right: 1rem !important;
    }
    
    [data-testid="column"] {
      padding: 0 0.25rem !important;
      margin-bottom: 1rem;
    }
    
    .stButton > button {
      min-height: 2.5rem !important;
      font-size: 0.9rem !important;
    }
  }
  
  /* Hide Streamlit branding elements for cleaner look */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---- NAVBAR (sticky at top) ----
render_navbar(sticky=True)

# ---------------------------
# PAGE ROUTING HELPERS
# ---------------------------
def goto(page_key: str):
    st.session_state["_page"] = page_key
    st.query_params["page"] = page_key

def init_page_state():
    if "_page" not in st.session_state:
        qp = st.query_params
        st.session_state["_page"] = qp.get("page", "Home")

init_page_state()
current = st.session_state["_page"]

# ---------------------------
# ROUTER
# ---------------------------
if current == "Home":
    FRAMEWORKS = [
        {"key": "swot",    "label": "SWOT Analysis", "desc": "Identify strengths, weaknesses, opportunities, and threats.", "emoji": "🧩"},
        {"key": "ansoff",  "label": "Ansoff + TAM",  "desc": "Plan market and product growth, estimate market size.", "emoji": "📈"},
        {"key": "5forces", "label": "Porter's 5 Forces", "desc": "Understand competition and industry forces.", "emoji": "🏟️"},
        {"key": "bcg",     "label": "BCG Matrix", "desc": "Balance growth and cash flow across product lines.", "emoji": "🟦"},
        {"key": "7s",      "label": "McKinsey 7-S", "desc": "Align structure, strategy, systems, and culture.", "emoji": "🧭"},
        {"key": "vchain",  "label": "Value Chain", "desc": "Map where value and cost are created in operations.", "emoji": "🔗"},
        {"key": "pestel",  "label": "PESTEL", "desc": "Scan macro trends — Political, Economic, Social, Tech, Environmental, Legal.", "emoji": "🌐"},
        {"key": "blueo",   "label": "Blue Ocean", "desc": "Find new, uncontested markets and value spaces.", "emoji": "🌊"},
    ]

    st.title("Choose your strategy framework")
    st.caption("Select a framework to begin your analysis.")
    
    # Create two rows of 4 columns each for proper alignment
    # First row (frameworks 0-3)
    cols_row1 = st.columns(4)
    for i in range(4):
        with cols_row1[i]:
            fw = FRAMEWORKS[i]
            if st.button(f"{fw['emoji']} {fw['label']}", use_container_width=True, key=f"fw_{fw['key']}"):
                st.session_state["framework"] = fw["key"]
                if fw["key"] == "swot":
                    goto("SWOT")
                else:
                    st.session_state["pending_fw"] = fw["label"]
                    goto("ComingSoon")
            st.caption(fw['desc'])
    
    # Second row (frameworks 4-7)
    cols_row2 = st.columns(4)
    for i in range(4, 8):
        with cols_row2[i - 4]:
            fw = FRAMEWORKS[i]
            if st.button(f"{fw['emoji']} {fw['label']}", use_container_width=True, key=f"fw_{fw['key']}"):
                st.session_state["framework"] = fw["key"]
                if fw["key"] == "swot":
                    goto("SWOT")
                else:
                    st.session_state["pending_fw"] = fw["label"]
                    goto("ComingSoon")
            st.caption(fw['desc'])

elif current == "SWOT":
    try:
        swot = importlib.import_module("swot")
        if hasattr(swot, "run"):
            swot.run()
        else:
            st.error("`swot.run()` not found. Please define a run() function in swot.py.")
    except ModuleNotFoundError as e:
        st.error(f"Could not import 'swot': {e}")
    except Exception as e:
        st.exception(e)

elif current == "ComingSoon":
    label = st.session_state.get("pending_fw", "This framework")
    st.title(label)
    st.warning("This framework module is not yet implemented. Coming soon!")
    if st.button("Back to Home"):
        goto("Home")

# ---- FOOTER (at bottom) ----
render_footer()
