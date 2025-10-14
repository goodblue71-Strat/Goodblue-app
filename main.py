# main.py — GoodBlue Framework Launcher (Option 2: in-app page switcher)
import streamlit as st
import importlib

st.set_page_config(page_title="GoodBlue Strategy App", page_icon="🧠", layout="centered")

# ---------------------------
# Page routing helpers
# ---------------------------
def goto(page_key: str):
    st.session_state["_page"] = page_key
    # keep URL in sync for deep links (e.g., /?page=SWOT)
    st.experimental_set_query_params(page=page_key)

def init_page_state():
    if "_page" not in st.session_state:
        qp = st.experimental_get_query_params()
        st.session_state["_page"] = qp.get("page", ["Home"])[0]

init_page_state()

# ---------------------------
# Simple top navbar
# ---------------------------
cols = st.columns([1, 1, 6])
with cols[0]:
    if st.button("🏠 Home", use_container_width=True):
        goto("Home")
with cols[1]:
    if st.button("🧩 SWOT", use_container_width=True):
        goto("SWOT")

st.divider()

# ---------------------------
# ROUTER
# ---------------------------
current = st.session_state["_page"]

if current == "Home":
    # ---------------------------
    # STEP 1: Choose Framework (your original grid)
    # ---------------------------
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
                # Navigate to the selected page via router
                if fw["key"] == "swot":
                    goto("SWOT")
                else:
                    st.session_state["pending_fw"] = fw["label"]
                    goto("ComingSoon")

elif current == "SWOT":
    # ---------------------------
    # Load and run SWOT page module
    # ---------------------------
    try:
        swot = importlib.import_module("swot")   # swot.py in the same folder
        if hasattr(swot, "run"):
            swot.run()  # if you want to pass shared state later: swot.run(st.session_state.get("app_state", {}))
        else:
            st.error("`swot.run()` not found. Please define a run() function in swot.py.")
    except ModuleNotFoundError as e:
        st.error(f"Could not import 'swot': {e}")
    except Exception as e:
        st.exception(e)

elif current == "ComingSoon":
    # ---------------------------
    # Placeholder for other frameworks
    # ---------------------------
    label = st.session_state.get("pending_fw", "This framework")
    st.title(label)
    st.warning("This framework module is not yet implemented. Coming soon!")
    if st.button("Back to Home"):
        goto("Home")
