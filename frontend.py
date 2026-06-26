import html
import os
from datetime import datetime
from urllib.parse import quote_plus

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
APP_NAME = "MindHarbor"

st.set_page_config(
    page_title="MindHarbor | Mental wellness companion",
    page_icon="MH",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        :root {
            --bg: #050507;
            --surface: rgba(13, 15, 24, .86);
            --surface-strong: #121624;
            --line: rgba(255, 216, 77, .18);
            --mint: #ffd84d;
            --mint-soft: #fff0a8;
            --sky: #2f8cff;
            --lavender: #ff4d5f;
            --text: #f8f7f2;
            --muted: #aeb4c2;
            --yellow: #ffd84d;
            --red: #ff4d5f;
            --blue: #2f8cff;
        }

        * { box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body, [class*="css"] { font-family: "DM Sans", sans-serif; }

        .stApp {
            color: var(--text);
            background:
                radial-gradient(circle at 7% 0%, rgba(255, 216, 77, .22), transparent 24rem),
                radial-gradient(circle at 92% 8%, rgba(47, 140, 255, .21), transparent 25rem),
                radial-gradient(circle at 48% 95%, rgba(255, 77, 95, .14), transparent 28rem),
                linear-gradient(145deg, #030304, #080b13 50%, #050507);
            background-attachment: fixed;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: .18;
            background-image:
                linear-gradient(rgba(255, 216, 77, .055) 1px, transparent 1px),
                linear-gradient(90deg, rgba(47, 140, 255, .055) 1px, transparent 1px);
            background-size: 54px 54px;
            mask-image: linear-gradient(to bottom, black, transparent 82%);
            animation: gridMove 22s linear infinite;
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; }
        .block-container { max-width: 1220px; padding: .75rem 2rem 8rem; }

        [data-testid="stSidebar"] {
            background: rgba(4, 5, 9, .94);
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] .block-container { padding-top: 1.3rem; }
        [data-testid="stSidebar"] hr { border-color: var(--line); }

        .brand {
            display: flex;
            align-items: center;
            gap: .8rem;
            margin: .2rem 0 1.6rem;
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 44px;
            height: 44px;
            border-radius: 15px;
            color: #06221e;
            font-size: 1.35rem;
            background: linear-gradient(135deg, var(--mint-soft), var(--yellow));
            box-shadow: 0 12px 30px rgba(255, 216, 77, .22);
        }

        .brand-name {
            font: 800 1.08rem "Manrope", sans-serif;
            letter-spacing: -.03em;
        }

        .brand-sub { color: var(--muted); font-size: .72rem; }

        .side-card {
            margin: 1rem 0;
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(19, 51, 53, .55);
        }

        .side-card strong { color: var(--mint-soft); }
        .side-card p { margin: .35rem 0 0; color: var(--muted); font-size: .8rem; line-height: 1.5; }

        .dashboard-hero {
            position: relative;
            display: grid;
            grid-template-columns: minmax(0, 1fr) 220px;
            align-items: center;
            min-height: 220px;
            overflow: hidden;
            padding: 1.7rem 2rem;
            border: 1px solid var(--line);
            border-radius: 28px;
            background:
                linear-gradient(120deg, rgba(18, 62, 58, .95), rgba(8, 12, 21, .88) 52%, rgba(38, 22, 43, .76)),
                rgba(11, 35, 39, .8);
            box-shadow: 0 30px 80px rgba(0, 0, 0, .26), inset 0 1px rgba(255,255,255,.07);
            backdrop-filter: blur(22px);
            animation: rise .7s cubic-bezier(.2,.8,.2,1) both;
        }

        .dashboard-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(255,255,255,.09) 1px, transparent 1px),
                linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px);
            background-size: 42px 42px;
            mask-image: linear-gradient(110deg, black, transparent 72%);
            opacity: .28;
            pointer-events: none;
        }

        .dashboard-hero::after {
            content: "";
            position: absolute;
            right: 34px;
            bottom: 28px;
            width: 245px;
            height: 96px;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(255,216,77,.18), rgba(47,140,255,.2), rgba(255,77,95,.16));
            filter: blur(28px);
            pointer-events: none;
        }

        .live-pill {
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            width: fit-content;
            margin-bottom: 1rem;
            padding: .45rem .75rem;
            border: 1px solid rgba(128, 225, 193, .2);
            border-radius: 99px;
            color: var(--mint-soft);
            background: rgba(128, 225, 193, .07);
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .live-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--mint);
            box-shadow: 0 0 15px var(--mint);
            animation: pulse 2s ease-in-out infinite;
        }

        .dashboard-hero h1 {
            max-width: 650px;
            margin: 0;
            color: #f4fffc;
            font: 800 clamp(1.8rem, 3.5vw, 2.8rem)/1.04 "Manrope", sans-serif;
            letter-spacing: -.055em;
        }

        .dashboard-hero h1 span {
            color: transparent;
            background: linear-gradient(100deg, var(--mint), var(--sky), var(--lavender));
            background-size: 180% 180%;
            background-clip: text;
            -webkit-background-clip: text;
            animation: gradient 6s ease infinite;
        }

        .dashboard-hero p {
            max-width: 620px;
            margin: .75rem 0 0;
            color: #afd0ca;
            line-height: 1.65;
        }

        .hero-actions {
            display: flex;
            flex-wrap: wrap;
            gap: .75rem;
            margin-top: 1rem;
        }

        .hero-chip {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            padding: .62rem .85rem;
            border: 1px solid rgba(255,255,255,.14);
            border-radius: 12px;
            color: #f8f7f2;
            background: rgba(255,255,255,.055);
            font-size: .82rem;
            font-weight: 700;
        }

        .hero-chip span { color: var(--mint); }

        .mind-orb-wrap {
            position: relative;
            display: grid;
            place-items: center;
            height: 145px;
            perspective: 800px;
        }

        .mind-orb {
            position: relative;
            width: 104px;
            height: 104px;
            border: 1px solid rgba(220,255,246,.44);
            border-radius: 50%;
            background:
                radial-gradient(circle at 32% 25%, rgba(255,255,255,.9) 0 2%, transparent 9%),
                radial-gradient(circle at 38% 34%, #96f1d7, #438fa0 44%, #7664a6 72%, #17283d);
            box-shadow: 0 0 40px rgba(105, 223, 192, .3), 0 24px 45px rgba(0,0,0,.35);
            transform-style: preserve-3d;
            animation: float 5s ease-in-out infinite;
        }

        .mind-orb::before, .mind-orb::after {
            content: "";
            position: absolute;
            inset: -22px;
            border: 1px solid rgba(128,225,193,.28);
            border-radius: 50%;
            transform: rotateX(68deg) rotateZ(12deg);
            animation: spin 8s linear infinite;
        }

        .mind-orb::after {
            inset: -38px 4px;
            border-color: rgba(184,169,239,.24);
            transform: rotateY(68deg) rotateZ(-18deg);
            animation-direction: reverse;
            animation-duration: 10s;
        }

        .section-title {
            margin: .9rem 0 .25rem;
            color: var(--text);
            font: 700 1.25rem "Manrope", sans-serif;
            letter-spacing: -.025em;
        }

        .section-copy { margin-bottom: 1.1rem; color: var(--muted); font-size: .9rem; }

        .metric-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: .75rem 0;
        }

        .metric-card, .feature-card, .care-card, .tool-card {
            border: 1px solid var(--line);
            background: var(--surface);
            box-shadow: 0 14px 35px rgba(0,0,0,.14), inset 0 1px rgba(255,255,255,.04);
            backdrop-filter: blur(17px);
        }

        .metric-card {
            padding: 1rem 1.15rem;
            border-radius: 18px;
            animation: rise .6s ease both;
        }

        .metric-label { color: var(--muted); font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; }
        .metric-value { margin-top: .25rem; color: var(--mint-soft); font: 700 1.1rem "Manrope", sans-serif; }

        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            position: sticky;
            top: .35rem;
            z-index: 10;
            gap: .45rem;
            margin: .7rem 0 .45rem;
            padding: .35rem;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: rgba(7, 27, 30, .7);
            backdrop-filter: blur(18px);
        }

        [data-testid="stTabs"] button {
            min-height: 42px;
            border-radius: 12px;
            color: var(--muted);
            font-weight: 600;
        }

        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #06211c;
            background: linear-gradient(135deg, var(--mint-soft), #78d7bd);
        }

        [data-testid="stTabs"] [data-baseweb="tab-highlight"],
        [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

        .chat-stage {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 260px;
            gap: 1rem;
            align-items: start;
        }

        .chat-focus, .chat-rail {
            border: 1px solid var(--line);
            background: rgba(9, 18, 25, .66);
            backdrop-filter: blur(18px);
        }

        .chat-focus {
            min-height: 58vh;
            padding: .35rem .55rem 8rem;
            border-radius: 22px;
        }

        .chat-rail {
            position: sticky;
            top: 6rem;
            padding: 1rem;
            border-radius: 18px;
        }

        .rail-kicker {
            color: var(--mint);
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .rail-copy {
            margin: .45rem 0 .9rem;
            color: var(--muted);
            font-size: .82rem;
            line-height: 1.5;
        }

        [data-testid="stChatMessage"] {
            margin: .8rem 0;
            padding: 1.05rem 1.2rem;
            border: 1px solid var(--line);
            border-radius: 20px;
            background: rgba(14, 41, 44, .78);
            box-shadow: 0 12px 30px rgba(0,0,0,.14);
            animation: message .4s cubic-bezier(.2,.8,.2,1) both;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: linear-gradient(135deg, rgba(41, 99, 96, .82), rgba(33, 68, 84, .74));
        }

        [data-testid="stChatMessage"] p { color: #eaf8f5; line-height: 1.65; }

        [data-testid="stChatInput"] {
            border: 1px solid rgba(128,225,193,.28);
            border-radius: 19px;
            background: rgba(9, 31, 34, .94);
            box-shadow: 0 18px 48px rgba(0,0,0,.28);
            backdrop-filter: blur(22px);
        }

        [data-testid="stChatInput"]:focus-within {
            border-color: rgba(128,225,193,.65);
            box-shadow: 0 18px 50px rgba(0,0,0,.32), 0 0 0 4px rgba(128,225,193,.07);
        }

        .stButton > button, .stFormSubmitButton > button, .stLinkButton > a {
            border: 1px solid rgba(135,221,201,.2);
            border-radius: 13px;
            color: var(--mint-soft);
            background: rgba(23, 63, 63, .72);
            transition: transform .2s ease, border-color .2s ease, background .2s ease;
        }

        .stButton > button:hover, .stFormSubmitButton > button:hover, .stLinkButton > a:hover {
            border-color: rgba(128,225,193,.55);
            color: #06201c;
            background: var(--mint);
            transform: translateY(-2px);
        }

        .feature-card, .tool-card {
            min-height: 150px;
            padding: 1.3rem;
            border-radius: 20px;
        }

        .card-icon {
            display: grid;
            place-items: center;
            width: 42px;
            height: 42px;
            margin-bottom: .8rem;
            border-radius: 13px;
            color: #06211c;
            background: linear-gradient(135deg, var(--mint-soft), var(--mint));
            box-shadow: 0 10px 24px rgba(90,210,177,.17);
        }

        .card-title { color: var(--text); font-weight: 700; }
        .card-copy { margin-top: .35rem; color: var(--muted); font-size: .85rem; line-height: 1.55; }

        .care-card {
            margin: .7rem 0;
            padding: 1.15rem 1.25rem;
            border-radius: 18px;
            transition: transform .2s ease, border-color .2s ease;
        }

        .care-card:hover { transform: translateY(-2px); border-color: rgba(128,225,193,.35); }
        .care-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
        .care-name { color: var(--text); font: 700 1rem "Manrope", sans-serif; }
        .distance { color: var(--mint); font-size: .8rem; white-space: nowrap; }
        .care-type { margin: .3rem 0; color: var(--lavender); font-size: .78rem; text-transform: capitalize; }
        .care-detail { color: var(--muted); font-size: .82rem; line-height: 1.55; }
        .care-actions { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: .8rem; }
        .care-actions a {
            padding: .45rem .7rem;
            border: 1px solid var(--line);
            border-radius: 10px;
            color: var(--mint-soft) !important;
            font-size: .76rem;
            text-decoration: none;
            background: rgba(128,225,193,.06);
        }

        .notice {
            padding: 1rem 1.15rem;
            border: 1px solid rgba(243, 190, 101, .2);
            border-radius: 16px;
            color: #d9caaa;
            background: rgba(112, 77, 29, .13);
            font-size: .82rem;
            line-height: 1.55;
        }

        .breathing-shell {
            display: grid;
            place-items: center;
            min-height: 310px;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: radial-gradient(circle, rgba(99,184,168,.16), transparent 55%), var(--surface);
        }

        .breathing-orb {
            display: grid;
            place-items: center;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            color: #08211d;
            font-weight: 700;
            background: radial-gradient(circle at 32% 26%, #f0fff9, var(--mint) 48%, #4c9d95);
            box-shadow: 0 0 45px rgba(128,225,193,.32);
            animation: breathe 10s ease-in-out infinite;
        }

        .login-shell {
            min-height: calc(100vh - 2rem);
            display: grid;
            grid-template-columns: minmax(320px, .68fr) minmax(0, 1fr);
            gap: 2rem;
            align-items: start;
            padding-top: 1rem;
        }

        .login-copy h1 {
            max-width: 720px;
            margin: 0;
            color: var(--text);
            font: 800 clamp(2rem, 4.5vw, 4rem)/1 "Manrope", sans-serif;
        }

        .login-copy h1 span {
            color: transparent;
            background: linear-gradient(100deg, var(--yellow), var(--blue), var(--red));
            background-size: 180% 180%;
            background-clip: text;
            -webkit-background-clip: text;
            animation: gradient 6s ease infinite;
        }

        .login-copy p {
            max-width: 610px;
            margin: 1.1rem 0 0;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.7;
        }

        .neural-animation {
            position: relative;
            width: min(520px, 92vw);
            height: 180px;
            margin-top: 1.2rem;
            overflow: hidden;
            border: 1px solid rgba(255, 216, 77, .2);
            border-radius: 24px;
            background:
                radial-gradient(circle at 20% 45%, rgba(255, 216, 77, .22), transparent 18%),
                radial-gradient(circle at 78% 58%, rgba(47, 140, 255, .22), transparent 20%),
                rgba(12, 15, 24, .72);
        }

        .neural-animation span {
            position: absolute;
            left: -12%;
            width: 124%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--yellow), var(--blue), var(--red), transparent);
            filter: drop-shadow(0 0 12px rgba(255, 216, 77, .45));
            animation: brainWave 4.5s ease-in-out infinite;
        }

        .neural-animation span:nth-child(1) { top: 42px; animation-delay: 0s; }
        .neural-animation span:nth-child(2) { top: 88px; animation-delay: .8s; opacity: .82; }
        .neural-animation span:nth-child(3) { top: 132px; animation-delay: 1.4s; opacity: .68; }

        .login-panel {
            padding: 1.5rem;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(9, 11, 18, .9);
            box-shadow: 0 28px 70px rgba(0,0,0,.35), inset 0 1px rgba(255,255,255,.06);
        }

        .login-panel h2 {
            margin: 0 0 .35rem;
            color: var(--mint-soft);
            font: 800 1.45rem "Manrope", sans-serif;
        }

        .login-panel p {
            margin: 0 0 1rem;
            color: var(--muted);
            font-size: .9rem;
            line-height: 1.55;
        }

        .footer-note {
            margin: 2rem 0 0;
            color: #718f8a;
            font-size: .74rem;
            text-align: center;
        }

        @keyframes rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes message { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 50% { opacity: .45; transform: scale(.8); } }
        @keyframes gradient { 50% { background-position: 100% 50%; } }
        @keyframes float { 50% { transform: translateY(-14px) rotateY(10deg) rotateX(-4deg); } }
        @keyframes spin { to { transform: rotateX(68deg) rotateZ(372deg); } }
        @keyframes gridMove { to { background-position: 54px 54px; } }
        @keyframes breathe {
            0%, 100% { transform: scale(.72); box-shadow: 0 0 30px rgba(128,225,193,.2); }
            45%, 55% { transform: scale(1.22); box-shadow: 0 0 70px rgba(128,225,193,.45); }
        }
        @keyframes brainWave {
            0%, 100% { transform: translateX(-4%) scaleY(1); border-radius: 50%; }
            35% { transform: translateX(4%) scaleY(5); }
            70% { transform: translateX(8%) scaleY(2); }
        }

        @media (max-width: 800px) {
            .block-container { padding: .75rem 1rem 7rem; }
            .dashboard-hero { grid-template-columns: 1fr; padding: 1.4rem; }
            .mind-orb-wrap { height: 150px; transform: scale(.82); }
            .metric-row { grid-template-columns: 1fr; }
            .login-shell { grid-template-columns: 1fr; }
            [data-testid="stTabs"] [data-baseweb="tab-list"] {
                position: static;
                flex-direction: row;
                overflow-x: auto;
                margin-bottom: 1rem;
            }
            .chat-stage { grid-template-columns: 1fr; }
            .chat-rail { position: static; }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {"name": "Friend", "email": ""}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Hi, I'm MindHarbor. You can talk with me about stress, anxiety, "
                    "relationships, sleep, motivation, or simply how today has felt. "
                    "What would feel most helpful to talk through?"
                ),
            }
        ]
    if "mood_log" not in st.session_state:
        st.session_state.mood_log = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def render_login_page() -> None:
    form_col, copy_col = st.columns([0.78, 1.22], gap="large", vertical_alignment="top")

    with form_col:
        st.markdown(
            """
            <div class="login-panel">
                <h2>Welcome back</h2>
                <p>Use any name and email to begin your local wellness session.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            name = st.text_input("Name", placeholder="Your name")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Any password")
            submitted = st.form_submit_button("Log in", use_container_width=True)

    with copy_col:
        st.markdown(
            """
            <div class="login-copy">
                <div class="live-pill"><span class="live-dot"></span> Private local session</div>
                <h1>Start with a calmer <span>mental health check-in.</span></h1>
                <p>Sign in to open your supportive chat, mood log, care finder, and animated calm tools. This demo login stays in your current Streamlit session.</p>
                <div class="neural-animation" aria-hidden="true">
                    <span></span><span></span><span></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if submitted:
        if not name.strip() or not email.strip() or not password.strip():
            st.error("Please enter your name, email, and password to continue.")
            return
        st.session_state.authenticated = True
        st.session_state.user_profile = {
            "name": name.strip(),
            "email": email.strip(),
        }
        st.rerun()


def chat_context() -> list[dict]:
    return [
        {"role": item["role"], "content": item["content"]}
        for item in st.session_state.chat_history[-8:]
        if item["role"] in {"user", "assistant"}
    ]


def stream_chat_response(prompt: str, history: list[dict]):
    try:
        with requests.post(
            f"{API_BASE_URL}/ask-stream",
            json={"message": prompt, "history": history},
            stream=True,
            timeout=(5, 90),
        ) as response:
            response.raise_for_status()
            received = False
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    received = True
                    yield chunk
            if not received:
                yield "I couldn't create a response just now. Please try again."
    except requests.exceptions.ConnectionError:
        yield "I can't reach the support service. Please make sure the backend is running."
    except requests.exceptions.Timeout:
        yield "That took longer than expected. Please try sending your message once more."
    except requests.exceptions.RequestException:
        yield "Something interrupted the response. Please try again in a moment."


def care_card(item: dict) -> str:
    name = html.escape(item.get("name") or "Mental health support")
    speciality = html.escape(item.get("speciality") or "mental health care")
    address = html.escape(item.get("address") or "Address not listed")
    distance = html.escape(str(item.get("distance_km", "?")))
    phone = item.get("phone")
    website = item.get("website")
    lat, lon = item.get("lat"), item.get("lon")
    maps_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}"

    actions = [f'<a href="{maps_url}" target="_blank">View map -></a>']
    if phone:
        safe_phone = html.escape(phone)
        actions.insert(0, f'<a href="tel:{quote_plus(phone)}">Call {safe_phone}</a>')
    if website:
        safe_website = html.escape(website, quote=True)
        actions.append(f'<a href="{safe_website}" target="_blank">Website -></a>')

    return f"""
    <div class="care-card">
        <div class="care-top">
            <div class="care-name">{name}</div>
            <div class="distance">{distance} km away</div>
        </div>
        <div class="care-type">{speciality}</div>
        <div class="care-detail">{address}</div>
        <div class="care-actions">{''.join(actions)}</div>
    </div>
    """


