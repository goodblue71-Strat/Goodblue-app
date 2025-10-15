# main.py — GoodBlue Strategy App (Modular layout with Navbar + Footer)
import streamlit as st
import importlib
from navbar import render_navbar
from footer import render_footer

# --- PAGE CONFIG ---
st.set_page_config(page_title="GoodBlue Strategy App", page_icon="images/favicon.ico", layout="centered")

# --- NAVBAR (no CTA) ---
render_navbar(sticky=True)

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

# ---------------------------
# ROUTER
# ---------------------------
if current == "Home":
    # --- Framework Selection Grid ---
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
    # --- SWOT Page ---
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
    # --- Placeholder for other frameworks ---
    label = st.session_state.get("pending_fw", "This framework")
    st.title(label)
    st.warning("This framework module is not yet implemented. Coming soon!")
    if st.button("Back to Home"):
        goto("Home")

# --- FOOTER ---
render_footer()
