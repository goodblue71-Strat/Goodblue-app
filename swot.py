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
except Exception:
    StrategyGenerator = None
    OpenAIProvider = None

def _mock_generator():
    class _MockGen:
        def generate_swot(self, **kwargs):
            return {
                "S": ["Clear value proposition", "Growing customer base"],
                "W": ["Limited brand awareness"],
                "O": ["Upsell existing accounts"],
                "T": ["Price pressure from rivals"],
            }
    return _MockGen()

def _get_generator():
    offline = st.session_state.state.get("offline_mode", False)
    if StrategyGenerator is None or offline:
        return _mock_generator()
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and OpenAIProvider is not None:
            provider = OpenAIProvider(model="gpt-4o-mini", api_key=api_key)
            return StrategyGenerator(provider)
    except Exception:
        pass
    return _mock_generator()

# ---------- Helpers ----------
def _list_to_text(items): return "\n".join(items or [])
def _text_to_list(txt): return [x.strip(" \t-•") for x in (txt or "").splitlines() if x.strip()]

# ---------- Page Entrypoint ----------
def run():
    st.set_page_config(page_title=APP_NAME, page_icon="🧩", layout="wide")
    st.title(APP_NAME)

    if "step" not in st.session_state:
        st.session_state.step = 0
    if "state" not in st.session_state:
        st.session_state.state = {
            "analysis_id": str(uuid.uuid4()),
            "company": "",
            "product": "",
            "scope": "",
            "geo": "",
            "notes": "",
            "offline_mode": False,
            "results": {"SWOT": {"S": [], "W": [], "O": [], "T": []}},
        }

    state = st.session_state.state

    def on_generate():
        if not state["company"].strip() or not state["product"].strip():
            st.error("Company and Product are required.")
            return
        gen = _get_generator()
        try:
            with st.spinner("Generating SWOT…"):
                swot = gen.generate_swot(
                    company=state["company"],
                    scope=state["scope"],
                    product=state["product"],
                    notes=state["notes"],
                    geo=state["geo"],
                )
                state["results"]["SWOT"] = swot
            st.toast("SWOT generated.", icon="✅")
            st.session_state.step = 1
        except Exception as e:
            st.error(f"Generation failed: {e}")

    st.progress((st.session_state.step + 1) / 3, text=f"Step {st.session_state.step + 1} of 3")

    # ---------- Step 0: Inputs ----------
    if st.session_state.step == 0:
        st.subheader("Inputs")
        state["company"] = st.text_input("Company *", state["company"], placeholder="e.g., Emerson")
        state["product"] = st.text_input("Product *", state["product"], placeholder="e.g., Edge IoT Sensors")
        state["scope"] = st.text_input("Scope (optional)", state["scope"], placeholder="e.g., Manufacturing")
        state["geo"] = st.selectbox("Geography (optional)", ["", "US", "EU", "APAC"])
        state["notes"] = st.text_area("Notes (optional)", value=state["notes"], height=100)
        state["offline_mode"] = st.checkbox("Run offline (mock mode)", value=state.get("offline_mode", False))

        if st.button("Generate SWOT", type="primary", use_container_width=True):
            on_generate()

    # ---------- Step 1: Edit SWOT ----------
    elif st.session_state.step == 1:
        st.subheader("SWOT Results")
        sw = state["results"]["SWOT"]
        cS, cW, cO, cT = st.columns(4)
        with cS: new_S = st.text_area("Strengths", _list_to_text(sw.get("S")), height=180)
        with cW: new_W = st.text_area("Weaknesses", _list_to_text(sw.get("W")), height=180)
        with cO: new_O = st.text_are
