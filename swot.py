# swot.py — GoodBlue SWOT Analysis (launched from main.py)
from __future__ import annotations
import os, json, uuid
from datetime import datetime
import streamlit as st

APP_NAME = "GoodBlue SWOT Analysis"

# ---------- Generator Wiring ----------
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

try:
    from generate import StrategyGenerator, OpenAIProvider
    GENERATOR_AVAILABLE = True
except Exception:
    StrategyGenerator = None
    OpenAIProvider = None
    GENERATOR_AVAILABLE = False

def _get_generator():
    """Returns generator if available, None otherwise"""
    if not GENERATOR_AVAILABLE:
        return None
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and OpenAIProvider is not None:
            provider = OpenAIProvider(model="gpt-4o-mini", api_key=api_key)
            return StrategyGenerator(provider)
    except Exception:
        pass
    
    return None

# ---------- Helpers ----------
def _list_to_text(items): 
    return "\n".join(items or [])

def _text_to_list(txt): 
    return [x.strip(" \t-•") for x in (txt or "").splitlines() if x.strip()]

# ---------- Page Entrypoint ----------
def run():
    st.set_page_config(page_title=APP_NAME, page_icon="images/favicon.ico", layout="wide")
    st.title(APP_NAME)

    if "step" not in st.session_state:
        st.session_state.step = 0
    if "state" not in st.session_state:
        st.session_state.state = {
            "analysis_id": str(uuid.uuid4()),
            "company": "",
            "product": "",
            "industry": "",
            "scope": "",
            "geo": "",
            "notes": "",
            "results": {"SWOT": {"S": [], "W": [], "O": [], "T": []}},
        }

    state = st.session_state.state

    def on_generate():
        if not state["company"].strip() or not state["product"].strip():
            st.error("Company and Product are required.")
            return
        
        gen = _get_generator()
        if gen is None:
            st.error("⚠️ LLM provider connection is not available. Please check your API key configuration.")
            return
        
        try:
            with st.spinner("Generating SWOT…"):
                swot = gen.generate_swot(
                    company=state["company"],
                    industry=state.get("industry", ""),
                    product=state["product"],
                    product_feature=state["scope"],
                    notes=state["notes"],
                    geo=state["geo"],
                )
                state["results"]["SWOT"] = swot
            st.toast("SWOT generated.", icon="✅")
            st.session_state.step = 1
            st.rerun()
        except Exception as e:
            st.error(f"Generation failed: {e}")

    st.progress((st.session_state.step + 1) / 4, text=f"Step {st.session_state.step + 1} of 4")

    # Check if generator is available and show warning if not
    if _get_generator() is None:
        st.warning("⚠️ LLM provider connection is not available. Please configure your OpenAI API key in Streamlit secrets.")

    # ---------- Step 0: Inputs ----------
    if st.session_state.step == 0:
        st.subheader("Inputs")
        state["company"] = st.text_input("Company *", state["company"], placeholder="e.g., Emerson")
        state["product"] = st.text_input("Product *", state["product"], placeholder="e.g., Edge IoT Sensors")
        state["industry"] = st.text_input("Industry", state.get("industry", ""), placeholder="e.g., Manufacturing")
        state["scope"] = st.text_input("Product Feature (optional)", state["scope"], placeholder="e.g., Identifying bearing failure")
        state["geo"] = st.selectbox("Geography (optional)", ["", "US", "EU", "APAC", "Africa", "Middle East"])
        state["notes"] = st.text_area("Notes (optional)", value=state["notes"], height=100)

        # Disable button if generator not available
        generator_available = _get_generator() is not None
        if st.button("Generate SWOT", type="primary", use_container_width=True, disabled=not generator_available):
            on_generate()

    # ---------- Step 1: Edit SWOT ----------
    elif st.session_state.step == 1:
        st.subheader("SWOT Results")
        sw = state["results"]["SWOT"]
        cS, cW, cO, cT = st.columns(4)
        with cS: 
            new_S = st.text_area("Strengths", _list_to_text(sw.get("S")), height=180)
        with cW: 
            new_W = st.text_area("Weaknesses", _list_to_text(sw.get("W")), height=180)
        with cO: 
            new_O = st.text_area("Opportunities", _list_to_text(sw.get("O")), height=180)
        with cT: 
            new_T = st.text_area("Threats", _list_to_text(sw.get("T")), height=180)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.step = 0
        with col2:
            if st.button("Next →", type="primary", use_container_width=True):
                # Save edited SWOT
                sw["S"] = _text_to_list(new_S)
                sw["W"] = _text_to_list(new_W)
                sw["O"] = _text_to_list(new_O)
                sw["T"] = _text_to_list(new_T)
                st.session_state.step = 2

    # ---------- Step 2: Edit SWOT ----------
    elif st.session_state.step == 2:
        st.subheader("Edit SWOT Results")
        sw = state["results"]["SWOT"]
        cS, cW, cO, cT = st.columns(4)
        with cS: 
            new_S = st.text_area("Strengths", _list_to_text(sw.get("S")), height=180)
        with cW: 
            new_W = st.text_area("Weaknesses", _list_to_text(sw.get("W")), height=180)
        with cO: 
            new_O = st.text_area("Opportunities", _list_to_text(sw.get("O")), height=180)
        with cT: 
            new_T = st.text_area("Threats", _list_to_text(sw.get("T")), height=180)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to View", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("Save & Continue →", type="primary", use_container_width=True):
                # Save edited SWOT
                sw["S"] = _text_to_list(new_S)
                sw["W"] = _text_to_list(new_W)
                sw["O"] = _text_to_list(new_O)
                sw["T"] = _text_to_list(new_T)
                st.session_state.step = 3
                st.rerun()

    # ---------- Step 3: Export ----------
    elif st.session_state.step == 3:
        st.subheader("Export")
        sw = state["results"]["SWOT"]
        
        # Display final SWOT
        st.markdown("### Final SWOT Analysis")
        cS, cW, cO, cT = st.columns(4)
        with cS:
            st.markdown("**Strengths**")
            for item in sw.get("S", []):
                st.markdown(f"- {item}")
        with cW:
            st.markdown("**Weaknesses**")
            for item in sw.get("W", []):
                st.markdown(f"- {item}")
        with cO:
            st.markdown("**Opportunities**")
            for item in sw.get("O", []):
                st.markdown(f"- {item}")
        with cT:
            st.markdown("**Threats**")
            for item in sw.get("T", []):
                st.markdown(f"- {item}")

        # Export options
        export_data = {
            "analysis_id": state["analysis_id"],
            "timestamp": datetime.now().isoformat(),
            "company": state["company"],
            "product": state["product"],
            "industry": state.get("industry", ""),
            "product_feature": state["scope"],
            "geography": state["geo"],
            "notes": state["notes"],
            "swot": sw
        }
        
        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            "Download JSON",
            json_str,
            file_name=f"swot_{state['company'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

        if st.button("← Back to Edit", use_container_width=True):
            st.session_state.step = 1
        
        if st.button("Start New Analysis", type="primary", use_container_width=True):
            # Reset state
            st.session_state.step = 0
            st.session_state.state = {
                "analysis_id": str(uuid.uuid4()),
                "company": "",
                "product": "",
                "industry": "",
                "scope": "",
                "geo": "",
                "notes": "",
                "results": {"SWOT": {"S": [], "W": [], "O": [], "T": []}},
            }
            st.rerun()
