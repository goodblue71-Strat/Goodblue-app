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
    from generator import StrategyGenerator, OpenAIProvider
    from swot_prompts import generate_swot
    GENERATOR_AVAILABLE = True
except Exception as e:
    st.error(f"Failed to import generator modules: {type(e).__name__}: {e}")
    import traceback
    st.code(traceback.format_exc())
    StrategyGenerator = None
    OpenAIProvider = None
    generate_swot = None
    GENERATOR_AVAILABLE = False

def _get_generator():
    """Returns generator if available, None otherwise"""
    if not GENERATOR_AVAILABLE:
        st.error("Generator modules not available. Check if generator.py and swot_prompts.py exist.")
        return None
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Check if it's in secrets but not in env
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        
        if not api_key:
            st.error("API key not found in environment or secrets.")
            return None
            
        if OpenAIProvider is None:
            st.error("OpenAIProvider class is None - import failed.")
            return None
            
        provider = OpenAIProvider(model="gpt-4o-mini", api_key=api_key)
        gen = StrategyGenerator(provider)
        
        if gen.is_available():
            return gen
        else:
            st.error("Generator created but provider not available.")
            return None
            
    except Exception as e:
        st.error(f"Error creating generator: {type(e).__name__}: {e}")
        import traceback
        st.code(traceback.format_exc())
    
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
                swot = generate_swot(
                    gen,
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

    # ---------- Step 1: Display SWOT Analysis ----------
    elif st.session_state.step == 1:
        st.subheader("SWOT Analysis Results")
        
        # AI-Generated Introduction
        sw = state["results"]["SWOT"]
        if sw.get("introduction"):
            st.markdown(f"*{sw['introduction']}*")
        
        st.divider()
        
        # Company info header
        st.markdown(f"**Company:** {state['company']}")
        st.markdown(f"**Product:** {state['product']}")
        if state.get('industry'):
            st.markdown(f"**Industry:** {state['industry']}")
        if state['scope']:
            st.markdown(f"**Product Feature:** {state['scope']}")
        if state['geo']:
            st.markdown(f"**Geography:** {state['geo']}")
        
        st.divider()
        
        # Strengths and Weaknesses row
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strengths")
            if sw.get("S"):
                for idx, item in enumerate(sw["S"], 1):
                    st.markdown(f"**S{idx}.** {item}")
            else:
                st.info("No strengths identified.")
        
        with col2:
            st.markdown("### ⚠️ Weaknesses")
            if sw.get("W"):
                for idx, item in enumerate(sw["W"], 1):
                    st.markdown(f"**W{idx}.** {item}")
            else:
                st.info("No weaknesses identified.")
        
        st.divider()
        
        # Opportunities and Threats row
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### 🎯 Opportunities")
            if sw.get("O"):
                for idx, item in enumerate(sw["O"], 1):
                    st.markdown(f"**O{idx}.** {item}")
            else:
                st.info("No opportunities identified.")
        
        with col4:
            st.markdown("### 🚨 Threats")
            if sw.get("T"):
                for idx, item in enumerate(sw["T"], 1):
                    st.markdown(f"**T{idx}.** {item}")
            else:
                st.info("No threats identified.")
        
        st.divider()
        
        # AI-Generated Key Takeaway
        st.markdown("#### 💡 Key Takeaway")
        if sw.get("key_takeaway"):
            st.info(sw["key_takeaway"])
        
        st.divider()
        
        # Action buttons
        col_back, col_edit, col_export = st.columns(3)
        with col_back:
            if st.button("← Back to Inputs", use_container_width=True):
                st.session_state.step = 0
                st.rerun()
        with col_edit:
            if st.button("✏️ Edit Results", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        with col_export:
            if st.button("💾 Export", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

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
            for idx, item in enumerate(sw.get("S", []), 1):
                st.markdown(f"**S{idx}.** {item}")
        with cW:
            st.markdown("**Weaknesses**")
            for idx, item in enumerate(sw.get("W", []), 1):
                st.markdown(f"**W{idx}.** {item}")
        with cO:
            st.markdown("**Opportunities**")
            for idx, item in enumerate(sw.get("O", []), 1):
                st.markdown(f"**O{idx}.** {item}")
        with cT:
            st.markdown("**Threats**")
            for idx, item in enumerate(sw.get("T", []), 1):
                st.markdown(f"**T{idx}.** {item}")

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
