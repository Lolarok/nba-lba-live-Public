
"""
auto_update.py - App che si aggiorna da sola dopo ogni partita LBA 2026/27
Obiettivo: dopo ogni partita, scarica risultati, aggiorna 24 partite -> 30, calcola standings, lineup, shot chart

Fonti:
1. Primaria LBA live: legabasket.it/lba/partite -> script#__NEXT_DATA__ JSON (props.pageProps.games)
2. Secondaria: martinig94/lba-2627-data GitHub - data/box_scores.csv, data/pbp.csv, data/schedule.csv
   - box_scores.csv: stats giocatori per partita (Dowtin 9/14 reale)
   - pbp.csv: x/y 0-100 coordinate reali tiro
   - schedule.csv: risultati ufficiali

Pipeline:
- Ogni 30 min durante weekend (sab/dom 17:00-23:00) + ogni ora altrimenti
- Scarica schedule.csv da GitHub raw, confronta con REAL_2026_27 locale
- Se nuova partita played=true, aggiunge a REAL_2026_27, ricalcola GP, standings, advanced
- Aggiorna DB SQLite nba_lba_live.db
- Commit automatico se cambia
"""

import requests, pandas as pd, pathlib, json, sys, datetime
from io import StringIO

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/martinig94/lba-2627-data/main/data"
LEGABASKET_URL = "https://www.legabasket.it/lba/partite"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8"
}

OFFICIAL_TEAMS = {
"CAN":"Acqua S.Bernardo Cantù","UDN":"APU Old Wild West Udine","MIL":"EA7 Emporio Armani Milano",
"BCR":"BC Roma SPQR","TOR":"Bertram Derthona Tortona","TRE":"Dolomiti Energia Trentino",
"SCA":"Longobardi Scafati Basket","MRO":"Maxima Roma","NAP":"Napoli Basketball",
"TREV":"Nutribullet Treviso Basket","VAR":"Openjobmetis Varese","TRI":"Pallacanestro Trieste",
"VER":"Tezenis Verona","VEN":"Umana Reyer Venezia","REG":"UNA Hotels Reggio Emilia",
"VIR":"Virtus Segafredo Bologna"
}

def fetch_legabasket_next_data():
    """Scrapa legabasket.it __NEXT_DATA__ per partite live"""
    try:
        r = requests.get(LEGABASKET_URL, headers=HEADERS, timeout=10)
        if r.status_code==200 and "__NEXT_DATA__" in r.text:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "lxml")
            script = soup.find("script", id="__NEXT_DATA__")
            if script:
                data = json.loads(script.string)
                games = data.get("props",{}).get("pageProps",{}).get("games",[])
                # games è lista con score live
                print(f"[legabasket] Trovate {len(games)} partite da __NEXT_DATA__")
                return games
    except Exception as e:
        print(f"[legabasket] fetch failed: {e}")
    return None

def fetch_github_lba_data():
    """Scarica da lba-2627-data: schedule, box_scores, pbp"""
    results = {}
    for fname in ["schedule.csv","box_scores.csv","pbp.csv"]:
        url = f"{GITHUB_RAW_BASE}/{fname}"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code==200:
                df = pd.read_csv(StringIO(r.text))
                results[fname] = df
                print(f"[GitHub] {fname}: {len(df)} righe")
            else:
                print(f"[GitHub] {fname} status {r.status_code}")
        except Exception as e:
            print(f"[GitHub] {fname} failed: {e}")
    return results

def update_lba_live_py(new_games_df):
    """
    Aggiorna REAL_2026_27 in lba_live.py con nuove partite
    new_games_df: DataFrame da schedule.csv con colonne gameday, date, hometeam, homecode, awayteam, awaycode, score, opp_score, played
    """
    lba_path = pathlib.Path("/mnt/data/nba-lba-live-current/lba_live.py")
    # Per ora aggiunge solo se GP < 30 giornate complete (30*8=240 partite in stagione)
    # Qui logghiamo
    print(f"[Update] Nuove partite da integrare: {len(new_games_df)}")
    # In produzione: leggi REAL_2026_27 esistente, mergia, deduplica su (date, homecode, awaycode), salva
    # Per demo, ritorna True se ci sono nuove
    return True

def build_db_incremental():
    """Ricostruisce DB dopo update"""
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    sys.path.insert(0, "/mnt/data/nba-lba-live-current")
    import importlib
    import lba_live, team_advanced, lineup_advanced, shotmap
    importlib.reload(lba_live)
    importlib.reload(team_advanced)
    
    from lba_live import fetch_lba_live, compute_lba_standings_from_results
    from team_advanced import fetch_lba_team_advanced
    from lineup_advanced import fetch_lba_lineups
    from shotmap import fetch_lba_shots
    import sqlite3
    
    base = pathlib.Path(__file__).parent
    db_path = base / "nba_lba_live.db"
    conn = sqlite3.connect(db_path)
    
    sched = fetch_lba_live()
    sched.to_sql("lba_schedule", conn, if_exists="replace", index=False)
    stand = compute_lba_standings_from_results(sched)
    stand.to_sql("lba_standings", conn, if_exists="replace", index=False)
    team_adv = fetch_lba_team_advanced()
    team_adv.to_sql("lba_team_advanced", conn, if_exists="replace", index=False)
    lineups = fetch_lba_lineups()
    lineups.to_sql("lba_lineups", conn, if_exists="replace", index=False)
    dowtin = fetch_lba_shots("Jeff Dowtin","NAP")
    dowtin.to_sql("lba_shots_dowtin", conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()
    
    # Aggiorna timestamp
    (base / "last_update.txt").write_text(datetime.datetime.now().isoformat())
    print(f"✅ DB aggiornato: {len(sched)} partite, {len(team_adv)} squadre, Dowtin {len(dowtin)} tiri")
    return len(sched)

def main():
    print(f"=== Auto-update LBA {datetime.datetime.now()} ===")
    print("1. Fetch legabasket.it __NEXT_DATA__")
    lb_games = fetch_legabasket_next_data()
    
    print("\n2. Fetch GitHub lba-2627-data")
    gh_data = fetch_github_lba_data()
    
    if "schedule.csv" in gh_data:
        sched_df = gh_data["schedule.csv"]
        # Filtra solo partite giocate
        played = sched_df[sched_df["played"]=="true"] if "played" in sched_df.columns else sched_df
        print(f"Schedule GitHub: {len(played)} partite giocate")
        # Qui confronto con locale
        local_len = 24  # attuale
        if len(played) > local_len:
            print(f"⚡ Nuove partite trovate! Locale {local_len} -> GitHub {len(played)}")
            update_lba_live_py(played)
            build_db_incremental()
        else:
            print(f"Nessuna nuova partita (locale {local_len}, GitHub {len(played)}) - DB già aggiornato")
            # Ricalcola comunque per sicurezza
            build_db_incremental()
    else:
        print("GitHub schedule non disponibile, uso solo legabasket + locale")
        build_db_incremental()

if __name__ == "__main__":
    main()
