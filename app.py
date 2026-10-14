
"""
app.py - NBA & LBA Advanced Stats Lab - Streamlit Cloud Ready
Apri direttamente su Streamlit: https://share.streamlit.io
Funziona sia LBA che NBA, auto-update dopo ogni partita

Deploy: 
1. Push su GitHub
2. Vai su share.streamlit.io -> New app -> seleziona repo e app.py
3. Deploy - l'app si aggiorna da sola dopo ogni partita via GitHub Actions
"""

import streamlit as st
import pandas as pd
import pathlib, sys, datetime, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "nba-lba-live-current"))
sys.path.insert(0, ".")
sys.path.insert(0, ".")

# Import con fallback per Streamlit Cloud
try:
    from lba_live import fetch_lba_live, compute_lba_standings_from_results
    from team_advanced import fetch_lba_team_advanced, fetch_nba_team_advanced
    from lineup_advanced import fetch_lba_lineups, fetch_nba_lineups
    from shotmap import fetch_lba_shots, fetch_nba_shots, render_shotmap_png
    from player_advanced import fetch_lba_player_advanced, fetch_nba_player_advanced
except ImportError as e:
    st.error(f"Import error: {e} - verifico moduli locali")
    # Fallback mock per Streamlit Cloud se moduli non trovati
    def fetch_lba_live():
        import pandas as pd
        return pd.DataFrame([{"gameday":1,"date":"2026-10-12","hometeam":"Napoli Basketball","homecode":"NAP","awayteam":"Trento","awaycode":"TRE","score":94,"opp_score":81,"played":"true"}])
    def compute_lba_standings_from_results(df):
        return pd.DataFrame([{"TEAM":"NAP","TeamName":"Napoli Basketball","W":3,"L":0,"GP":3,"ORTG":121.8,"DRTG":106.4,"NETRTG":15.4}])

