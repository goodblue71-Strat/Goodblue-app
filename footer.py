import streamlit as st

def render_footer():
    """Render the GoodBlue-style footer at the bottom of the page."""

    st.markdown("""
    <style>
      .gb-wrap {max-width: 1120px; margin: 0 auto; padding: 0 16px;}
      .gb-hr {border:none; border-top:1px solid #e5e7eb; margin:0;}
      
      .gb-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #6b7280;
        font-size: 14px;
        padding: 16px 0;
        flex-wrap: wrap;
      }

      .gb-footer-left {
        font-weight: 400;
      }

      .gb-footer-right {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
      }

      .gb-footer a {
        color: #4b5563;
        text-decoration: none;
      }

      .gb-footer a:hover {
        color: #111827;
      }

      @media (max-width: 640px) {
        .gb-footer {
          flex-direction: column;
          text-align: center;
          gap: 8px;
        }
        .gb-footer-right {
          justify-content: center;
        }
      }
    </style>

    <div class="gb-wrap">
      <hr class="gb-hr"/>
      <div class="gb-footer">
        <div class="gb-footer-left">
          © 2025 GoodBlue.ai
        </div>
        <div class="gb-footer-right">
          <a href="https://goodblue.ai/contact" target="_blank" rel="noopener noreferrer">Contact</a>
          <a href="https://www.linkedin.com/in/kirthivani/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
          <a href="https://goodblue.ai/Privacy" target="_blank" rel="noopener noreferrer">Privacy</a>
          <a href="https://goodblue.ai/Terms" target="_blank" rel="noopener noreferrer">Terms</a>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
