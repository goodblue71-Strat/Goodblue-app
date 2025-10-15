import streamlit as st

def render_footer():
    """Render the GoodBlue-style footer at the bottom of the page."""
    st.markdown("""
    <style>
      .gb-wrap {max-width: 1120px; margin: 0 auto; padding: 0 16px;}
      .gb-hr {border:none; border-top:1px solid #e5e7eb; margin:0;}
      .gb-footer {text-align:center; color:#6b7280; font-size:14px; padding:12px 0;}
      .gb-footer a {color:#4b5563; text-decoration:none;}
      .gb-footer a:hover {color:#111827;}
    </style>

    <div class="gb-wrap">
      <hr class="gb-hr"/>
      <div class="gb-footer">
        © 2025 GoodBlue.ai
        <a href="https://goodblue.ai/contact" target="_blank" rel="noopener noreferrer">Contact</a>
        <a href="https://www.linkedin.com/in/kirthivani/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        <a href="https://goodblue.ai/Privacy" target="_blank" rel="noopener noreferrer">Privacy</a> ·
        <a href="https://goodblue.ai/Terms" target="_blank" rel="noopener noreferrer">Terms</a> ·
       
      </div>
    </div>
    """, unsafe_allow_html=True)
