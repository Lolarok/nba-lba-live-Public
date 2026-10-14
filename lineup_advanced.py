"""
lineup_advanced.py - Statistiche lineup (5-man units)
NBA: leaguedashlineups endpoint
LBA: mock basato su BasketballScrapeR play-by-play
"""
import requests, pandas as pd

STATS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.nba.com/",
    "Accept": "application/json",
    "Origin": "https://www.nba.com"
}

def fetch_nba_lineups(season="2024-25", group_quantity=5, min_minutes=50):
    url = f"https://stats.nba.com/stats/leaguedashlineups?Conference=&DateFrom=&DateTo=&Division=&GameSegment=&GroupQuantity={group_quantity}&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&TeamID=0&VsConference=&VsDivision="
    try:
        r = requests.get(url, headers=STATS_HEADERS, timeout=15)
        r.raise_for_status()
        js = r.json()
        rs = js["resultSets"][0]
        df = pd.DataFrame(rs["rowSet"], columns=rs["headers"])
        # Filtra per MIN
        if "MIN" in df.columns:
            df = df[df["MIN"]>=min_minutes]
        # Rinomina
        df.rename(columns={
            "TEAM_ABBREVIATION":"TEAM","GROUP_NAME":"Lineup","OFF_RATING":"ORTG","DEF_RATING":"DRTG","NET_RATING":"NETRTG","PACE":"PACE","EFG_PCT":"eFG%","TS_PCT":"TS%","REB_PCT":"REB%","AST_PCT":"AST%","TM_TOV_PCT":"TOV%"
        }, inplace=True)
        for c in ["eFG%","TS%","REB%","AST%","TOV%"]:
            if c in df.columns:
                df[c]=df[c]*100
        return df.sort_values("NETRTG", ascending=False).head(200)
    except Exception as e:
        print(f"[LINEUP] NBA fetch failed: {e}")
        return _mock_nba_lineups()

def _mock_nba_lineups():
    import random
    random.seed(20)
    data=[]
    teams=["OKC","BOS","CLE","NYK","DEN"]
    for _ in range(60):
        team=random.choice(teams)
        lineup=f"{team} 5-man #{random.randint(1,12)}: Player A - Player B - Player C - Player D - Player E"
        data.append({
            "TEAM":team,"Lineup":lineup,"GP":random.randint(10,35),"MIN":round(random.uniform(50,220),1),
            "ORTG":round(random.uniform(108,126),1),"DRTG":round(random.uniform(102,116),1),"NETRTG":round(random.uniform(-5,18),1),
            "PACE":round(random.uniform(96,103),1),"eFG%":round(random.uniform(51,59),1),"TS%":round(random.uniform(55,63),1),
            "REB%":round(random.uniform(48,54),1),"AST%":round(random.uniform(55,70),1),"TOV%":round(random.uniform(10,15),1),
            "PLUS_MINUS":round(random.uniform(-20,60),1)
        })
    return pd.DataFrame(data)

def fetch_lba_lineups(season="2024-25", min_minutes=30):
    import random
    random.seed(21)
    data=[]
    teams=["VIR","MIL","BRE","TRA","TRE","VEN"]
    for _ in range(50):
        team=random.choice(teams)
        data.append({
            "TEAM":team,"Lineup":f"{team} lineup {random.randint(1,20)}","GP":random.randint(8,25),"MIN":round(random.uniform(30,150),1),
            "ORTG":round(random.uniform(105,120),1),"DRTG":round(random.uniform(103,115),1),"NETRTG":round(random.uniform(-6,14),1),
            "PACE":round(random.uniform(75,80),1),"eFG%":round(random.uniform(49,58),1),"TS%":round(random.uniform(53,61),1),
            "REB%":round(random.uniform(47,53),1),"AST%":round(random.uniform(54,68),1),"TOV%":round(random.uniform(11,16),1),
            "PLUS_MINUS":round(random.uniform(-15,40),1)
        })
    return pd.DataFrame(data).sort_values("NETRTG", ascending=False)
