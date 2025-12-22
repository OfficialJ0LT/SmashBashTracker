import streamlit as st
import pandas as pd
import base64
import json

# 1. SETTINGS & CONFIG
st.set_page_config(page_title="Smash Iron Man: Grand Tour", layout="wide")

# --- BACKGROUND ENGINE ---
def apply_background(bg_type, current_game=None):
    era_bgs = {
        "Smash 64 (Stock)": "https://wallpaperaccess.com/full/1164817.jpg",
        "Smash Remix": "https://cdn.discordapp.com/attachments/1452593220780294244/1452599486093463665/64.jpg?ex=694a6631&is=694914b1&hm=dd2d9aec7e95dc1d650023aff9ac8bebed03e2f56fab69695ae63304b1c6315e&",
        "Melee": "https://cdn.discordapp.com/attachments/1452593220780294244/1452594303984730264/melee.webp?ex=694a615d&is=69490fdd&hm=f41b1641021dd047bc31fedcd5462dbacb199869469f9cbc82c79979973aae70&", 
        "Melee Beyond": "insert link",
        "Project+": "https://cdn.discordapp.com/attachments/1452593220780294244/1452602519489613904/p.jpg?ex=694a6904&is=69491784&hm=f2bb905e72cb0c7c439d565bad5d21567a1bf229d762da17cfe75ac31ab271fc&",
        "Brawl": "Instert link",
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
    "Smash 64 (Stock)": ["64: Mario Bros", "64: Hyrule & Dreamland", "64: Sector Z & Kanto"],
    "Smash Remix": [
        "Remix: New Challengers 1", 
        "Remix: New Challengers 2", 
        "Remix: Guest Legends", 
        "Remix: Left side bonus line"
    ],
    "Melee": ["Melee: Mario Bros", "Melee: Starfox and Zelda", "Melee: Pokemon and sword dudes"],
    "Melee Beyond": [
        "Beyond: Modded Wave 1", 
        "Beyond: Modded Wave 2", 
        "Beyond: Modded Wave 3", 
        "Beyond: Final Expansion"
    ],
    "Project+": [
        "P+: Mario Bros", 
        "P+: Star Fox & Zelda", 
        "P+: Pokemon",
        "P+: Floaters and sword pricks", 
        "P+: Newcomer Finale" # Total of 5 lines
    ],
    "Brawl": ["Brawl: Classics", "Brawl: Luigi - Snake", "Brawl: Peach - Sonic", "Brawl: Final Smash"],
    "Smash 4": ["S4: Mario - Little mac", "S4: Link - Robin", "S4: Duck Hunt - Greninja","S4: Nintendo All-Stars", "S4: Friends"],
    "Ultimate": ["ULT: Mario - JigglyPuff, "ULT: Peach - Ganandorf, "Mewtwo - Diddykong", "ULT: Lucas - Little Mac", "ULT: Greninja - Inkling", "ULT: Ridley - Min Min", "ULT: DLC Finale"]
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

# Safety sync
st.session_state.selected_games = [g for g in st.session_state.selected_games if g in MASTER_DATA]

active_game_data = {k: MASTER_DATA[k] for k in st.session_state.selected_games}
all_lines = [line for lines in active_game_data.values() for line in lines]
curr_idx = st.session_state.current_line_idx
marathon_finished = curr_idx >= len(all_lines) if all_lines else False

# Logic for current game
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

# 4. SIDEBAR
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
    if st.button("Full Reset", type="secondary"):
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

    # --- ADVANCE & UNDO BAR ---
    st.divider()
    ctrl_c1, ctrl_c2 = st.columns([3, 1])
    
    with ctrl_c1:
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
            st.button("Confirm & Advance", disabled=True, use_container_width=True, help="Finish 3 players to advance")

    with ctrl_c2:
        if st.session_state.current_line_idx > 0:
            if st.button("↩️ UNDO", use_container_width=True, help="Go back one line and revert points"):
                # 1. Get last result
                last_res = st.session_state.history.pop()
                # 2. Subtract points
                for name in st.session_state.player_names:
                    st.session_state.scores[name] -= last_res.get(name, 0)
                # 3. Handle Era Win Reversion
                prev_line = last_res["Line"]
                for era, lines in MASTER_DATA.items():
                    if prev_line in lines and lines[-1] == prev_line:
                        st.session_state.era_wins[era] = "TBD"
                # 4. Decrement index
                st.session_state.current_line_idx -= 1
                st.session_state.finished_this_line = []
                st.rerun()

else:
    # --- GRAND FINALE ---
    st.balloons(); st.snow()
    final_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    winner_name = final_scores[0][0]
    st.markdown(f'<div style="text-align: center; border: 10px solid gold; padding: 20px;"><h1>🏆 CHAMPION: {winner_name}</h1></div>', unsafe_allow_html=True)
    
    # Hall of Fame Row
    st.subheader("🏛️ Hall of Fame (Era Trophies)")
    fame_cols = st.columns(4)
    for i, name in enumerate(st.session_state.player_names):
        count = list(st.session_state.era_wins.values()).count(name)
        fame_cols[i].metric(label=name, value=f"{count} Trophies", delta="🏆" * count if count > 0 else None)

    st.divider()
    st.subheader("🥇 Final Standings")
    l_cols = st.columns(4)
    for idx, (player, score) in enumerate(final_scores):
        l_cols[idx].metric(label=f"Rank #{idx+1}", value=player, delta=f"{score} Total Pts")
    
    if st.button("↩️ Undo Last Line", use_container_width=True):
        last_res = st.session_state.history.pop()
        for name in st.session_state.player_names: st.session_state.scores[name] -= last_res.get(name, 0)
        st.session_state.current_line_idx -= 1; st.rerun()

if st.session_state.history:
    with st.expander("📊 Full Match History"): st.table(pd.DataFrame(st.session_state.history))


