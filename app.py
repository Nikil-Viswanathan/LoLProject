import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="LoL: Higher or Lower", layout="wide")
@st.cache_data
def load_data():
    return pd.read_csv("sg2_match_dataset.csv")

data = load_data()

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

def pick_new_matchup():
    matchid = random.choice(data["match_id"].unique())
    match_data = data[data["match_id"] == matchid]
    winteam = match_data[match_data["win"] == True]
    loseteam = match_data[match_data["win"] == False]
    winnerchamp = winteam.sample(1).iloc[0]
    loserchamp = loseteam.sample(1).iloc[0]
    matchup = [winnerchamp, loserchamp]
    random.shuffle(matchup)
    st.session_state.champ1 = matchup[0]
    st.session_state.champ2 = matchup[1]
    stats_to_compare = ["kills", "damage", "gold", "cs"]
    st.session_state.stat = random.choice(stats_to_compare)

if 'champ1' not in st.session_state:
    pick_new_matchup()

def display_scoreboard():
    c1 = st.session_state.champ1
    c2 = st.session_state.champ2
    secret_stat = st.session_state.stat
    
    matchup_df = pd.DataFrame([c1, c2])
    
    columns_to_show = [
        "champion", "lane", "level", "kills", "deaths", "assists", "damage", "gold", "cs", "vision", "win", "timePlayed"
    ]
    display_df = matchup_df[columns_to_show].copy()
    display_df["win"] = display_df["win"].map({True: "✅", False: "❌"})
    display_df["lane"] = display_df["lane"].map({"TOP": "Top", "MIDDLE": "Mid", "JUNGLE":"Jungle", "BOTTOM" : "Bottom", "UTILITY": "Support"})
    display_df["timePlayed"] = display_df["timePlayed"].apply(lambda x: f"{x//60}:{x%60:02d}")
    if secret_stat in columns_to_show:
        display_df[secret_stat] = "?"
    display_df = display_df.rename(columns={
        "champion": "Champion",
        "win": "Game won?",
        "lane": "Role",
        "level": "Level",
        "kills": "Kills",
        "deaths": "Deaths",
        "assists": "Assists",
        "damage": "Damage",
        "gold": "Gold",
        "cs": "CS",
        "vision": "Vision Score",
        "timePlayed": "Match Length"
    })
    st.write("---") 
    st.write(f"### Matchup Scoreboard")
    st.write(f"*The **{secret_stat.capitalize()}** column has been hidden.*")
    
    st.dataframe(display_df, hide_index=True) 

st.markdown("<h1 style='color: #FFD700; text-align: center;'>League of Legends: Higher or Lower</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>(Random sample of games from Silver to Emerald as of 21-4-2026)</p>", unsafe_allow_html=True)
st.subheader(f"Current Score: {st.session_state.score}")


# Main Game Logic
if not st.session_state.game_over:
    c1 = st.session_state.champ1
    c2 = st.session_state.champ2
    stat = st.session_state.stat
    if stat == "kills":
        st.markdown("### Who had more :orange[KILLS] in their match?")
    elif stat == "damage":
        st.markdown(f"### Who had more :red[DAMAGE] in their match?")
    elif stat == "gold":
        st.markdown("### Who had more :color[GOLD]{foreground='#FFD700'} in their match?")
    else:
        st.markdown("### Who had more :green[CS] in their match?")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**{c1['champion']}**")
        if st.button(f"Choose {c1['champion']}", key="btn1", use_container_width=True):
            if c1[stat] >= c2[stat]:
                st.success("Correct!")
                st.session_state.score += 1
                time.sleep(2)
                pick_new_matchup()
                st.rerun()
            else:
                st.session_state.game_over = True
                st.rerun()

    with col2:
        st.info(f"**{c2['champion']}**")
        if st.button(f"Choose {c2['champion']}", key="btn2", use_container_width=True):
            if c2[stat] >= c1[stat]:
                st.success("Correct!")
                st.session_state.score += 1
                time.sleep(2)
                pick_new_matchup()
                st.rerun()
            else:
                st.session_state.game_over = True
                st.rerun()

    display_scoreboard()

else:
    # Game Over Screen
    st.error("Wrong! Game Over.")
    
    c1 = st.session_state.champ1
    c2 = st.session_state.champ2
    stat = st.session_state.stat
    
    st.write("### The actual stats were:")
    st.write(f"- **{c1['champion']}**: {c1[stat]:,} {stat}")
    st.write(f"- **{c2['champion']}**: {c2[stat]:,} {stat}")
    
    if st.button("Play Again", use_container_width=True):
        st.session_state.score = 0
        st.session_state.game_over = False
        pick_new_matchup()
        st.rerun()