import streamlit as st  # type: ignore
from datetime import datetime
from tools.fetch_stock_info import Anazlyze_stock, chat_follow_up

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="GenAI Investment Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Custom CSS
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Overall app background */
        .stApp {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        }

        /* Reduce Streamlit's default top padding so the sticky header
           sits closer to the very top of the page */
        div[data-testid="stMainBlockContainer"],
        .main .block-container {
            padding-top: 1.5rem !important;
        }

        /* Hide the hamburger menu and footer only — keep header intact
           so the sidebar open/close arrow keeps working */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Make the header bar solid dark so text scrolling under it is hidden */
        header[data-testid="stHeader"] {
            background-color: #0f172a !important;
            box-shadow: none;
            z-index: 1000; /* Keep it on top of other elements */
        }

        /* Hide just the "Deploy" button, keep everything else (incl. sidebar arrow) */
        button[data-testid="stAppDeployButton"] {
            display: none !important;
        }

        /* Streamlit wraps elements in containers that use a CSS transform
           for fade-in animation. ANY transform on ANY ancestor breaks
           position:sticky, so we strip transforms from the main scroll area. */
        section[data-testid="stMain"] * {
            transform: none !important;
        }

        /* 1. Make the outer wrapper container sticky, give it a background,
              and enforce a gap after the header using padding-bottom */
        div[data-testid="stVerticalBlock"] > div:has(.app-header) {
            position: sticky;
            top: 2.875rem;        /* Positioned exactly below the solid stHeader bar */
            z-index: 999;
            background-color: #0f172a; /* Matches app background to hide scrolling text */
            padding-top: 0.2rem;   /* Spacing at the top of the header */
            padding-bottom: 2rem;  /* Creates the 2rem gap after the header */
        }

        /* 2. Style the header itself */
        .app-header {
            padding: 1.25rem 1.5rem;
            border-radius: 16px;
            background: linear-gradient(135deg, #1e3a8a 0%, #0891b2 100%);
            box-shadow: 0 8px 24px rgba(8, 145, 178, 0.25);
        }
        .app-header h1 {
            color: #ffffff;
            font-size: 1.8rem;
            margin: 0;
        }
        .app-header p {
            color: #dbeafe;
            margin: 0.35rem 0 0 0;
            font-size: 0.95rem;
        }

        /* Chat bubbles */
        [data-testid="stChatMessage"] {
            border-radius: 14px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
            border: 1px solid rgba(255,255,255,0.06);
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.03);
            color: #e5e7eb;
            text-align: left;
            padding: 0.6rem 0.8rem;
            margin-bottom: 0.5rem;
            transition: all 0.15s ease;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            border-color: #0891b2;
            background: rgba(8, 145, 178, 0.12);
            color: #ffffff;
        }

        /* Chat input box */
        .stChatInputContainer {
            border-radius: 14px;
        }

        /* Badge */
        .status-badge {
            display: inline-block;
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            background: rgba(34,197,94,0.15);
            color: #4ade80;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(34,197,94,0.3);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📊 Stock Assistant")
    st.markdown('<span class="status-badge">● Live</span>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**Try an example**")
    examples = [
        "Should I invest in TCS?",
        "What's the outlook for Reliance Industries?",
        "Compare Infosys and Wipro fundamentals",
        "Is HDFC Bank a good long-term buy?",
    ]
    example_clicked = None
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            example_clicked = ex

    st.markdown("---")
    questions_asked = len(st.session_state.messages) // 2
    st.markdown(f"**Questions asked this session:** {questions_asked}")
    st.caption(datetime.now().strftime("%A, %d %B %Y"))

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption(
        "⚠️ This assistant provides informational analysis only, "
        "not financial advice. Always do your own research."
    )

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <h1>📈 GenAI Investment Advisor</h1>
        <p>Ask about any stock (e.g., "Should I invest in TCS?") and follow up with more questions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Empty state
# ----------------------------------------------------------------------
if not st.session_state.messages:
    st.info("👋 Start by typing a stock question below, or pick an example from the sidebar.")

# ----------------------------------------------------------------------
# Render chat history
# ----------------------------------------------------------------------
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "📊"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ----------------------------------------------------------------------
# Handle input (typed or example button)
# ----------------------------------------------------------------------
prompt = st.chat_input("Enter your query here...")
if example_clicked and not prompt:
    prompt = example_clicked

if prompt:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="📊"):
        with st.spinner("Analyzing data..."):
            if len(st.session_state.messages) == 1:
                response = Anazlyze_stock(prompt)
            else:
                response = chat_follow_up(st.session_state.messages)

            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