initialize_state()

if not st.session_state.authenticated:
    render_login_page()
    st.stop()

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">MH</div>
            <div>
                <div class="brand-name">MindHarbor</div>
                <div class="brand-sub">A calmer place to think</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("SIGNED IN")
    st.markdown(
        f"""
        <div class="side-card">
            <strong>{html.escape(st.session_state.user_profile["name"])}</strong>
            <p>{html.escape(st.session_state.user_profile["email"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.caption("TODAY")
    current_mood = (
        st.session_state.mood_log[-1]["label"]
        if st.session_state.mood_log
        else "Not checked in"
    )
    st.markdown(
        f"""
        <div class="side-card">
            <strong>{html.escape(current_mood)}</strong>
            <p>Your latest emotional check-in. Small observations can reveal useful patterns.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("+ Start a fresh conversation", use_container_width=True):
        st.session_state.chat_history = [st.session_state.chat_history[0]]
        st.rerun()

    st.divider()
    st.markdown(
        """
        <div class="side-card">
            <strong>Need urgent help?</strong>
            <p>If you may act on thoughts of harming yourself or someone else, call local emergency services now and stay with a trusted person.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "MindHarbor offers supportive information, not diagnosis, medical treatment, "
        "or a replacement for a licensed professional."
    )

st.markdown(
    """
    <section class="dashboard-hero">
        <div>
            <div class="live-pill"><span class="live-dot"></span> Local AI ready</div>
            <h1>Your space to pause, understand, and <span>move forward.</span></h1>
            <p>Talk through what is weighing on you, check in with your mood, find nearby professional care, or take a two-minute reset.</p>
            <div class="hero-actions">
                <div class="hero-chip"><span>01</span> Context-aware chat</div>
                <div class="hero-chip"><span>02</span> Nearby care finder</div>
                <div class="hero-chip"><span>03</span> Calm reset tools</div>
            </div>
        </div>
        <div class="mind-orb-wrap" aria-hidden="true"><div class="mind-orb"></div></div>
    </section>
    """,
    unsafe_allow_html=True,
)

message_count = sum(1 for msg in st.session_state.chat_history if msg["role"] == "user")
mood_count = len(st.session_state.mood_log)
st.markdown(
    f"""
    <div class="metric-row">
        <div class="metric-card"><div class="metric-label">Conversation</div><div class="metric-value">{message_count} reflections shared</div></div>
        <div class="metric-card"><div class="metric-label">Check-ins</div><div class="metric-value">{mood_count} mood moments</div></div>
        <div class="metric-card"><div class="metric-label">Privacy</div><div class="metric-value">Local AI model</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

chat_tab, care_tab, checkin_tab, tools_tab = st.tabs(
    ["Support chat", "Find care", "Daily check-in", "Calm toolkit"]
)

with chat_tab:
    st.markdown('<div class="section-title">A conversation without judgment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Share as much or as little as feels comfortable. Replies appear as they are written.</div>',
        unsafe_allow_html=True,
    )

    chat_col, rail_col = st.columns([3.1, 1])
    quick_prompts = [
        ("I feel overwhelmed", "I'm feeling overwhelmed and I don't know where to start."),
        ("Help me calm down", "Can you guide me through a short calming exercise?"),
        ("I can't sleep", "My mind keeps racing when I try to sleep."),
        ("I need perspective", "I'm stuck in a difficult situation and need help seeing it clearly."),
    ]

    with rail_col:
        st.markdown(
            '<div class="chat-rail"><div class="rail-kicker">Start gently</div>'
            '<div class="rail-copy">Pick a prompt or write freely. The assistant now receives recent context, so replies can build on the conversation.</div></div>',
            unsafe_allow_html=True,
        )
        for label, prompt_text in quick_prompts:
            if st.button(label, use_container_width=True):
                st.session_state.pending_prompt = prompt_text
                st.rerun()

    message_area = chat_col.container()

    typed_prompt = st.chat_input("What's been on your mind?", key="main_chat_input")
    prompt = st.session_state.pending_prompt or typed_prompt

    with message_area:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt:
            previous_context = chat_context()
            st.session_state.pending_prompt = None
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                response_text = st.write_stream(stream_chat_response(prompt, previous_context))
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response_text}
            )
            st.rerun()
