import streamlit as st  # type: ignore
from datetime import datetime
from tools.fetch_stock_info import Anazlyze_stock, chat_follow_up

st.set_page_config(
    page_title="GenAI Investment Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        }

        div[data-testid="stMainBlockContainer"],
        .main .block-container {
            padding-top: 1.5rem !important;
        }

        div[data-testid="stMainBlockContainer"] {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }

        div[data-testid="stMainBlockContainer"] {
            padding-top: 2.75rem !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        header[data-testid="stHeader"] {
            background-color: #0f172a !important;
            box-shadow: none;
            z-index: 1000; /* Keep it on top of other elements */
        }

        button[data-testid="stAppDeployButton"] {
            display: none !important;
        }

        section[data-testid="stMain"] * {
            transform: none !important;
        }

        @media (min-width: 768px) {
            div[data-testid="stVerticalBlock"] > div:has(.app-header) {
                position: sticky;
                top: 3.5rem;        
                z-index: 999;
                background-color: #0f172a; 
                padding-top: 0.2rem;   
                padding-bottom: 0.5rem; 
            }
        }

        .app-header {
            padding: 0.8rem 1rem;       
            border-radius: 12px;        
            background: linear-gradient(135deg, #1e3a8a 0%, #0891b2 100%);
            box-shadow: 0 8px 24px rgba(8, 145, 178, 0.25);
            margin-bottom: 0.5rem;
            box-sizing: border-box;
            width: 100%;
        }
        .app-header h1 {
            color: #ffffff;
            font-size: 1.3rem;          
            margin: 0;
            line-height: 1.2;
            word-break: break-word;
        }
        .app-header p {
            color: #dbeafe;
            margin: 0.25rem 0 0 0;
            font-size: 0.8rem;
            word-break: break-word;
        }

        @media (max-width: 480px) {
            .app-header {
                padding: 0.6rem 0.75rem;
                border-radius: 10px;
            }
            .app-header h1 {
                font-size: 1.05rem;
            }
            .app-header p {
                font-size: 0.72rem;
            }
        }

        @media (min-width: 768px) {
            .app-header {
                padding: 1.25rem 1.5rem; 
                border-radius: 16px;
                margin-bottom: 0.75rem; 
            }
            .app-header h1 {
                font-size: 1.8rem;       
            }
            .app-header p {
                font-size: 0.95rem;      
            }
        }

        /* Chat bubbles */
        [data-testid="stChatMessage"] {
            border-radius: 14px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
            border: 1px solid rgba(255,255,255,0.06);
            max-width: 100%;
            overflow-wrap: break-word;
            word-break: break-word;
        }

        @media (max-width: 480px) {
            [data-testid="stChatMessage"] {
                padding: 0.6rem 0.75rem;
                font-size: 0.9rem;
                border-radius: 12px;
            }
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
            white-space: normal;
            word-break: break-word;
            line-height: 1.3;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            border-color: #0891b2;
            background: rgba(8, 145, 178, 0.12);
            color: #ffffff;
        }

        @media (max-width: 480px) {
            section[data-testid="stSidebar"][aria-expanded="true"] {
                min-width: 82vw !important;
                max-width: 88vw !important;
            }
            section[data-testid="stSidebar"] .stButton button {
                padding: 0.5rem 0.65rem;
                font-size: 0.85rem;
            }
        }

        @media (max-width: 480px) {
            div[data-testid="stSidebarResizeHandle"] {
                display: none !important;
            }
        }

        /* Chat input box */
        .stChatInputContainer {
            border-radius: 14px;
        }

        @media (max-width: 480px) {
            .stChatInputContainer {
                border-radius: 12px;
            }
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

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
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

# Header
st.markdown(
    """
    <div class="app-header">
        <h1>📈 GenAI Investment Advisor</h1>
        <p>Ask about any stock (e.g., "Should I invest in TCS?") and follow up with more questions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Empty state
if not st.session_state.messages:
    st.info("👋 Start by typing a stock question below, or pick an example from the sidebar.")

# Render chat history
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "📊"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Handle input (typed or example button)
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