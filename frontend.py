import streamlit as st
st.set_page_config(page_title="Ai Mental Health Therapist", layout="wide")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        :root {
            --ink: #eaf7f4;
            --muted: #a9c8c2;
            --mint: #74e0c4;
            --aqua: #68bddd;
            --violet: #a995e8;
            --panel: rgba(13, 38, 43, 0.68);
            --line: rgba(155, 226, 211, 0.16);
        }

        * {
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body,
        [class*="css"] {
            font-family: "DM Sans", sans-serif;
        }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at 15% 10%, rgba(69, 164, 151, 0.20), transparent 28%),
                radial-gradient(circle at 85% 20%, rgba(117, 96, 181, 0.16), transparent 30%),
                linear-gradient(145deg, #06191d 0%, #0a2529 48%, #07191e 100%);
            background-attachment: fixed;
            overflow-x: hidden;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: 0.22;
            background-image:
                linear-gradient(rgba(131, 215, 198, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(131, 215, 198, 0.08) 1px, transparent 1px);
            background-size: 52px 52px;
            mask-image: linear-gradient(to bottom, black, transparent 75%);
            animation: gridDrift 18s linear infinite;
        }

        .stApp::after {
            content: "";
            position: fixed;
            width: 380px;
            height: 380px;
            right: -140px;
            bottom: -140px;
            border-radius: 50%;
            pointer-events: none;
            background: radial-gradient(circle, rgba(104, 189, 221, 0.15), transparent 68%);
            animation: ambientPulse 7s ease-in-out infinite;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"],
        #MainMenu,
        footer {
            visibility: hidden;
        }

        .block-container {
            width: min(980px, 92vw);
            max-width: 980px;
            padding-top: 2.2rem;
            padding-bottom: 8rem;
            position: relative;
            z-index: 1;
        }

        .hero {
            position: relative;
            display: grid;
            grid-template-columns: 1fr 220px;
            align-items: center;
            min-height: 260px;
            margin: 0 0 2rem;
            padding: 2.5rem 3rem;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 30px;
            background: linear-gradient(135deg, rgba(15, 52, 57, 0.82), rgba(14, 34, 47, 0.65));
            box-shadow:
                0 28px 70px rgba(0, 0, 0, 0.28),
                inset 0 1px 0 rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(22px);
            animation: heroEnter 0.8s cubic-bezier(.2,.8,.2,1) both;
        }

        .hero::before {
            content: "";
            position: absolute;
            width: 300px;
            height: 300px;
            left: -160px;
            top: -170px;
            border-radius: 50%;
            background: rgba(116, 224, 196, 0.12);
            filter: blur(2px);
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            margin-bottom: 1rem;
            color: var(--mint);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--mint);
            box-shadow: 0 0 0 6px rgba(116, 224, 196, 0.10), 0 0 18px var(--mint);
            animation: statusPulse 2.2s ease-in-out infinite;
        }

        .hero h1 {
            max-width: 580px;
            margin: 0;
            font-family: "Manrope", sans-serif;
            font-size: clamp(2rem, 4.3vw, 3.55rem);
            line-height: 1.04;
            letter-spacing: -0.055em;
            color: #f3fffc;
        }

        .hero h1 span {
            color: transparent;
            background: linear-gradient(100deg, var(--mint), var(--aqua), #c3b4f5);
            background-size: 180% 180%;
            -webkit-background-clip: text;
            background-clip: text;
            animation: gradientFlow 6s ease infinite;
        }

        .hero p {
            max-width: 560px;
            margin: 1rem 0 0;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.65;
        }

        .orb-stage {
            position: relative;
            display: grid;
            place-items: center;
            height: 200px;
            perspective: 800px;
        }

        .orb {
            position: relative;
            width: 126px;
            height: 126px;
            border: 1px solid rgba(190, 255, 242, 0.42);
            border-radius: 50%;
            background:
                radial-gradient(circle at 34% 28%, rgba(255,255,255,.82) 0 2%, transparent 8%),
                radial-gradient(circle at 38% 35%, #8ef0d4, #458fa4 43%, #7865aa 72%, #172b44);
            box-shadow:
                0 0 38px rgba(102, 216, 193, 0.32),
                0 24px 45px rgba(0, 0, 0, 0.35),
                inset -18px -14px 30px rgba(13, 18, 50, 0.38),
                inset 10px 8px 24px rgba(255, 255, 255, 0.18);
            transform-style: preserve-3d;
            animation: orbFloat 5s ease-in-out infinite;
        }

        .orb::before,
        .orb::after {
            content: "";
            position: absolute;
            inset: -22px;
            border: 1px solid rgba(116, 224, 196, 0.28);
            border-radius: 50%;
            transform: rotateX(68deg) rotateZ(12deg);
            animation: orbitSpin 8s linear infinite;
        }

        .orb::after {
            inset: -38px 4px;
            border-color: rgba(169, 149, 232, 0.25);
            transform: rotateY(68deg) rotateZ(-18deg);
            animation-direction: reverse;
            animation-duration: 10s;
        }

        .orb-shadow {
            position: absolute;
            bottom: 18px;
            width: 110px;
            height: 22px;
            border-radius: 50%;
            background: rgba(58, 206, 178, 0.18);
            filter: blur(12px);
            animation: shadowBreath 5s ease-in-out infinite;
        }

        [data-testid="stChatMessage"] {
            margin: 0.85rem 0;
            padding: 1.15rem 1.25rem;
            border: 1px solid var(--line);
            border-radius: 20px;
            background: var(--panel);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.16);
            backdrop-filter: blur(16px);
            animation: messageIn 0.45s cubic-bezier(.2,.8,.2,1) both;
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        }

        [data-testid="stChatMessage"]:hover {
            transform: translateY(-2px);
            border-color: rgba(116, 224, 196, 0.28);
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.21);
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: linear-gradient(135deg, rgba(42, 102, 102, 0.72), rgba(33, 70, 84, 0.68));
        }

        [data-testid="stChatMessage"] p {
            color: #e9f8f5;
            line-height: 1.65;
        }

        [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"],
        [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] {
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 7px 18px rgba(0,0,0,.18);
        }

        [data-testid="stBottom"] {
            background: linear-gradient(to top, #06191d 60%, transparent);
        }

        [data-testid="stChatInput"] {
            border: 1px solid rgba(133, 222, 205, 0.26);
            border-radius: 20px;
            background: rgba(11, 37, 42, 0.90);
            box-shadow: 0 18px 48px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255,255,255,.05);
            backdrop-filter: blur(22px);
            transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
        }

        [data-testid="stChatInput"]:focus-within {
            transform: translateY(-2px);
            border-color: rgba(116, 224, 196, 0.62);
            box-shadow: 0 20px 55px rgba(0, 0, 0, 0.34), 0 0 0 4px rgba(116, 224, 196, 0.07);
        }

        [data-testid="stChatInput"] textarea {
            color: var(--ink);
            caret-color: var(--mint);
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: #85aaa4;
        }

        [data-testid="stChatInputSubmitButton"] {
            color: var(--mint);
            transition: transform 0.2s ease, color 0.2s ease;
        }

        [data-testid="stChatInputSubmitButton"]:hover {
            color: #c8fff1;
            transform: translateY(-2px) scale(1.08);
        }

        @keyframes heroEnter {
            from { opacity: 0; transform: translateY(22px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        @keyframes messageIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes orbFloat {
            0%, 100% { transform: translateY(0) rotateY(-8deg) rotateX(5deg); }
            50% { transform: translateY(-15px) rotateY(10deg) rotateX(-4deg); }
        }

        @keyframes shadowBreath {
            0%, 100% { transform: scale(.78); opacity: .55; }
            50% { transform: scale(1); opacity: .9; }
        }

        @keyframes orbitSpin {
            to { transform: rotateX(68deg) rotateZ(372deg); }
        }

        @keyframes statusPulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: .55; transform: scale(.82); }
        }

        @keyframes gradientFlow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        @keyframes gridDrift {
            to { background-position: 52px 52px; }
        }

        @keyframes ambientPulse {
            0%, 100% { transform: scale(.85); opacity: .65; }
            50% { transform: scale(1.15); opacity: 1; }
        }

        @media (max-width: 720px) {
            .block-container {
                width: 94vw;
                padding-top: 1rem;
            }

            .hero {
                grid-template-columns: 1fr;
                min-height: auto;
                padding: 2rem 1.5rem 1.5rem;
                border-radius: 24px;
            }

            .orb-stage {
                height: 145px;
                margin-top: 0.5rem;
                transform: scale(.8);
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                scroll-behavior: auto !important;
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
            }
        }
    </style>

    <section class="hero">
        <div class="hero-copy">
            <div class="eyebrow"><span class="status-dot"></span> A calm space, always here</div>
            <h1>Your AI mental health <span>companion.</span></h1>
            <p>Share what is on your mind. This is a private, thoughtful space to pause, reflect, and find your next small step.</p>
        </div>
        <div class="orb-stage" aria-hidden="true">
            <div class="orb-shadow"></div>
            <div class="orb"></div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Step2: User is able to ask question
# Chat input
user_input = st.chat_input("What's on your mind today?")
if user_input:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # AI Agent exists here
    response = requests.post(BACKEND_URL, json={"message": user_input})

    st.session_state.chat_history.append({"role": "assistant", "content": f'{response.json()["response"]} WITH TOOL: [{response.json()["tool_called"]}]'})


# Step3: Show response from backend
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
