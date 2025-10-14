# main.py — GoodBlue Framework Launcher
import streamlit as st
import importlib

st.set_page_config(page_title="GoodBlue Strategy App", page_icon="🧠", layout="centered")

# ---------------------------
# STEP 1: Choose Framework
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
        if st.button(f"{fw['emoji']} {fw['label']}", use_container_width=True):
            st.session_state.framework = fw["key"]

# ---------------------------
# STEP 2: Load Framework App
# ---------------------------
if "framework" in st.session_state:
    chosen = st.session_state.framework
    st.divider()
    st.success(f"Framework selected: **{next(f['label'] for f in FRAMEWORKS if f['key']==chosen)}**")

    if chosen == "swot":
        st.info("Launching SWOT Analysis...")
        swot = importlib.import_module("swot")
        swot.run()
    else:
        st.warning("This framework module is not yet implemented. Coming soon!")
