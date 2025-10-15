import streamlit as st

def render_navbar(sticky: bool = True):
    """Render the GoodBlue-style navbar at the top of the Streamlit app (no CTA)."""

    st.markdown("""
    <style>
      .gb-wrap {max-width: 1120px; margin: 0 auto; padding: 0 16px;}
      .gb-nav {display:flex; justify-content:space-between; align-items:center;
               gap:16px; padding:16px 0;}
      .gb-links {display:flex; gap:20px; flex-wrap:wrap; align-items:center;}

      /* Match Tailwind 'font-sans' system stack */
      body, .gb-brand, .gb-link {
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans",
                     sans-serif, "Apple Color Emoji", "Segoe UI Emoji",
                     "Segoe UI Symbol", "Noto Color Emoji";
      }

      /* Brand styling — remove underline in all states */
      .gb-brand,
      .gb-brand:link,
      .gb-brand:visited,
      .gb-brand:hover,
      .gb-brand:active {
        font-weight:700;
        font-size:20px;
        color:#0f172a;
        text-decoration:none !important;
      }

      /* Updated: remove underline from all link states */
      .gb-link,
      .gb-link:link,
      .gb-link:visited,
      .gb-link:hover,
      .gb-link:active {
        color:#374151;
        text-decoration:none !important;
        font-size:14px;
      }

      .gb-link:hover {color:#111827;}
      .gb-hr {border:none; border-top:1px solid #e5e7eb; margin:0;}
      .gb-sticky {position: sticky; top: 0; background: #fff; z-index: 20;}
      @media (max-width: 480px) {.gb-links {gap:12px;}}
    </style>
    """, unsafe_allow_html=True)

    sticky_cls = " gb-sticky" if sticky else ""

    st.markdown(f"""
    <div class="gb-wrap{sticky_cls}">
      <div class="gb-nav">
        <a href="https://goodblue.ai/" target="_blank" rel="noopener noreferrer" class="gb-brand">
          GoodBlue
        </a>
        <nav class="gb-links">
          <a href="https://goodblue.ai/" target="_blank" rel="noopener noreferrer" class="gb-link">
            Home
          </a>
          <a href="https://goodblue.ai/#frameworks" target="_blank" rel="noopener noreferrer" class="gb-link">
            Frameworks
          </a>
          <a href="https://goodblue.ai/Pricing" target="_blank" rel="noopener noreferrer" class="gb-link">
            Pricing
          </a>
        </nav>
      </div>
      <hr class="gb-hr"/>
    </div>
    """, unsafe_allow_html=True)
