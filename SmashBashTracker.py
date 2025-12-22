import streamlit as st
import pandas as pd
import base64
import json

# 1. SETTINGS & CONFIG (MUST BE FIRST)
st.set_page_config(page_title="Smash Iron Man: Grand Tour", layout="wide")

# --- BACKGROUND ENGINE ---
def apply_background(bg_type, current_game=None):
    era_bgs = {
        "Smash Remix": "https://cdn.discordapp.com/attachments/1452593220780294244/1452599486093463665/64.jpg?ex=694a6631&is=694914b1&hm=dd2d9aec7e95dc1d650023aff9ac8bebed03e2f56fab69695ae63304b1c6315e&",
        "Melee": "https://cdn.discordapp.com/attachments/1452593220780294244/1452594303984730264/melee.webp?ex=694a615d&is=69490fdd&hm=f41b1641021dd047bc31fedcd5462dbacb199869469f9cbc82c79979973aae70&", 
        "Project+": "https://cdn.discordapp.com/attachments/1452593220780294244/1452602519489613904/p.jpg?ex=694a6904&is=69491784&hm=f2bb905e72cb0c7c439d565bad5d21567a1bf229d762da17cfe75ac31ab271fc&",
        "Smash 4": "https://cdn.discordapp.com/attachments/1452593220780294244/1452596054854860850/wii_u.webp?ex=694a62ff&is=6949117f&hm=dd93e44659c848b03445c2ba9995b0bfada3081685de7da954a9343d754a0640&",
        "Ultimate": "https://cdn.discordapp.com/attachments/1452593220780294244/1452596756713046126/ultimate.webp?ex=694a63a6&is=69491226&hm=64f91e457dd6bf117a8279a11a784445ea47f452d9b56909aa890213ed9be0b5&",
        "Complete!": "https://cdn.discordapp.com/attachments/1452593220780294244/1452597354157838376/win.webp?ex=694a6435&is=694912b5&hm=d7f9f512510a2ff43d37e636dd17e85ce7d2e29818baddd151ec67d292e80209&"
    }
    url = era_bgs.get(current_game, era_bgs["Ultimate"])
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("{url}"); background-size: cover; background-attachment: fixed; }}
        [data-testid="stAppViewContainer"] {{ background-color: rgba(0, 0, 0, 0.75); }}
        [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.85); }}
        .stButton>button {{ border: 2px solid gold; background-color: rgba(0,0,0,0.5); color: white; }}
        .gold-winner {{ color: gold !important; font-weight: bold; }}
        h1, h2, h3, p, span, [data-testid="stMetricValue"] {{ color: white !important; }}
        </style>
    """, unsafe_allow_html=True)

# 2. MASTER DATA
MASTER_DATA = {
    "Smash Remix": ["64: The OG 12", "64: Melee Era", "64: Brawl/Ult Era", "64: The Guests", "64: The Oddballs"],
    "Melee": ["Melee: Line 1", "Melee: Line 2", "Melee: Line 3", "Melee: Line 4", "Melee: Line 5"],
    "Project+": ["P+: The Heavies", "P+: Star Fox & Zelda", "P+: Retro & Pokemon", "P+: The Rivals"],
    "Smash 4": ["S4: Mushroom Kingdom", "S4: Hyrule & Icarus", "S4: Dream Land & Poke", "S4: 3rd Party", "S4: DLC Wave", "S4: Final Slots"],
    "Ultimate": ["ULT: #01-#10", "ULT: #11-#20", "ULT: #21-#30", "ULT: #31-#40", "ULT: #41-#50", "ULT: #51-#60", "ULT: #61-#70", "ULT: #71-#80", "ULT: Final DLC/Mods"]
}

# 3. SESSION STATE
if 'initialized' not in st.session_state:
    st.session_state.selected_games = list(MASTER_DATA.keys())
    st.session_state.current_line_idx = 0
    st.session_state.player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
    st.session_state.scores = {name: 0 for name in st.session_state.player_names}
    st.session_state.era_wins = {game: "TBD" for game in MASTER_DATA.keys()}
    st.session_state.finished_this_line = []
    st.session_state.history = []
    st.session_state.initialized = True

# Safety sync for game names
st.session_state.selected_games = [g for g in st.session_state.selected_games if g in MASTER_DATA]

# Build Active Lines
active_game_data = {k: MASTER_DATA[k] for k in st.session_state.selected_games}
all_lines = [line for lines in active_game_data.values() for line in lines]
curr_idx = st.session_state.current_line_idx
marathon_finished = curr_idx >= len(all_lines) if all_lines else False

# Logic to find current game info
current_game = "Complete!"
game_lines, game_line_num, next_game = [], 0, "THE END"
if not marathon_finished and all_lines:
    temp_count = 0
    for game, lines in active_game_data.items():
        if temp_count <= curr_idx < temp_count + len(lines):
            current_game, game_lines, game_line_num = game, lines, (curr_idx - temp_count) + 1
            keys = list(active_game_data.keys()); idx = keys.index(game)
            next_game = keys[idx+1] if idx+1 < len(keys) else "THE END"
            break
        temp_count += len(lines)

# 4. SIDEBAR (UI)
with st.sidebar:
    st.header("📂 Restore Progress")
    uploaded_file = st.file_uploader("Upload .json backup", type="json")
    if uploaded_file and st.button("✅ Confirm Restore", use_container_width=True):
        data = json.load(uploaded_file)
        for key in data: st.session_state[key] = data[key]
        st.rerun()

    st.divider()
    st.header("⚙️ Game Setup")
    can_edit = st.session_state.current_line_idx == 0
    new_selection = st.multiselect("Included Games", options=list(MASTER_DATA.keys()), default=st.session_state.selected_games, disabled=not can_edit)
    if can_edit and new_selection != st.session_state.selected_games:
        st.session_state.selected_games = new_selection; st.rerun()

    st.divider()
    st.header("👥 Player Names")
    for i in range(4):
        old_n = st.session_state.player_names[i]
        new_n = st.text_input(f"P{i+1}", value=old_n, key=f"input_p{i}")
        if new_n != old_n:
            st.session_state.scores[new_n] = st.session_state.scores.pop(old_n, 0)
            st.session_state.player_names[i] = new_n; st.rerun()

    # --- SAVE BUTTON (Safe Position) ---
    st.divider()
    st.header("💾 Save Progress")
    save_blob = {k: st.session_state[k] for k in ["current_line_idx", "player_names", "scores", "era_wins", "history", "selected_games"]}
    st.download_button("📥 Download Checkpoint", json.dumps(save_blob), "smash_save.json", use_container_width=True)

    st.divider()
    st.header("🏆 Era Champions")
    for era in st.session_state.selected_games:
        champ = st.session_state.era_wins.get(era, "TBD")
        if champ != "TBD": st.markdown(f"<span class='gold-winner'>{era}: {champ}</span>", unsafe_allow_html=True)
        else: st.write(f"{era}: {champ}")

    st.divider()
    if st.button("Full Reset", type="secondary", help="Danger: This clears all current progress!"):
        st.session_state.clear(); st.rerun()

# 5. MAIN UI
apply_background("Auto Era", current_game)
st.title("🎮 Smash Bash Tracker")

if not all_lines:
    st.warning("Please select at least one game in the sidebar!")
elif not marathon_finished:
    # --- HUD ---
    c1, c2, c3 = st.columns([2,2,1])
    with c1: 
        st.metric("Total Progress", f"{curr_idx + 1} / {len(all_lines)}")
        st.progress((curr_idx + 1) / len(all_lines))
    with c2: 
        st.metric(f"{current_game} Progress", f"{game_line_num} / {len(game_lines)}")
        st.progress(game_line_num / len(game_lines))
    with c3: st.info(f"Next: {next_game}")

    st.header(f"📍 Current Line: {all_lines[curr_idx]}")
    hud = st.columns(4)
    for i, name in enumerate(st.session_state.player_names):
        trophies = list(st.session_state.era_wins.values()).count(name)
        hud[i].metric(label=f"{name} ({trophies} 🏆)", value=f"{st.session_state.scores[name]} pts")

    # Scoring Buttons
    skip_mode = len(st.session_state.finished_this_line) >= 3
    btns = st.columns(4)
    for i, name in enumerate(st.session_state.player_names):
        with btns[i]:
            if st.button(f"DONE: {name}", disabled=(name in st.session_state.finished_this_line or skip_mode), key=f"btn_{i}", use_container_width=True):
                st.session_state.finished_this_line.append(name); st.rerun()

    if skip_mode:
        if st.button("🚀 CONFIRM & ADVANCE", type="primary", use_container_width=True):
            pts = [4, 3, 2, 0]
            results = {"Line": all_lines[curr_idx]}
            for i, p in enumerate(st.session_state.finished_this_line):
                st.session_state.scores[p] += pts[i]; results[p] = pts[i]
            skipper = list(set(st.session_state.player_names) - set(st.session_state.finished_this_line))[0]
            results[skipper] = 0; st.session_state.history.append(results)
            
            if game_line_num == len(game_lines):
                era_scores = {n: sum(r.get(n, 0) for r in st.session_state.history if r["Line"] in game_lines) for n in st.session_state.player_names}
                st.session_state.era_wins[current_game] = max(era_scores, key=era_scores.get)
            
            st.session_state.current_line_idx += 1; st.session_state.finished_this_line = []; st.rerun()

else:
    # --- GRAND FINALE & HALL OF FAME ---
    st.balloons(); st.snow()
    final_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    winner_name = final_scores[0][0]
    
    st.markdown(f"""
        <div style="text-align: center; padding: 30px; border: 10px solid gold; border-radius: 20px; background-color: rgba(255, 215, 0, 0.15); margin-bottom: 40px;">
            <h1 style="color: gold; font-size: 70px;">🏆 GRAND CHAMPION 🏆</h1>
            <h2 style="font-size: 90px; margin: 0;">{winner_name}</h2>
            <p style="font-size: 28px;">Victory with {st.session_state.scores[winner_name]} total points!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🏛️ Hall of Fame (Era Trophies)")
    fame_cols = st.columns(4)
    for i, name in enumerate(st.session_state.player_names):
        count = list(st.session_state.era_wins.values()).count(name)
        fame_cols[i].metric(label=name, value=f"{count} Trophies", delta="🏆" * count if count > 0 else None)

    st.divider()
    st.subheader("🥇 Final Marathon Standings")
    leaderboard_cols = st.columns(4)
    for idx, (player, score) in enumerate(final_scores):
        leaderboard_cols[idx].metric(label=f"Rank #{idx+1}", value=player, delta=f"{score} Total Pts")

if st.session_state.history:
    with st.expander("📊 Full Match History"): st.table(pd.DataFrame(st.session_state.history))