with care_tab:
    st.markdown('<div class="section-title">Find professional support nearby</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Search by city, neighborhood, or postal code. Results come from current OpenStreetMap listings.</div>',
        unsafe_allow_html=True,
    )

    with st.form("care_search_form"):
        left, right = st.columns([3, 1])
        with left:
            location = st.text_input(
                "Your area",
                placeholder="e.g. Gurugram, Haryana",
                label_visibility="collapsed",
            )
        with right:
            radius = st.selectbox("Distance", [5, 10, 12, 20, 25], index=2)
        search_care = st.form_submit_button(
            "Find nearby support", use_container_width=True
        )

    st.markdown(
        """
        <div class="notice">
            Listings may be incomplete or outdated. Verify credentials, services, fees, and phone numbers directly before booking. This finder is not an emergency service.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if search_care:
        if not location.strip():
            st.warning("Enter a city, area, or postal code to search.")
        else:
            try:
                with st.spinner("Looking for nearby mental-health support..."):
                    response = requests.get(
                        f"{API_BASE_URL}/nearby-care",
                        params={"location": location.strip(), "radius_km": radius},
                        timeout=(5, 45),
                    )
                    response.raise_for_status()
                    care_data = response.json()
                    st.session_state.care_results = care_data
            except requests.exceptions.HTTPError:
                detail = response.json().get("detail", "No results could be loaded.")
                st.error(detail)
            except requests.exceptions.RequestException:
                st.error("The care finder is unavailable right now. Please try again shortly.")

    if "care_results" in st.session_state:
        care_data = st.session_state.care_results
        results = care_data.get("results", [])
        st.caption(f"Showing care near {care_data.get('location', location)}")
        if results:
            for item in results:
                st.markdown(care_card(item), unsafe_allow_html=True)
        else:
            st.info(
                "No specialist listings were found in this radius. Try a nearby city or "
                "increase the distance. You can also ask a local hospital or primary-care "
                "clinic for a mental-health referral."
            )
        st.caption(f"Location data (c) {care_data.get('source', 'OpenStreetMap contributors')}")

with checkin_tab:
    st.markdown('<div class="section-title">Name what today feels like</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">This is a reflection tool, not a clinical assessment. Notice the pattern without judging it.</div>',
        unsafe_allow_html=True,
    )

    mood_options = {
        "Drained": 1,
        "Low": 2,
        "Unsettled": 3,
        "Okay": 4,
        "Steady": 5,
        "Good": 6,
        "Energized": 7,
    }
    with st.form("mood_form"):
        mood = st.select_slider(
            "How are you feeling right now?",
            options=list(mood_options.keys()),
            value="Okay",
        )
        note = st.text_area(
            "What may be influencing this?",
            placeholder="A sentence is enough: sleep, work, relationships, health, or anything else.",
            height=100,
        )
        save_mood = st.form_submit_button("Save this check-in")

    if save_mood:
        st.session_state.mood_log.append(
            {
                "label": mood,
                "score": mood_options[mood],
                "note": note.strip(),
                "time": datetime.now().strftime("%d %b, %I:%M %p"),
            }
        )
        st.success("Check-in saved. Noticing is already a useful step.")

    if st.session_state.mood_log:
        st.markdown('<div class="section-title">Recent check-ins</div>', unsafe_allow_html=True)
        for entry in reversed(st.session_state.mood_log[-5:]):
            note_text = html.escape(entry["note"] or "No note added")
            st.markdown(
                f"""
                <div class="care-card">
                    <div class="care-top">
                        <div class="care-name">{html.escape(entry["label"])}</div>
                        <div class="distance">{html.escape(entry["time"])}</div>
                    </div>
                    <div class="care-detail">{note_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tools_tab:
    st.markdown('<div class="section-title">Small tools for difficult moments</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Choose one simple action. You do not need to solve everything at once.</div>',
        unsafe_allow_html=True,
    )
    breathing_col, guide_col = st.columns([1.15, 1])
    with breathing_col:
        st.markdown(
            """
            <div class="breathing-shell">
                <div class="breathing-orb">Breathe</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Follow the circle: inhale as it expands, pause gently, exhale as it softens.")
    with guide_col:
        st.markdown(
            """
            <div class="tool-card">
                <div class="card-icon">5</div>
                <div class="card-title">5-4-3-2-1 grounding</div>
                <div class="card-copy">Notice 5 things you see, 4 you feel, 3 you hear, 2 you smell, and 1 you taste.</div>
            </div><br>
            <div class="tool-card">
                <div class="card-icon">v</div>
                <div class="card-title">Release physical tension</div>
                <div class="card-copy">Drop your shoulders, unclench your jaw, press your feet into the floor, and take one slower breath.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Build a gentle next step</div>', unsafe_allow_html=True)
    cards = st.columns(3)
    toolkit = [
        ("*", "Reset your environment", "Drink water, open a window, or move to a quieter place."),
        ("OK", "Make it smaller", "Choose the next action that takes less than five minutes."),
        ("+", "Reach outward", "Message someone safe: \"I'm having a hard day. Can we talk?\""),
    ]
    for column, (icon, title, copy) in zip(cards, toolkit):
        with column:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown(
    '<div class="footer-note">MindHarbor - Supportive AI for reflection and navigation - Not medical care or an emergency service</div>',
    unsafe_allow_html=True,
)
