import html
import random

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Rift Rankings | Higher or Lower",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


STAT_CONFIG = {
    "kills": {"label": "Kills", "accent": "#f36b57", "hint": "Champion takedowns"},
    "damage": {"label": "Damage", "accent": "#df4f71", "hint": "Damage dealt to champions"},
    "gold": {"label": "Gold", "accent": "#d6a84b", "hint": "Total gold earned"},
    "cs": {"label": "CS", "accent": "#63c6a5", "hint": "Minions and monsters slain"},
}

ROLE_LABELS = {
    "TOP": "Top",
    "MIDDLE": "Mid",
    "JUNGLE": "Jungle",
    "BOTTOM": "Bottom",
    "UTILITY": "Support",
}


@st.cache_data
def load_data():
    return pd.read_csv("sg2_match_dataset.csv")


data = load_data()


def init_state():
    defaults = {
        "score": 0,
        "best_score": 0,
        "round": 1,
        "game_over": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def pick_new_matchup():
    match_id = random.choice(data["match_id"].unique())
    match_data = data[data["match_id"] == match_id]
    winner = match_data[match_data["win"] == True].sample(1).iloc[0]
    loser = match_data[match_data["win"] == False].sample(1).iloc[0]
    matchup = [winner, loser]
    random.shuffle(matchup)

    st.session_state.champ1 = matchup[0]
    st.session_state.champ2 = matchup[1]
    st.session_state.stat = random.choice(list(STAT_CONFIG))


def format_duration(seconds):
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"


def format_value(value):
    return f"{int(value):,}"


def champion_card(champion, side):
    name = html.escape(str(champion["champion"]))
    role = ROLE_LABELS.get(champion["lane"], str(champion["lane"]).title())
    result = "Victory" if bool(champion["win"]) else "Defeat"
    result_class = "victory" if bool(champion["win"]) else "defeat"
    kills = "?" if st.session_state.stat == "kills" else int(champion["kills"])
    initials = "".join(part[0] for part in name.replace("'", " ").split())[:2].upper()
    if len(initials) < 2:
        initials = name[:2].upper()

    st.markdown(
        f"""
        <div class="champ-card {side}">
            <div class="card-topline">
                <span class="side-label">CONTENDER {side[-1]}</span>
                <span class="result-pill {result_class}">{result}</span>
            </div>
            <div class="champ-identity">
                <div class="champ-avatar">{initials}</div>
                <div>
                    <div class="champ-name">{name}</div>
                    <div class="champ-role">{role} · Level {int(champion["level"])}</div>
                </div>
            </div>
            <div class="quick-stats">
                <div><strong>{kills}/{int(champion["deaths"])}/{int(champion["assists"])}</strong><span>KDA</span></div>
                <div><strong>{int(champion["vision"])}</strong><span>Vision</span></div>
                <div><strong>{format_duration(champion["timePlayed"])}</strong><span>Game time</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_scoreboard(reveal=False):
    c1 = st.session_state.champ1
    c2 = st.session_state.champ2
    secret_stat = st.session_state.stat
    matchup_df = pd.DataFrame([c1, c2])

    columns = [
        "champion",
        "lane",
        "level",
        "kills",
        "deaths",
        "assists",
        "damage",
        "gold",
        "cs",
        "vision",
        "win",
        "timePlayed",
    ]
    display_df = matchup_df[columns].copy()
    display_df["win"] = display_df["win"].map({True: "Victory", False: "Defeat"})
    display_df["lane"] = display_df["lane"].map(ROLE_LABELS)
    display_df["timePlayed"] = display_df["timePlayed"].apply(format_duration)

    if not reveal:
        display_df[secret_stat] = "Hidden"

    display_df = display_df.rename(
        columns={
            "champion": "Champion",
            "win": "Result",
            "lane": "Role",
            "level": "Level",
            "kills": "Kills",
            "deaths": "Deaths",
            "assists": "Assists",
            "damage": "Damage",
            "gold": "Gold",
            "cs": "CS",
            "vision": "Vision",
            "timePlayed": "Duration",
        }
    )

    st.markdown("### Match scoreboard")
    if not reveal:
        st.caption(f"{STAT_CONFIG[secret_stat]['label']} stays hidden until the round ends.")
    st.dataframe(display_df, hide_index=True, width="stretch")


def handle_guess(selected, other):
    stat = st.session_state.stat
    if selected[stat] >= other[stat]:
        st.session_state.score += 1
        st.session_state.best_score = max(
            st.session_state.best_score, st.session_state.score
        )
        st.session_state.round += 1
        pick_new_matchup()
        st.toast("Correct. Next matchup ready.", icon="✅")
    else:
        st.session_state.game_over = True
    st.rerun()


def restart_game():
    st.session_state.score = 0
    st.session_state.round = 1
    st.session_state.game_over = False
    pick_new_matchup()
    st.rerun()


init_state()
if "champ1" not in st.session_state:
    pick_new_matchup()

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

        :root {
            --ink: #f3f6f4;
            --muted: #8d9994;
            --panel: rgba(18, 25, 27, .88);
            --line: rgba(255, 255, 255, .09);
            --gold: #d6a84b;
            --green: #63c6a5;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% -10%, rgba(99, 198, 165, .16), transparent 34%),
                radial-gradient(circle at 95% 8%, rgba(214, 168, 75, .13), transparent 30%),
                #090d0e;
            color: var(--ink);
            font-family: "DM Sans", sans-serif;
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stMainBlockContainer"] {
            max-width: 1120px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3, .champ-name, .score-value {
            font-family: "Space Grotesk", sans-serif !important;
        }

        .hero {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 2rem;
            margin: .3rem 0 2rem;
        }
        .eyebrow {
            color: var(--green);
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .18em;
            margin-bottom: .65rem;
        }
        .hero h1 {
            color: var(--ink);
            font-size: clamp(2.2rem, 6vw, 4.7rem);
            letter-spacing: -.07em;
            line-height: .92;
            margin: 0;
        }
        .hero p {
            color: var(--muted);
            max-width: 430px;
            margin: 1rem 0 0;
            line-height: 1.55;
        }
        .scoreboard {
            display: flex;
            gap: .65rem;
            flex-shrink: 0;
        }
        .score-box {
            min-width: 96px;
            padding: .8rem 1rem;
            background: rgba(255,255,255,.035);
            border: 1px solid var(--line);
            border-radius: 14px;
        }
        .score-label {
            color: var(--muted);
            display: block;
            font-size: .65rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
        }
        .score-value {
            color: var(--ink);
            display: block;
            font-size: 1.65rem;
            line-height: 1.1;
            margin-top: .25rem;
        }

        .challenge {
            padding: 1.15rem 1.3rem;
            background: linear-gradient(90deg, rgba(214,168,75,.11), rgba(255,255,255,.025));
            border: 1px solid rgba(214,168,75,.24);
            border-radius: 16px;
            margin-bottom: 1rem;
        }
        .challenge-kicker {
            color: var(--gold);
            font-size: .68rem;
            font-weight: 700;
            letter-spacing: .14em;
        }
        .challenge-title {
            color: var(--ink);
            font-family: "Space Grotesk", sans-serif;
            font-size: clamp(1.25rem, 3vw, 1.8rem);
            font-weight: 700;
            margin-top: .22rem;
        }
        .challenge-hint { color: var(--muted); font-size: .82rem; }

        .champ-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 18px;
            min-height: 230px;
            padding: 1.3rem;
            position: relative;
            overflow: hidden;
        }
        .champ-card::after {
            content: "";
            position: absolute;
            width: 170px;
            height: 170px;
            right: -60px;
            bottom: -80px;
            border-radius: 50%;
            background: rgba(99,198,165,.07);
            filter: blur(2px);
        }
        .champ-card.side-2::after { background: rgba(214,168,75,.08); }
        .card-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .side-label {
            color: var(--muted);
            font-size: .65rem;
            font-weight: 700;
            letter-spacing: .13em;
        }
        .result-pill {
            border-radius: 99px;
            font-size: .67rem;
            font-weight: 700;
            padding: .28rem .55rem;
        }
        .victory { color: #76d5b5; background: rgba(99,198,165,.12); }
        .defeat { color: #ee826f; background: rgba(243,107,87,.11); }
        .champ-identity {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 2rem 0;
        }
        .champ-avatar {
            align-items: center;
            background: linear-gradient(135deg, #243538, #172123);
            border: 1px solid rgba(255,255,255,.12);
            border-radius: 16px;
            color: var(--green);
            display: flex;
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            height: 64px;
            justify-content: center;
            width: 64px;
        }
        .side-2 .champ-avatar { color: var(--gold); }
        .champ-name {
            color: var(--ink);
            font-size: 1.65rem;
            font-weight: 700;
            letter-spacing: -.04em;
        }
        .champ-role { color: var(--muted); font-size: .8rem; margin-top: .2rem; }
        .quick-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: .55rem;
            position: relative;
            z-index: 1;
        }
        .quick-stats div {
            background: rgba(255,255,255,.025);
            border: 1px solid rgba(255,255,255,.055);
            border-radius: 10px;
            padding: .55rem .65rem;
        }
        .quick-stats strong { color: var(--ink); display: block; font-size: .82rem; }
        .quick-stats span { color: var(--muted); display: block; font-size: .62rem; margin-top: .15rem; }

        .versus {
            color: var(--muted);
            font-family: "Space Grotesk", sans-serif;
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .12em;
            margin: .8rem 0;
            text-align: center;
        }

        .stButton > button {
            background: #eef3f0;
            border: 0;
            border-radius: 11px;
            color: #0b1112;
            font-weight: 700;
            min-height: 3rem;
            transition: transform .15s ease, background .15s ease;
        }
        .stButton > button:hover {
            background: #ffffff;
            color: #0b1112;
            transform: translateY(-1px);
        }
        [data-testid="stExpander"] {
            background: rgba(255,255,255,.025);
            border: 1px solid var(--line);
            border-radius: 14px;
            margin-top: 1.5rem;
        }
        [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

        .game-over {
            background: linear-gradient(135deg, rgba(243,107,87,.12), rgba(255,255,255,.025));
            border: 1px solid rgba(243,107,87,.24);
            border-radius: 18px;
            margin: 1rem 0;
            padding: 1.4rem;
            text-align: center;
        }
        .game-over .label { color: #ee826f; font-size: .7rem; font-weight: 700; letter-spacing: .15em; }
        .game-over .final { color: var(--ink); font-family: "Space Grotesk", sans-serif; font-size: 2rem; font-weight: 700; margin: .25rem 0; }
        .game-over .copy { color: var(--muted); font-size: .85rem; }
        .answer-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: .7rem;
            margin: 1rem 0;
        }
        .answer {
            background: rgba(255,255,255,.035);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: .9rem;
        }
        .answer span { color: var(--muted); display: block; font-size: .7rem; }
        .answer strong { color: var(--ink); display: block; font-family: "Space Grotesk", sans-serif; font-size: 1.35rem; margin-top: .2rem; }

        footer { visibility: hidden; }
        @media (max-width: 760px) {
            [data-testid="stMainBlockContainer"] { padding-top: 1.2rem; }
            .hero { align-items: flex-start; flex-direction: column; gap: 1.2rem; }
            .hero h1 { font-size: 3rem; }
            .scoreboard { width: 100%; }
            .score-box { flex: 1; }
            .champ-card { min-height: auto; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
        <div>
            <div class="eyebrow">RIFT RANKINGS · HIGHER OR LOWER</div>
            <h1>Read the match.<br>Call the stat.</h1>
            <p>Two players from the same ranked game. One hidden stat. Pick who posted the higher number.</p>
        </div>
        <div class="scoreboard">
            <div class="score-box"><span class="score-label">Score</span><span class="score-value">{st.session_state.score}</span></div>
            <div class="score-box"><span class="score-label">Best</span><span class="score-value">{st.session_state.best_score}</span></div>
            <div class="score-box"><span class="score-label">Round</span><span class="score-value">{st.session_state.round}</span></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1 = st.session_state.champ1
c2 = st.session_state.champ2
stat = st.session_state.stat
stat_config = STAT_CONFIG[stat]

if not st.session_state.game_over:
    st.markdown(
        f"""
        <div class="challenge">
            <div class="challenge-kicker">THIS ROUND</div>
            <div class="challenge-title">Who had more <span style="color:{stat_config['accent']}">{stat_config['label']}</span>?</div>
            <div class="challenge-hint">{stat_config['hint']} · ties count as correct</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        champion_card(c1, "side-1")
        if st.button(
            f"Choose {c1['champion']}",
            key="choose_1",
            width="stretch",
            type="primary",
        ):
            handle_guess(c1, c2)

    with col2:
        champion_card(c2, "side-2")
        if st.button(
            f"Choose {c2['champion']}",
            key="choose_2",
            width="stretch",
            type="primary",
        ):
            handle_guess(c2, c1)

    st.markdown('<div class="versus">SAME MATCH · ONE DECISION</div>', unsafe_allow_html=True)
    display_scoreboard()

else:
    st.markdown(
        f"""
        <div class="game-over">
            <div class="label">RUN COMPLETE</div>
            <div class="final">{st.session_state.score} correct call{"s" if st.session_state.score != 1 else ""}</div>
            <div class="copy">The hidden {stat_config['label'].lower()} totals are revealed below.</div>
        </div>
        <div class="answer-grid">
            <div class="answer"><span>{html.escape(str(c1["champion"]))}</span><strong>{format_value(c1[stat])}</strong></div>
            <div class="answer"><span>{html.escape(str(c2["champion"]))}</span><strong>{format_value(c2[stat])}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Start a new run", width="stretch", type="primary"):
        restart_game()

    display_scoreboard(reveal=True)
