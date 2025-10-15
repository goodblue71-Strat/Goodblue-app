# main.py — GoodBlue Strategy App (responsive layout)
import streamlit as st
import importlib
from navbar import render_navbar
from footer import render_footer

st.set_page_config(page_title="GoodBlue Strategy App", page_icon="images/favicon.ico", layout="centered")

# ---- RESPONSIVE LAYOUT CSS ----
st.markdown("""
<style>
  /* Remove default Streamlit padding */
  .block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  /* Main app wrapper - flexbox layout */
  .stApp {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  
  /* Content area grows to fill available space */
  .main .block-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  /* Responsive padding adjustments */
  @media (max-width: 768px) {
    .block-container {
      padding-left: 0.5rem;
      padding-right: 0.5rem;
    }
    
    .main .block-container {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }
  }
  
  /* Ensure content is scrollable if needed */
  .main {
    overflow-y: auto;
  }
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
    
    st.write("")  # Add some spacing

    # Responsive column layout: 4 on desktop, 2 on tablet, 1 on mobile
    cols = st.columns([1, 1, 1, 1])
    for i, fw in enumerate(FRAMEWORKS):
        with cols[i % 4]:
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
