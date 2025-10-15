# main.py — GoodBlue Strategy App (center content between navbar & footer)
import streamlit as st
import importlib
from navbar import render_navbar
from footer import render_footer

st.set_page_config(page_title="GoodBlue Strategy App", page_icon="images/favicon.ico", layout="centered")

# ---- TUNE THESE IF NEEDED (approx visual heights in px) ----
HEADER_PX = 72   # your navbar’s visual height
FOOTER_PX = 64   # your footer’s visual height

# ---- LAYOUT CSS: center content between header & footer ----
st.markdown(f"""
<style>
  /* remove extra Streamlit padding so header sits near the top */
  .block-container {{
    padding-top: 0rem;
    padding-bottom: 0rem;
  }}

  /* a band that fills the viewport minus header+footer */
  #gb-viewport {{
    min-height: calc(100vh - {HEADER_PX + FOOTER_PX}px);
    display: flex;
    align-items: center;        /* vertical center */
    justify-content: center;    /* horizontal center for narrow content */
    padding: 8px 0;             /* small breathing room */
    box-sizing: border-box;
    width: 100%;
  }}

  /* keep Streamlit's centered layout look */
  #gb-viewport > .gb-content-wrap {{
    width: 100%;
    max-width: 1120px;          /* match GoodBlue width */
    padding: 0 16px;
    box-sizing: border-box;
  }}
</style>
""", unsafe_allow_html=True)

# ---- NAVBAR (top, normal flow) ----
render_navbar(sticky=False)

# ---- VIEWPORT band that centers content ----
st.markdown('<div id="gb-viewport"><div class="gb-content-wrap">', unsafe_allow_html=True)

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
# ROUTER (your existing code)
# ---------------------------
if current == "Home":
    FRAMEWORKS = [
        {"key": "swot",    "label": "SWOT Analysis", "desc": "Identify strengths, weaknesses, opportunities, and threats.", "emoji": "🧩"},
        {"key": "ansoff",  "label": "Ansoff + TAM",  "desc": "Plan market and product growth, estimate market size.", "emoji": "📈"},
        {"key": "5forces", "label": "Porter’s 5 Forces", "desc": "Understand competition and industry forces.", "emoji": "🏟️"},
        {"key": "bcg",     "label": "BCG Matrix", "desc": "Balance growth and cash flow across product lines.", "emoji": "🟦"},
        {"key": "7s",      "label": "McKinsey 7-S", "desc": "Align structure, strategy, systems, and culture.", "emoji": "🧭"},
        {"key": "vchain",  "label": "Value Chain", "desc": "Map where value and cost are created in operations.", "emoji": "🔗"},
        {"key": "pestel",  "label": "PESTEL", "desc": "Scan macro trends — Political, Economic, Social, Tech, Environmental, Legal.", "emoji": "🌐"},
        {"key": "blueo",   "label": "Blue Ocean", "desc": "Find new, uncontested markets and value spaces.", "emoji": "🌊"},
    ]

    st.title("Choose your strategy framework")
    st.caption("Select a framework to begin your analysis.")

    cols = st.columns(4)
    for i, fw in enumerate(FRAMEWORKS):
        with cols[i % 4]:
            if st.button(f"{fw['emoji']} {fw['label']}", use_container_width=True, key=f"fw_{fw['key']}"):
                st.session_state["framework"] = fw["key"]
                if fw["key"] == "swot":
                    goto("SWOT")
                else:
                    st.session_state["pending_fw"] = fw["label"]
                    goto("ComingSoon")

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

# ---- close viewport wrappers ----
st.markdown('</div></div>', unsafe_allow_html=True)

# ---- FOOTER (bottom, normal flow) ----
render_footer()