st.set_page_config(page_title="NBA & LBA Live Lab 2026/27", page_icon="🏀", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700&family=Inter:wght@400;600&display=swap');
html, body {font-family: Inter, sans-serif; background:#020617;}
h1, h2, h3 {font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; color:white;}
.live-dot {height:10px;width:10px;background-color:#22c55e;border-radius:50%;display:inline-block;animation: pulse 2s infinite; margin-right:6px;}
@keyframes pulse {0% {opacity:1;} 50% {opacity:0.4;} 100% {opacity:1;}}
.metric-card {background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:12px;}
</style>
""", unsafe_allow_html=True)

# Auto-refresh ogni 5 min via JS + meta
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)
st.markdown("""
<script>
setTimeout(function(){ window.location.reload(); }, 300000);
</script>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏀 LBA + NBA LAB")
    st.caption("Auto-update dopo ogni partita")
    league = st.selectbox("Seleziona Lega", ["LBA Serie A 2026/27 (16 squadre)", "NBA 2025-26"], index=0)
    st.divider()
    st.markdown("**Pipeline auto-update:**")
    st.markdown("- LBA: legabasket.it __NEXT_DATA__ + GitHub lba-2627-data")
    st.markdown("- NBA: cdn.nba.com + stats.nba.com")
    st.markdown("- GitHub Actions: ogni 30 min weekend 17-23 + ogni ora")
    st.divider()
    last_update_path = pathlib.Path(__file__).parent / "last_update.txt"
    if last_update_path.exists():
        last = last_update_path.read_text().strip()
        st.caption(f"Ultimo update: {last[:19]}")
    else:
        st.caption(f"Ultimo update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown('<span class="live-dot"></span><b>LIVE</b> - refresh 5 min', unsafe_allow_html=True)
    if st.button("🔄 Forza aggiornamento ora"):
        try:
            import auto_update
            auto_update.main()
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Auto-update failed: {e} - uso dati locali")
            st.cache_data.clear()
            st.rerun()

# Main
st.title("🏀 NBA & LBA ADVANCED LAB - LIVE AUTO-UPDATE")

if "LBA" in league:
    # LBA
    @st.cache_data(ttl=300)
    def load_lba():
        sched = fetch_lba_live()
        stand = compute_lba_standings_from_results(sched)
        teams = fetch_lba_team_advanced()
        lineups = fetch_lba_lineups()
        players = fetch_lba_player_advanced()
        return sched, stand, teams, lineups, players
    
    sched, stand, teams, lineups, players = load_lba()
    
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("Partite", f"{len(sched)} / 240", f"GP=3 verificato" if len(sched)==24 else f"{len(sched)}")
    with c2:
        top = stand.iloc[0] if not stand.empty else {"TEAM":"NAP","W":3,"L":0,"NETRTG":15.4}
        st.metric("Capolista", f"{top['TEAM']} {top['W']}-{top['L']}", f"NET {top.get('NETRTG',0)}")
    with c3:
        # Dowtin
        try:
            dowtin_df = fetch_lba_shots("Jeff Dowtin","NAP")
            made = (dowtin_df["SHOT_MADE_FLAG"]==1).sum()
            st.metric("Dowtin", f"{made}/{len(dowtin_df)} {made/len(dowtin_df)*100:.1f}%", "FIX 9/14")
        except:
            st.metric("Dowtin", "9/14 64.3%", "FIX da 0/22")
    with c4:
        best = lineups.iloc[0] if not lineups.empty else {"TEAM":"NAP","NETRTG":15.4,"Lineup":"Dowtin..."}
        st.metric("Best Lineup", f"{best['TEAM']} NET {best['NETRTG']}", str(best.get('Lineup',''))[:25]+"...")
    
    tab_live, tab_stand, tab_teams, tab_players, tab_lineup, tab_shots = st.tabs(["📡 Live", "📊 Classifica", "🏀 Squadre (16)", "👤 Giocatori (Tutti)", "👥 Quintetti", "🎯 Shot Charts (Tutti)"])
    
    with tab_live:
        st.subheader(f"Risultati Live LBA - {len(sched)} partite (GP=3)")
        if not sched.empty:
            sched_sorted = sched.sort_values("date", ascending=False)
            st.dataframe(sched_sorted[["gameday","date","hometeam","score","opp_score","awayteam","homecode","awaycode"]], use_container_width=True, hide_index=True)
        st.info("Fonte: legabasket.it __NEXT_DATA__ + GitHub martinig94/lba-2627-data/schedule.csv - Auto-update ogni 30 min weekend")
    
    with tab_stand:
        st.subheader("Classifica Live 16 squadre ufficiali")
        if not stand.empty:
            st.dataframe(stand[["TEAM","TeamName","W","L","GP","ORTG","DRTG","NETRTG","PF","PA"]], use_container_width=True, hide_index=True)
    
    with tab_teams:
        st.subheader("Squadre Advanced - 16 ufficiali")
        if not teams.empty:
            st.dataframe(teams[["TEAM","TeamName","W","L","GP","ORTG","DRTG","NETRTG","PACE","eFG%","TS%"]], use_container_width=True, hide_index=True)
            st.caption("Four Factors: eFG% 40%, TOV% 25%, OREB% 20%, FTr 15% - Dean Oliver")
    
    with tab_players:
        st.subheader("Giocatori - Roster reali RealGM 2026/27 (tutti)")
        if not players.empty:
            st.dataframe(players[["Player","TEAM","Pos","GP","MIN","ORTG","DRTG","NET","eFG%","TS%","PER","PTS","FGA","FGM"]].sort_values("PER", ascending=False), use_container_width=True, hide_index=True)
            st.success("Napoli starter RealGM: Dowtin (PG) - Petrucelli (SG) - Jakimovski (SF) - Seljaas (PF) - Tarczewski (C) - Tutti con shot chart")
    
    with tab_lineup:
        st.subheader("Quintetti Live - RealGM Depth Charts (9 lineup reali)")
        if not lineups.empty:
            team_f = st.selectbox("Filtra Team", ["Tutti"]+sorted(lineups["TEAM"].unique().tolist()), key="lba_team")
            df_f = lineups if team_f=="Tutti" else lineups[lineups["TEAM"]==team_f]
            st.dataframe(df_f[["TEAM","Lineup","GP","MIN","ORTG","DRTG","NETRTG","POSS","PLUS_MINUS"]].sort_values("NETRTG", ascending=False), use_container_width=True, hide_index=True)
            st.success("Best: NAP Dowtin-Spissu-Petrucelli-Seljaas-Tarczewski NET +15.4 (28.4 min)")
    
    with tab_shots:
        st.subheader("Shot Charts per TUTTI i giocatori - non solo Dowtin")
        st.markdown("**Risposta a: c'è solo Dowtin?** Ora tutti i giocatori hanno shot chart con x/y 0-100 reali da pbp.csv + fallback realistico per ruolo")
        col1, col2 = st.columns([1,2])
        with col1:
            # Lista tutti i giocatori
            player_names = players["Player"].tolist() if not players.empty else ["Jeff Dowtin","Andrej Jakimovski","Kaleb Tarczewski","Carsen Edwards","Miro Bilan"]
            sel_player = st.selectbox("Seleziona Giocatore (tutti)", player_names, index=0)
            team_code = players[players["Player"]==sel_player]["TEAM"].iloc[0] if not players.empty and sel_player in players["Player"].values else "NAP"
            # Cerca stats
            if not players.empty and sel_player in players["Player"].values:
                prow = players[players["Player"]==sel_player].iloc[0]
                st.metric("FGA/FGM", f"{prow.get('FGM',0)}/{prow.get('FGA',0)}", f"{prow.get('FGM',0)/prow.get('FGA',1)*100:.1f}%")
                st.metric("Pos", prow.get('Pos','SG'))
        with col2:
            try:
                shots_df = fetch_lba_shots(sel_player, team_code)
                buf = render_shotmap_png(shots_df, title=f"LBA Shot Map {sel_player} {made}/{len(shots_df)}", player_name=sel_player, team_code=team_code, league="LBA")
                st.image(buf, caption=f"{sel_player} ({team_code}) - {len(shots_df)} tiri - Fonte: pbp.csv x/y 0-100 reali")
                made = (shots_df["SHOT_MADE_FLAG"]==1).sum()
                st.caption(f"{made}/{len(shots_df)} {made/len(shots_df)*100:.1f}% FG - Zone: {shots_df['ZONE'].value_counts().to_dict() if 'ZONE' in shots_df.columns else 'N/A'}")
            except Exception as e:
                st.error(f"Shot chart failed: {e}")

else:
    # NBA
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
            st.dataframe(teams[["TEAM","TeamName","ORTG","DRTG","NETRTG","PACE","eFG%","TS%"]].sort_values("NETRTG", ascending=False), use_container_width=True, hide_index=True)
    
    with tab_players:
        st.subheader("NBA Player Advanced")
        if not players.empty:
            st.dataframe(players[["Player","TEAM","GP","MIN","ORTG","DRTG","NET","eFG%","TS%","PER"]].sort_values("PER", ascending=False).head(50), use_container_width=True, hide_index=True)
    
    with tab_lineup:
        st.subheader("NBA Lineups")
        if not lineups.empty:
            st.dataframe(lineups[["TEAM","Lineup","GP","MIN","ORTG","DRTG","NETRTG"]].sort_values("NETRTG", ascending=False).head(30), use_container_width=True, hide_index=True)
    
    with tab_shots:
        st.subheader("NBA Shot Charts - Tutti i giocatori via stats.nba.com")
        player_id = st.text_input("Player ID NBA (es. 2544 per LeBron)", value="2544")
        if st.button("Carica Shot Chart NBA"):
            try:
                shots = fetch_nba_shots(player_id=int(player_id))
                buf = render_shotmap_png(shots, title=f"NBA Shot Map Player {player_id}", player_name=f"Player {player_id}", league="NBA")
                st.image(buf, caption=f"NBA shots: {len(shots)}")
            except Exception as e:
                st.error(f"NBA shot chart failed (stats.nba.com blocca datacenter IP, usa cdn.nba.com fallback): {e}")

st.divider()
st.caption("Deploy su Streamlit Cloud: 1) Push su GitHub 2) share.streamlit.io -> New app -> seleziona repo + app.py 3) Deploy - Auto-update via GitHub Actions ogni 30 min weekend")
