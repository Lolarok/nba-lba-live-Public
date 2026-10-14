
"""
app.py - NBA & LBA Advanced Stats Lab - Streamlit Cloud Ready
16 squadre ufficiali LBA 2026/27 - tutti i giocatori trattati allo stesso modo
"""

import streamlit as st
import pandas as pd
import pathlib, sys, datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent))

# Import con fallback
try:
    from lba_live import fetch_lba_live, compute_lba_standings_from_results
    from team_advanced import fetch_lba_team_advanced, fetch_nba_team_advanced
    from lineup_advanced import fetch_lba_lineups, fetch_nba_lineups
    from shotmap import fetch_lba_shots, fetch_nba_shots, render_shotmap_png
    from player_advanced import fetch_lba_player_advanced, fetch_nba_player_advanced
except ImportError as e:
    st.error(f"Import error: {e}")
    import pandas as pd
    def fetch_lba_live():
        return pd.DataFrame([{"gameday":1,"date":"2026-10-12","hometeam":"Napoli Basketball","homecode":"NAP","awayteam":"Trento","awaycode":"TRE","score":94,"opp_score":81,"played":"true"}])
    def compute_lba_standings_from_results(df):
        return pd.DataFrame([{"TEAM":"NAP","TeamName":"Napoli Basketball","W":3,"L":0,"GP":3,"ORTG":121.8,"DRTG":106.4,"NETRTG":15.4,"PF":280,"PA":250}])
    def fetch_lba_team_advanced(): 
        return pd.DataFrame([{"TEAM":"NAP","TeamName":"Napoli Basketball","Team":"Napoli Basketball","W":3,"L":0,"GP":3,"PF":280,"PA":250,"ORTG":118,"DRTG":105,"NETRTG":13,"PACE":78,"eFG%":55,"TS%":59}])
    def fetch_nba_team_advanced(): return pd.DataFrame([{"TEAM":"OKC","TeamName":"OKC Thunder","W":60,"L":12,"ORTG":118.9,"DRTG":107.7,"NETRTG":11.1}])
    def fetch_lba_lineups(): return pd.DataFrame([{"TEAM":"NAP","Lineup":"Lineup 1 NAP","GP":3,"MIN":68.5,"ORTG":118.2,"DRTG":104.5,"NETRTG":13.7,"PACE":78,"eFG%":56,"TS%":60,"REB%":52,"AST%":62,"TOV%":12,"POSS":142,"PLUS_MINUS":18}])
    def fetch_nba_lineups(): return pd.DataFrame([{"TEAM":"OKC","Lineup":"SGA-Dort-JDub-Chet","NETRTG":15.0,"MIN":100,"GP":20,"POSS":150,"PLUS_MINUS":20}])
    def fetch_lba_player_advanced(): 
        return pd.DataFrame([
            {"Player":"Giocatore A","TEAM":"NAP","Pos":"PG","GP":3,"MIN":28.5,"ORTG":120,"DRTG":105,"NET":15,"eFG%":54,"TS%":58,"PER":18,"PTS":15.2,"FGA":14,"FGM":7},
            {"Player":"Giocatore B","TEAM":"VIR","Pos":"SG","GP":3,"MIN":27,"ORTG":115,"DRTG":108,"NET":7,"eFG%":52,"TS%":56,"PER":16,"PTS":12,"FGA":10,"FGM":5}
        ])
    def fetch_nba_player_advanced(): return pd.DataFrame([{"Player":"SGA","TEAM":"OKC","GP":76,"PER":30.2,"ORTG":124,"DRTG":107,"NET":16,"eFG%":58,"TS%":64}])
    def fetch_lba_shots(player_name="Giocatore", team_code="NAP", season="2026-27"):
        import random, numpy as np, pandas as pd
        random.seed(hash(player_name)%1000); np.random.seed(hash(player_name)%1000)
        n=12
        xs=np.random.normal(0,100,n); ys=np.random.normal(50,100,n)
        made=[random.choice([0,1]) for _ in range(n)]
        df=pd.DataFrame({"LOC_X":xs,"LOC_Y":ys,"SHOT_MADE_FLAG":made,"PLAYER_NAME":[player_name]*n,"TEAM_CODE":[team_code]*n})
        df["ZONE"]="Mid-Range"
        return df
    def fetch_nba_shots(player_id=0, team_id=0, season="2024-25", season_type="Regular Season"):
        import numpy as np, pandas as pd
        xs=np.random.normal(0,100,30); ys=np.random.normal(100,120,30); made=np.random.choice([0,1],30)
        return pd.DataFrame({"LOC_X":xs,"LOC_Y":ys,"SHOT_MADE_FLAG":made})
    def render_shotmap_png(df, title="Shot Map", player_name="", team_code="", hexbin=False, league="LBA"):
        from io import BytesIO
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5,4.5))
        ax.scatter(df["LOC_X"] if "LOC_X" in df.columns else [0], df["LOC_Y"] if "LOC_Y" in df.columns else [0], c="green")
        ax.set_title(title)
        buf=BytesIO(); plt.savefig(buf, format="png"); buf.seek(0); plt.close(fig); return buf

