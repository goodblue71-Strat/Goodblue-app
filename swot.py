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
    if not items:
        return ""
    result = []
    for item in items:
        if isinstance(item, dict):
            result.append(item.get('text', ''))
        else:
            result.append(str(item))
    return "\n".join(result)

def _text_to_list(txt):
    lines = [x.strip(" \t-•") for x in (txt or "").splitlines() if x.strip()]
    return [{"text": line, "impact": 5, "control": 5} for line in lines]

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
        state["notes"] = st.text_area("Additional Prompts (optional)", value=state["notes"], height=100, placeholder="Consider these prompts while deriving SWOT")

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
        
        # Strengths and Weaknesses row
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strengths")
            if sw.get("S"):
                for idx, item in enumerate(sw["S"], 1):
                    if isinstance(item, dict):
                        st.markdown(f"**S{idx}.** {item['text']}")
                    else:
                        st.markdown(f"**S{idx}.** {item}")
            else:
                st.info("No strengths identified.")
        
        with col2:
            st.markdown("### ⚠️ Weaknesses")
            if sw.get("W"):
                for idx, item in enumerate(sw["W"], 1):
                    if isinstance(item, dict):
                        st.markdown(f"**W{idx}.** {item['text']}")
                    else:
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
                    if isinstance(item, dict):
                        st.markdown(f"**O{idx}.** {item['text']}")
                    else:
                        st.markdown(f"**O{idx}.** {item}")
            else:
                st.info("No opportunities identified.")
        
        with col4:
            st.markdown("### 🚨 Threats")
            if sw.get("T"):
                for idx, item in enumerate(sw["T"], 1):
                    if isinstance(item, dict):
                        st.markdown(f"**T{idx}.** {item['text']}")
                    else:
                        st.markdown(f"**T{idx}.** {item}")
            else:
                st.info("No threats identified.")
        
        st.divider()
        
        # AI-Generated Key Takeaway
        st.markdown("#### 💡 Key Takeaway")
        if sw.get("key_takeaway"):
            st.info(sw["key_takeaway"])
        
        st.divider()
        
        # Priority Matrix
        st.markdown("### 📊 Priority Matrix")
        if sw.get("matrix_introduction"):
            st.markdown(f"*{sw['matrix_introduction']}*")
        
        # Create priority matrix visualization
        import plotly.graph_objects as go
        import numpy as np
        
        fig = go.Figure()
        
        # Normalize and de-cluster function
        def normalize_and_decluster(items_dict):
            """Normalize scores to spread across matrix and add jitter to prevent overlap"""
            all_items = []
            for category, items in items_dict.items():
                if items:
                    for idx, item in enumerate(items):
                        if isinstance(item, dict):
                            all_items.append({
                                'category': category,
                                'idx': idx,
                                'text': item.get('text', ''),
                                'impact': item.get('impact', 5),
                                'control': item.get('control', 5)
                            })
            
            if not all_items:
                return all_items, 0, 10, 0, 10
            
            # Extract scores
            impacts = [item['impact'] for item in all_items]
            controls = [item['control'] for item in all_items]
            
            # Get min/max for normalization
            min_impact, max_impact = min(impacts), max(impacts)
            min_control, max_control = min(controls), max(controls)
            
            # Normalize to spread across 1-10 range
            if len(set(impacts)) > 1:  # Only normalize if there's variance
                for item in all_items:
                    item['impact_norm'] = 1 + 9 * (item['impact'] - min_impact) / (max_impact - min_impact)
            else:
                for item in all_items:
                    item['impact_norm'] = item['impact']
            
            if len(set(controls)) > 1:
                for item in all_items:
                    item['control_norm'] = 1 + 9 * (item['control'] - min_control) / (max_control - min_control)
            else:
                for item in all_items:
                    item['control_norm'] = item['control']
            
            # Add small jitter to prevent exact overlaps
            np.random.seed(42)  # For consistency
            for item in all_items:
                item['impact_final'] = item['impact_norm'] + np.random.uniform(-0.3, 0.3)
                item['control_final'] = item['control_norm'] + np.random.uniform(-0.3, 0.3)
                # Clamp to valid range
                item['impact_final'] = max(0.5, min(10.5, item['impact_final']))
                item['control_final'] = max(0.5, min(10.5, item['control_final']))
            
            return all_items, min_impact, max_impact, min_control, max_control
        
        # Prepare data
        items_dict = {
            'S': sw.get("S", []),
            'W': sw.get("W", []),
            'O': sw.get("O", []),
            'T': sw.get("T", [])
        }
        
        all_items, min_impact, max_impact, min_control, max_control = normalize_and_decluster(items_dict)
        
        # Define colors and symbols
        category_styles = {
            'S': {'color': 'green', 'symbol': 'circle', 'name': 'Strengths'},
            'W': {'color': 'orange', 'symbol': 'square', 'name': 'Weaknesses'},
            'O': {'color': 'blue', 'symbol': 'diamond', 'name': 'Opportunities'},
            'T': {'color': 'red', 'symbol': 'triangle-up', 'name': 'Threats'}
        }
        
        # Plot items by category
        for category in ['S', 'W', 'O', 'T']:
            cat_items = [item for item in all_items if item['category'] == category]
            if cat_items:
                style = category_styles[category]
                for item in cat_items:
                    label = f"{category}{item['idx']+1}"
                    fig.add_trace(go.Scatter(
                        x=[item['impact_final']],
                        y=[item['control_final']],
                        mode='markers+text',
                        marker=dict(size=15, color=style['color'], symbol=style['symbol'], 
                                  line=dict(width=2, color='white')),
                        text=[label],
                        textposition="top center",
                        textfont=dict(size=10, color='black'),
                        name=f"{label}: {item['text'][:40]}...",
                        hovertemplate=f"<b>{label}</b><br>{item['text']}<br>" +
                                    f"Impact: {item['impact']}/10<br>Control: {item['control']}/10<extra></extra>",
                        showlegend=True,
                        legendgroup=category,
                        legendgrouptitle_text=style['name']
                    ))
        
        # Add priority zones with improved styling
        fig.add_shape(type="rect", x0=5.5, y0=5.5, x1=11, y1=11,
                     fillcolor="rgba(144, 238, 144, 0.15)", opacity=1, line=dict(width=2, color="green", dash="dash"))
        fig.add_annotation(x=8.25, y=10, text="HIGH PRIORITY<br>(High Impact + High Control)", 
                          showarrow=False, font=dict(size=11, color="darkgreen", family="Arial Black"))
        
        fig.add_shape(type="rect", x0=5.5, y0=0, x1=11, y1=5.5,
                     fillcolor="rgba(255, 255, 153, 0.15)", opacity=1, line=dict(width=2, color="orange", dash="dash"))
        fig.add_annotation(x=8.25, y=2.75, text="MEDIUM PRIORITY<br>(High Impact + Low Control)",
                          showarrow=False, font=dict(size=11, color="darkorange", family="Arial Black"))
        
        fig.add_shape(type="rect", x0=0, y0=5.5, x1=5.5, y1=11,
                     fillcolor="rgba(255, 182, 193, 0.15)", opacity=1, line=dict(width=2, color="red", dash="dash"))
        fig.add_annotation(x=2.75, y=10, text="LOW PRIORITY<br>(Low Impact + High Control)",
                          showarrow=False, font=dict(size=11, color="darkred", family="Arial Black"))
        
        fig.add_shape(type="rect", x0=0, y0=0, x1=5.5, y1=5.5,
                     fillcolor="rgba(255, 182, 193, 0.15)", opacity=1, line=dict(width=2, color="red", dash="dash"))
        fig.add_annotation(x=2.75, y=2.75, text="LOW PRIORITY<br>(Low Impact + Low Control)",
                          showarrow=False, font=dict(size=11, color="darkred", family="Arial Black"))
        
        # Add centered X and Y axes
        fig.add_shape(type="line", x0=0, y0=5.5, x1=11, y1=5.5,
                     line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=5.5, y0=0, x1=5.5, y1=11,
                     line=dict(color="black", width=2))
        
        # Create custom tick labels that map to original scores
        def create_tick_labels(min_val, max_val):
            """Create tick labels that show original score values"""
            tick_positions = list(range(0, 11))
            tick_labels = []
            for pos in tick_positions:
                if min_val != max_val:
                    # Map normalized position back to original score
                    original = min_val + (max_val - min_val) * (pos - 1) / 9
                    tick_labels.append(f"{original:.1f}")
                else:
                    tick_labels.append(f"{min_val:.1f}")
            return tick_positions, tick_labels
        
        x_tick_positions, x_tick_labels = create_tick_labels(min_impact, max_impact)
        y_tick_positions, y_tick_labels = create_tick_labels(min_control, max_control)
        
        # Update layout
        fig.update_layout(
            title="Impact on Success vs Ability to Influence",
            xaxis_title="Impact on Success →",
            yaxis_title="Ability to Influence →",
            xaxis=dict(
                range=[0, 11], 
                tickmode='array',
                tickvals=x_tick_positions,
                ticktext=x_tick_labels,
                showgrid=False,
                zeroline=False,
                showticklabels=True
            ),
            yaxis=dict(
                range=[0, 11], 
                tickmode='array',
                tickvals=y_tick_positions,
                ticktext=y_tick_labels,
                showgrid=False,
                zeroline=False,
                showticklabels=True
            ),
            height=650,
            showlegend=True,
            hovermode='closest',
            plot_bgcolor='white',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Matrix Key Takeaway
        if sw.get("matrix_takeaway"):
            st.info(sw["matrix_takeaway"])
        
        st.divider()
        
        # Priority Table
        st.markdown("### 📋 Strategic Priorities")
        
        # Priority Table Introduction
        if sw.get("priority_table_introduction"):
            st.markdown(f"*{sw['priority_table_introduction']}*")
            st.markdown("")
        
        # Calculate the center threshold for impact
        all_impacts = []
        for category in ['S', 'W', 'O', 'T']:
            items = sw.get(category, [])
            for item in items:
                if isinstance(item, dict):
                    all_impacts.append(item.get('impact', 0))
        
        # Center of impact range (midpoint between min and max)
        if all_impacts:
            min_impact_threshold = min(all_impacts)
            max_impact_threshold = max(all_impacts)
            center_impact = (min_impact_threshold + max_impact_threshold) / 2
        else:
            center_impact = 5  # default
        
        # Collect high and medium priority items with impact >= center
        priority_items = []
        for category in ['S', 'W', 'O', 'T']:
            items = sw.get(category, [])
            for idx, item in enumerate(items, 1):
                if isinstance(item, dict):
                    priority = item.get('priority', 'low')
                    impact = item.get('impact', 0)
                    # Only include if impact is at or above center threshold
                    if priority in ['high', 'medium'] and impact >= center_impact:
                        priority_items.append({
                            'ref': f"{category}{idx}",
                            'category': category,
                            'text': item.get('text', ''),
                            'priority': priority,
                            'solution': item.get('solution', 'No solution provided'),
                            'impact': impact,
                            'control': item.get('control', 0),
                            'score': impact + item.get('control', 0)
                        })
        
        # Sort by combined score (impact + control), highest first
        priority_items.sort(key=lambda x: (-x['score'], -x['impact']))
        
        if priority_items:
            # Create table data
            table_data = []
            for item in priority_items:
                table_data.append({
                    'Strategic Factor': item['text'],
                    'Priority': item['score'],
                    'Solution': item['solution']
                })
            
            # Display as dataframe with custom column widths
            import pandas as pd
            df = pd.DataFrame(table_data)
            
            st.dataframe(
                df,
                column_config={
                    "Strategic Factor": st.column_config.TextColumn(
                        "Strategic Factor",
                        width="medium",
                    ),
                    "Priority": st.column_config.NumberColumn(
                        "Priority",
                        width="small",
                        format="%d"
                    ),
                    "Solution": st.column_config.TextColumn(
                        "Solution",
                        width="large",
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No high or medium priority items identified with sufficient impact")
        
        # Priority Table Takeaway
        if sw.get("priority_table_takeaway"):
            st.markdown("")
            st.info(sw["priority_table_takeaway"])
        
        st.divider()
        
        # Strategic Roadmap - Built from Priority Table
        st.markdown("### 🗓️ Strategic Roadmap")
        
        # Roadmap Introduction
        if sw.get("roadmap_introduction"):
            st.markdown(f"*{sw['roadmap_introduction']}*")
            st.markdown("")
        
        # Build roadmap from priority_items (already sorted by score)
        if priority_items:
            # Distribute items across time horizons based on control score
            short_term_items = []
            near_term_items = []
            long_term_items = []
            
            for item in priority_items:
                control = item['control']
                # High control (>7) → short term, Medium control (5-7) → near term, Lower control → long term
                if control > 7:
                    short_term_items.append(item)
                elif control >= 5:
                    near_term_items.append(item)
                else:
                    long_term_items.append(item)
            
            # Create three columns for timeline
            col_short, col_near, col_long = st.columns(3)
            
            with col_short:
                st.markdown("#### 📅 Short Term")
                st.markdown("*Next Quarter*")
                st.markdown("")
                if short_term_items:
                    for idx, item in enumerate(short_term_items, 1):
                        st.markdown(f"{idx}. {item['solution']}")
                        st.markdown("")
                else:
                    st.info("No short-term actions")
            
            with col_near:
                st.markdown("#### 📅 Near Term")
                st.markdown("*This Year*")
                st.markdown("")
                if near_term_items:
                    for idx, item in enumerate(near_term_items, 1):
                        st.markdown(f"{idx}. {item['solution']}")
                        st.markdown("")
                else:
                    st.info("No near-term actions")
            
            with col_long:
                st.markdown("#### 📅 Long Term")
                st.markdown("*Greater than 1 Year*")
                st.markdown("")
                if long_term_items:
                    for idx, item in enumerate(long_term_items, 1):
                        st.markdown(f"{idx}. {item['solution']}")
                        st.markdown("")
                else:
                    st.info("No long-term actions")
        else:
            st.info("No priority items to display in roadmap")
        
        # Roadmap Takeaway
        if sw.get("roadmap_takeaway"):
            st.markdown("")
            st.info(sw["roadmap_takeaway"])
        
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