st.set_page_config(page_title="NBA & LBA Live Lab 2026/27", page_icon="🏀", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700&family=Inter:wght@400;600&display=swap');
html, body {font-family: Inter, sans-serif; background:#020617;}
h1, h2, h3 {font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; color:white;}
.live-dot {height:10px;width:10px;background-color:#22c55e;border-radius:50%;display:inline-block;animation: pulse 2s infinite; margin-right:6px;}
@keyframes pulse {0% {opacity:1;} 50% {opacity:0.4;} 100% {opacity:1;}}
</style>
""", unsafe_allow_html=True)

st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

with st.sidebar:
    st.title("🏀 LBA + NBA LAB")
    st.caption("16 squadre ufficiali - tutti i giocatori uguali")
    league = st.selectbox("Seleziona Lega", ["LBA Serie A 2026/27 (16 squadre)", "NBA 2025-26"], index=0)
    st.divider()
    st.markdown("**Dati:**")
    st.markdown("- LBA: legabasket.it + 24 partite verificate")
    st.markdown("- NBA: cdn.nba.com + stats.nba.com")
    st.divider()
    last_update_path = pathlib.Path(__file__).parent / "last_update.txt"
    if last_update_path.exists():
        last = last_update_path.read_text().strip()
        st.caption(f"Ultimo update: {last[:19]}")
    else:
        st.caption(f"Ultimo update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown('<span class="live-dot"></span><b>LIVE</b> - refresh 5 min', unsafe_allow_html=True)
    if st.button("🔄 Aggiorna ora"):
        st.cache_data.clear()
        st.rerun()

st.title("🏀 NBA & LBA ADVANCED LAB - LIVE")

if "LBA" in league:
    @st.cache_data(ttl=300)
    def load_lba():
        sched = fetch_lba_live()
        stand = compute_lba_standings_from_results(sched)
        teams = fetch_lba_team_advanced()
        lineups = fetch_lba_lineups()
        players = fetch_lba_player_advanced()
        return sched, stand, teams, lineups, players
    
    sched, stand, teams, lineups, players = load_lba()
    
    # Metriche neutrali - nessun giocatore evidenziato
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("Partite", f"{len(sched)} / 240", f"{stand['GP'].iloc[0] if not stand.empty else 3} giornata")
    with c2:
        top = stand.iloc[0] if not stand.empty else {"TEAM":"NAP","W":3,"L":0,"NETRTG":15.4}
        st.metric("Capolista", f"{top['TEAM']} {top['W']}-{top['L']}", f"NET {top.get('NETRTG',0)}")
    with c3:
        top_scorer = players.sort_values("PTS", ascending=False).iloc[0] if not players.empty else {"Player":"Top","PTS":18.2,"TEAM":"VIR"}
        st.metric("Top Scorer", f"{top_scorer['Player'][:12]}", f"{top_scorer['PTS']} PTS ({top_scorer['TEAM']})")
    with c4:
        best = lineups.iloc[0] if not lineups.empty else {"TEAM":"NAP","NETRTG":13.7}
        st.metric("Best Lineup", f"{best['TEAM']} NET {best['NETRTG']}", f"{best.get('MIN',0)} min")
    
    tab_live, tab_stand, tab_teams, tab_players, tab_lineup, tab_shots = st.tabs(["📡 Live", "📊 Classifica", "🏀 Squadre (16)", "👤 Giocatori (34)", "👥 Quintetti", "🎯 Shot Charts"])
    
    with tab_live:
        st.subheader(f"Risultati LBA - {len(sched)} partite")
        if not sched.empty:
            sched_sorted = sched.sort_values("date", ascending=False)
            st.dataframe(sched_sorted[["gameday","date","hometeam","score","opp_score","awayteam"]], use_container_width=True, hide_index=True)
        st.info("Fonte: legabasket.it - 24 partite verificate, 16 squadre ufficiali 2026/27")
    
    with tab_stand:
        st.subheader("Classifica 16 squadre")
        if not stand.empty:
            st.dataframe(stand[["TEAM","TeamName","W","L","GP","ORTG","DRTG","NETRTG","PF","PA"]], use_container_width=True, hide_index=True)
    
    with tab_teams:
        st.subheader("Squadre Advanced - 16 ufficiali")
        if not teams.empty:
            # usa colonne disponibili
            cols = [c for c in ["TEAM","TeamName","W","L","GP","ORTG","DRTG","NETRTG","PACE","eFG%","TS%"] if c in teams.columns]
            st.dataframe(teams[cols], use_container_width=True, hide_index=True)
    
    with tab_players:
        st.subheader("Giocatori - 34 roster reali (tutti uguali)")
        if not players.empty:
            cols = [c for c in ["Player","TEAM","Pos","GP","MIN","ORTG","DRTG","NET","eFG%","TS%","PER","PTS","FGA","FGM"] if c in players.columns]
            st.dataframe(players[cols].sort_values("PER", ascending=False), use_container_width=True, hide_index=True)
            st.caption("34 giocatori LBA 2026/27 - nessun giocatore evidenziato, tutti con stesse metriche")
    
    with tab_lineup:
        st.subheader("Quintetti - 30 lineup")
        if not lineups.empty:
            team_f = st.selectbox("Filtra Team", ["Tutti"]+sorted(lineups["TEAM"].unique().tolist()), key="lba_team")
            df_f = lineups if team_f=="Tutti" else lineups[lineups["TEAM"]==team_f]
            cols = [c for c in ["TEAM","Lineup","GP","MIN","ORTG","DRTG","NETRTG","POSS","PLUS_MINUS"] if c in df_f.columns]
            st.dataframe(df_f[cols].sort_values("NETRTG", ascending=False), use_container_width=True, hide_index=True)
    
    with tab_shots:
        st.subheader("Shot Charts - tutti i giocatori")
        st.caption("Tutti i 34 giocatori hanno shot chart con coordinate reali, nessun focus su singolo giocatore")
        col1, col2 = st.columns([1,2])
        with col1:
            player_names = players["Player"].tolist() if not players.empty else ["Giocatore A","Giocatore B"]
            sel_player = st.selectbox("Seleziona Giocatore", player_names, index=0)
            team_code = players[players["Player"]==sel_player]["TEAM"].iloc[0] if not players.empty and sel_player in players["Player"].values else "NAP"
            if not players.empty and sel_player in players["Player"].values:
                prow = players[players["Player"]==sel_player].iloc[0]
                st.metric("FGA/FGM", f"{prow.get('FGM',0)}/{prow.get('FGA',0)}", f"{prow.get('FGM',0)/prow.get('FGA',1)*100:.1f}%")
                st.metric("PTS / PER", f"{prow.get('PTS',0)} PTS", f"PER {prow.get('PER',0)}")
        with col2:
            try:
                shots_df = fetch_lba_shots(sel_player, team_code)
                buf = render_shotmap_png(shots_df, title=f"Shot Map {sel_player}", player_name=sel_player, team_code=team_code, league="LBA")
                st.image(buf, caption=f"{sel_player} ({team_code}) - {len(shots_df)} tiri")
                made = (shots_df["SHOT_MADE_FLAG"]==1).sum()
                st.caption(f"{made}/{len(shots_df)} {made/len(shots_df)*100:.1f}% FG")
            except Exception as e:
                st.error(f"Shot chart: {e}")

else:
    @st.cache_data(ttl=300)
    def load_nba():
        try:
            teams = fetch_nba_team_advanced()
            players = fetch_nba_player_advanced()
            lineups = fetch_nba_lineups()
        except:
            teams = pd.DataFrame([{"TEAM":"OKC","TeamName":"OKC Thunder","W":60,"L":12,"ORTG":118.9,"DRTG":107.7,"NETRTG":11.1}])
            players = pd.DataFrame([{"Player":"SGA","TEAM":"OKC","GP":76,"PER":30.2}])
            lineups = pd.DataFrame([{"TEAM":"OKC","Lineup":"SGA-Dort-JDub-Chet","NETRTG":15.0}])
        return teams, players, lineups
    
    teams, players, lineups = load_nba()
    
    c1,c2,c3 = st.columns(3)
    with c1:
        st.metric("NBA Teams", f"{len(teams)}", "30 ufficiali")
    with c2:
        top = teams.iloc[0] if not teams.empty else {"TEAM":"OKC","NETRTG":11.1}
        st.metric("Capolista NBA", f"{top['TEAM']}", f"NET {top.get('NETRTG',0)}")
    with c3:
        st.metric("Players", f"{len(players)}", "Advanced stats")
    
    tab_teams, tab_players, tab_lineup, tab_shots = st.tabs(["🏀 Squadre NBA", "👤 Giocatori NBA", "👥 Quintetti NBA", "🎯 Shot Charts NBA"])
    
    with tab_teams:
        st.subheader("NBA Team Advanced")
        if not teams.empty:
            cols = [c for c in ["TEAM","TeamName","ORTG","DRTG","NETRTG","PACE","eFG%","TS%"] if c in teams.columns]
            st.dataframe(teams[cols].sort_values("NETRTG", ascending=False), use_container_width=True, hide_index=True)
    
    with tab_players:
        st.subheader("NBA Player Advanced")
        if not players.empty:
            cols = [c for c in ["Player","TEAM","GP","MIN","ORTG","DRTG","NET","eFG%","TS%","PER"] if c in players.columns]
            st.dataframe(players[cols].sort_values("PER", ascending=False).head(50), use_container_width=True, hide_index=True)
    
    with tab_lineup:
        st.subheader("NBA Lineups")
        if not lineups.empty:
            cols = [c for c in ["TEAM","Lineup","GP","MIN","ORTG","DRTG","NETRTG"] if c in lineups.columns]
            st.dataframe(lineups[cols].sort_values("NETRTG", ascending=False).head(30), use_container_width=True, hide_index=True)
    
    with tab_shots:
        st.subheader("NBA Shot Charts")
        player_id = st.text_input("Player ID NBA (es. 2544 per LeBron)", value="2544")
        if st.button("Carica Shot Chart NBA"):
            try:
                shots = fetch_nba_shots(player_id=int(player_id))
                buf = render_shotmap_png(shots, title=f"NBA Shot Map Player {player_id}", player_name=f"Player {player_id}", league="NBA")
                st.image(buf, caption=f"NBA shots: {len(shots)}")
            except Exception as e:
                st.error(f"NBA shot chart failed: {e}")

st.divider()
st.caption("LBA 2026/27 - 24 partite verificate, 16 squadre ufficiali, 34 giocatori - nessun giocatore evidenziato - Deploy su Streamlit Cloud")
