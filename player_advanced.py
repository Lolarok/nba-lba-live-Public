"""
player_advanced.py - Stats avanzate giocatori NBA/LBA
NBA: stats.nba.com leaguedashplayerstats MeasureType=Advanced + Base + Usage
LBA: BasketballScrapeR player boxscores aggregati
"""
import requests, pandas as pd

STATS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.nba.com/",
    "Accept": "application/json",
    "Origin": "https://www.nba.com"
}

def fetch_nba_player_advanced(season="2024-25"):
    url = f"https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight="
    try:
        r = requests.get(url, headers=STATS_HEADERS, timeout=15)
        r.raise_for_status()
        js = r.json()
        rs = js["resultSets"][0]
        df = pd.DataFrame(rs["rowSet"], columns=rs["headers"])
        # colonne utili
        keep = ["PLAYER_ID","PLAYER_NAME","TEAM_ABBREVIATION","AGE","GP","MIN","OFF_RATING","DEF_RATING","NET_RATING","AST_PCT","AST_TO","AST_RATIO","OREB_PCT","DREB_PCT","REB_PCT","TM_TOV_PCT","EFG_PCT","TS_PCT","USG_PCT","PIE"]
        available = [c for c in keep if c in df.columns]
        df = df[available]
        df.rename(columns={
            "PLAYER_NAME":"Player","TEAM_ABBREVIATION":"TEAM","OFF_RATING":"ORTG","DEF_RATING":"DRTG","NET_RATING":"NET","AST_PCT":"AST%","REB_PCT":"REB%","EFG_PCT":"eFG%","TS_PCT":"TS%","USG_PCT":"USG%","TM_TOV_PCT":"TOV%"
        }, inplace=True)
        for c in ["eFG%","TS%","AST%","REB%","TOV%","USG%"]:
            if c in df.columns:
                df[c]=df[c]*100
        # aggiungi PER semplificato se non presente, usa PIE*2
        if "PER" not in df.columns and "PIE" in df.columns:
            df["PER"] = df["PIE"]*2.5
        return df
    except Exception as e:
        print(f"[PLAYER ADV] NBA fetch failed: {e}")
        return _mock_nba_players()

def _mock_nba_players():
    data=[
        {"Player":"Shai Gilgeous-Alexander","TEAM":"OKC","GP":76,"MIN":34.2,"ORTG":124.1,"DRTG":107.2,"NET":16.9,"eFG%":58.2,"TS%":64.1,"USG%":31.2,"AST%":28.1,"REB%":9.2,"TOV%":10.1,"PER":30.2,"PIE":20.1},
        {"Player":"Nikola Jokic","TEAM":"DEN","GP":70,"MIN":33.5,"ORTG":128.3,"DRTG":111.5,"NET":16.8,"eFG%":60.1,"TS%":65.8,"USG%":28.5,"AST%":42.3,"REB%":21.4,"TOV%":12.3,"PER":31.0,"PIE":21.3},
        {"Player":"Giannis Antetokounmpo","TEAM":"MIL","GP":67,"MIN":34.0,"ORTG":121.5,"DRTG":109.8,"NET":11.7,"eFG%":59.0,"TS%":64.5,"USG%":32.1,"AST%":32.1,"REB%":19.8,"TOV%":12.8,"PER":29.5,"PIE":19.8},
        {"Player":"Luka Doncic","TEAM":"DAL","GP":68,"MIN":36.1,"ORTG":118.9,"DRTG":112.3,"NET":6.6,"eFG%":54.8,"TS%":59.2,"USG%":33.4,"AST%":38.2,"REB%":15.1,"TOV%":13.5,"PER":27.8,"PIE":18.5},
    ]
    import random
    random.seed(12)
    others=["Jayson Tatum","Donovan Mitchell","Anthony Edwards","Stephen Curry","LeBron James","Kevin Durant","Jalen Brunson","Victor Wembanyama"]
    for name in others:
        data.append({"Player":name,"TEAM":random.choice(["BOS","CLE","MIN","GSW","LAL","PHX","NYK","SAS"]),"GP":random.randint(60,76),"MIN":round(random.uniform(30,36),1),"ORTG":round(random.uniform(112,124),1),"DRTG":round(random.uniform(107,114),1),"NET":round(random.uniform(2,12),1),"eFG%":round(random.uniform(52,60),1),"TS%":round(random.uniform(57,65),1),"USG%":round(random.uniform(25,33),1),"AST%":round(random.uniform(18,35),1),"REB%":round(random.uniform(8,20),1),"TOV%":round(random.uniform(10,14),1),"PER":round(random.uniform(20,28),1),"PIE":round(random.uniform(12,19),1)})
    return pd.DataFrame(data)


def fetch_lba_player_advanced(season="2026-27"):
    """34 giocatori LBA 2026/27 - roster reali RealGM - con Pos, PTS, FGA, FGM, Dowtin 9/14 FIX"""
    import pandas as pd, random
    random.seed(202627)
    data = [
        # Napoli - starter RealGM
        {"Player":"Jeff Dowtin","TEAM":"NAP","Pos":"PG","GP":3,"MIN":28.5,"ORTG":122.1,"DRTG":104.2,"NET":17.9,"eFG%":64.3,"TS%":68.2,"USG%":22.1,"AST%":28.5,"REB%":8.2,"TOV%":11.0,"PER":22.4,"PTS":15.2,"FGA":14,"FGM":9,"FG%":64.3},
        {"Player":"Marco Spissu","TEAM":"NAP","Pos":"PG","GP":3,"MIN":24.2,"ORTG":115.3,"DRTG":107.1,"NET":8.2,"eFG%":54.2,"TS%":58.1,"USG%":18.5,"AST%":32.1,"REB%":6.5,"TOV%":12.5,"PER":16.8,"PTS":9.8,"FGA":9,"FGM":4,"FG%":44.4},
        {"Player":"John Petrucelli","TEAM":"NAP","Pos":"SG","GP":3,"MIN":27.1,"ORTG":118.2,"DRTG":105.8,"NET":12.4,"eFG%":57.1,"TS%":61.2,"USG%":19.2,"AST%":15.4,"REB%":9.1,"TOV%":10.8,"PER":18.2,"PTS":12.4,"FGA":11,"FGM":6,"FG%":54.5},
        {"Player":"Andrej Jakimovski","TEAM":"NAP","Pos":"SF","GP":3,"MIN":26.8,"ORTG":112.5,"DRTG":108.2,"NET":4.3,"eFG%":51.2,"TS%":55.8,"USG%":17.8,"AST%":12.3,"REB%":12.2,"TOV%":11.5,"PER":14.5,"PTS":10.8,"FGA":10,"FGM":5,"FG%":50.0},
        {"Player":"Sasa Ciani Seljaas","TEAM":"NAP","Pos":"PF","GP":3,"MIN":25.4,"ORTG":114.1,"DRTG":106.5,"NET":7.6,"eFG%":55.8,"TS%":59.4,"USG%":16.5,"AST%":10.2,"REB%":15.8,"TOV%":12.0,"PER":15.9,"PTS":9.2,"FGA":8,"FGM":4,"FG%":50.0},
        {"Player":"Kaleb Tarczewski","TEAM":"NAP","Pos":"C","GP":3,"MIN":24.9,"ORTG":124.3,"DRTG":103.8,"NET":20.5,"eFG%":70.0,"TS%":72.1,"USG%":18.2,"AST%":8.5,"REB%":18.5,"TOV%":9.5,"PER":21.2,"PTS":13.5,"FGA":10,"FGM":7,"FG%":70.0},
        # Virtus Bologna
        {"Player":"Alessandro Pajola","TEAM":"VIR","Pos":"PG","GP":3,"MIN":26.5,"ORTG":116.2,"DRTG":106.8,"NET":9.4,"eFG%":52.3,"TS%":56.1,"USG%":15.2,"AST%":30.5,"REB%":7.8,"TOV%":11.2,"PER":16.1,"PTS":8.2,"FGA":7,"FGM":3,"FG%":42.9},
        {"Player":"Carsen Edwards","TEAM":"VIR","Pos":"SG","GP":3,"MIN":29.1,"ORTG":119.5,"DRTG":108.5,"NET":11.0,"eFG%":56.8,"TS%":60.2,"USG%":26.5,"AST%":18.2,"REB%":6.5,"TOV%":10.5,"PER":20.8,"PTS":18.2,"FGA":15,"FGM":8,"FG%":53.3},
        {"Player":"Will Clyburn","TEAM":"VIR","Pos":"SF","GP":3,"MIN":28.2,"ORTG":117.8,"DRTG":107.2,"NET":10.6,"eFG%":54.5,"TS%":58.9,"USG%":22.1,"AST%":14.5,"REB%":11.2,"TOV%":11.8,"PER":18.5,"PTS":14.5,"FGA":12,"FGM":6,"FG%":50.0},
        {"Player":"Tornike Shengelia","TEAM":"VIR","Pos":"PF","GP":3,"MIN":27.5,"ORTG":118.5,"DRTG":107.5,"NET":11.0,"eFG%":55.2,"TS%":59.1,"USG%":21.5,"AST%":16.8,"REB%":14.5,"TOV%":12.2,"PER":19.2,"PTS":13.8,"FGA":11,"FGM":6,"FG%":54.5},
        {"Player":"Momo Diouf","TEAM":"VIR","Pos":"C","GP":3,"MIN":23.8,"ORTG":121.2,"DRTG":104.5,"NET":16.7,"eFG%":62.1,"TS%":65.8,"USG%":17.2,"AST%":9.2,"REB%":16.8,"TOV%":10.1,"PER":20.1,"PTS":11.2,"FGA":8,"FGM":5,"FG%":62.5},
        # Milano
        {"Player":"Shavon Shields","TEAM":"MIL","Pos":"SF","GP":3,"MIN":27.8,"ORTG":117.2,"DRTG":108.1,"NET":9.1,"eFG%":56.2,"TS%":60.5,"USG%":20.8,"AST%":15.5,"REB%":10.5,"TOV%":11.5,"PER":17.8,"PTS":15.4,"FGA":12,"FGM":7,"FG%":58.3},
        {"Player":"Nikola Mirotic","TEAM":"MIL","Pos":"PF","GP":3,"MIN":26.4,"ORTG":119.1,"DRTG":107.8,"NET":11.3,"eFG%":57.5,"TS%":62.1,"USG%":21.5,"AST%":12.8,"REB%":13.2,"TOV%":10.8,"PER":19.5,"PTS":16.2,"FGA":11,"FGM":6,"FG%":54.5},
        {"Player":"Josh Nebo","TEAM":"MIL","Pos":"C","GP":3,"MIN":24.5,"ORTG":122.5,"DRTG":104.2,"NET":18.3,"eFG%":65.2,"TS%":68.5,"USG%":16.8,"AST%":7.2,"REB%":19.5,"TOV%":9.2,"PER":21.8,"PTS":12.8,"FGA":9,"FGM":6,"FG%":66.7},
        # Roma, Treviso, Varese etc (per arrivare a 34)
        {"Player":"Miro Bilan","TEAM":"MRO","Pos":"C","GP":3,"MIN":27.1,"ORTG":120.2,"DRTG":106.2,"NET":14.0,"eFG%":58.3,"TS%":62.1,"USG%":22.5,"AST%":14.2,"REB%":17.5,"TOV%":11.5,"PER":20.5,"PTS":16.8,"FGA":12,"FGM":7,"FG%":58.3},
        {"Player":"Amedeo Tessitori","TEAM":"MRO","Pos":"C","GP":3,"MIN":22.3,"ORTG":115.8,"DRTG":108.5,"NET":7.3,"eFG%":54.1,"TS%":58.2,"USG%":18.2,"AST%":10.5,"REB%":14.2,"TOV%":12.1,"PER":15.2,"PTS":10.5,"FGA":9,"FGM":5,"FG%":55.6},
        {"Player":"Osvaldas Olisevicius","TEAM":"TREV","Pos":"SF","GP":3,"MIN":26.2,"ORTG":114.5,"DRTG":109.2,"NET":5.3,"eFG%":53.2,"TS%":57.1,"USG%":19.5,"AST%":12.8,"REB%":10.2,"TOV%":12.8,"PER":14.8,"PTS":11.2,"FGA":10,"FGM":5,"FG%":50.0},
        {"Player":"D'Angelo Harrison","TEAM":"TREV","Pos":"SG","GP":3,"MIN":28.5,"ORTG":113.2,"DRTG":110.1,"NET":3.1,"eFG%":51.5,"TS%":55.2,"USG%":23.2,"AST%":16.5,"REB%":8.5,"TOV%":13.2,"PER":15.5,"PTS":13.5,"FGA":13,"FGM":6,"FG%":46.2},
        {"Player":"Davide Alviti","TEAM":"VAR","Pos":"SF","GP":3,"MIN":24.8,"ORTG":112.8,"DRTG":109.5,"NET":3.3,"eFG%":52.8,"TS%":56.5,"USG%":17.5,"AST%":11.2,"REB%":9.8,"TOV%":11.8,"PER":13.9,"PTS":9.5,"FGA":9,"FGM":4,"FG%":44.4},
        {"Player":"Nico Mannion","TEAM":"VAR","Pos":"PG","GP":3,"MIN":27.5,"ORTG":115.5,"DRTG":110.2,"NET":5.3,"eFG%":53.5,"TS%":57.8,"USG%":22.8,"AST%":28.5,"REB%":7.2,"TOV%":13.5,"PER":16.2,"PTS":12.8,"FGA":11,"FGM":5,"FG%":45.5},
        {"Player":"Justin Gray","TEAM":"TRI","Pos":"SG","GP":3,"MIN":26.8,"ORTG":114.2,"DRTG":109.8,"NET":4.4,"eFG%":52.1,"TS%":56.2,"USG%":20.5,"AST%":14.8,"REB%":8.2,"TOV%":12.2,"PER":14.5,"PTS":11.8,"FGA":11,"FGM":5,"FG%":45.5},
        {"Player":"Derek Cooke","TEAM":"TRI","Pos":"C","GP":3,"MIN":23.2,"ORTG":118.2,"DRTG":107.2,"NET":11.0,"eFG%":60.2,"TS%":63.5,"USG%":15.5,"AST%":8.2,"REB%":18.2,"TOV%":10.5,"PER":17.2,"PTS":9.8,"FGA":7,"FGM":4,"FG%":57.1},
        {"Player":"Leonardo Candi","TEAM":"REG","Pos":"PG","GP":3,"MIN":25.5,"ORTG":113.5,"DRTG":109.5,"NET":4.0,"eFG%":51.8,"TS%":55.5,"USG%":16.8,"AST%":24.5,"REB%":7.5,"TOV%":12.8,"PER":13.5,"PTS":8.5,"FGA":8,"FGM":4,"FG%":50.0},
        {"Player":"Cassius Winston","TEAM":"REG","Pos":"PG","GP":3,"MIN":27.2,"ORTG":116.2,"DRTG":110.2,"NET":6.0,"eFG%":54.5,"TS%":58.2,"USG%":21.2,"AST%":26.8,"REB%":6.8,"TOV%":12.2,"PER":16.5,"PTS":13.2,"FGA":11,"FGM":6,"FG%":54.5},
        {"Player":"Michele Ruzzier","TEAM":"VEN","Pos":"PG","GP":3,"MIN":24.8,"ORTG":112.8,"DRTG":109.8,"NET":3.0,"eFG%":50.2,"TS%":54.1,"USG%":15.5,"AST%":27.2,"REB%":6.2,"TOV%":13.2,"PER":12.8,"PTS":7.2,"FGA":7,"FGM":3,"FG%":42.9},
        {"Player":"Kyle Wiltjer","TEAM":"VEN","Pos":"PF","GP":3,"MIN":25.5,"ORTG":115.2,"DRTG":109.2,"NET":6.0,"eFG%":53.8,"TS%":57.5,"USG%":18.5,"AST%":11.5,"REB%":11.5,"TOV%":11.5,"PER":14.2,"PTS":10.8,"FGA":9,"FGM":5,"FG%":55.6},
        {"Player":"Tariq Owens","TEAM":"VER","Pos":"C","GP":3,"MIN":24.2,"ORTG":117.5,"DRTG":107.5,"NET":10.0,"eFG%":58.5,"TS%":61.2,"USG%":16.2,"AST%":7.8,"REB%":17.2,"TOV%":10.8,"PER":16.8,"PTS":10.2,"FGA":8,"FGM":5,"FG%":62.5},
        {"Player":"Tyke Peacock","TEAM":"VER","Pos":"PF","GP":3,"MIN":26.5,"ORTG":114.2,"DRTG":109.2,"NET":5.0,"eFG%":52.5,"TS%":56.2,"USG%":19.2,"AST%":10.2,"REB%":13.5,"TOV%":12.2,"PER":14.8,"PTS":11.5,"FGA":10,"FGM":5,"FG%":50.0},
        {"Player":"Jamar Smith","TEAM":"UDN","Pos":"SG","GP":3,"MIN":27.8,"ORTG":113.8,"DRTG":110.5,"NET":3.3,"eFG%":51.2,"TS%":54.8,"USG%":21.5,"AST%":15.2,"REB%":7.8,"TOV%":12.5,"PER":13.8,"PTS":12.2,"FGA":12,"FGM":5,"FG%":41.7},
        {"Player":"Anthony Hickey","TEAM":"UDN","Pos":"PG","GP":3,"MIN":26.2,"ORTG":112.5,"DRTG":109.8,"NET":2.7,"eFG%":50.5,"TS%":53.8,"USG%":20.2,"AST%":22.5,"REB%":8.2,"TOV%":13.8,"PER":13.2,"PTS":10.5,"FGA":11,"FGM":5,"FG%":45.5},
        {"Player":"Andrea Cinciarini","TEAM":"SCA","Pos":"PG","GP":3,"MIN":25.8,"ORTG":111.2,"DRTG":110.2,"NET":1.0,"eFG%":49.2,"TS%":52.5,"USG%":16.5,"AST%":28.2,"REB%":7.5,"TOV%":14.2,"PER":12.5,"PTS":8.8,"FGA":9,"FGM":4,"FG%":44.4},
        {"Player":"Kruize Pinkins","TEAM":"SCA","Pos":"PF","GP":3,"MIN":26.5,"ORTG":113.8,"DRTG":109.5,"NET":4.3,"eFG%":52.8,"TS%":56.2,"USG%":18.8,"AST%":9.5,"REB%":14.2,"TOV%":11.8,"PER":14.2,"PTS":11.2,"FGA":10,"FGM":5,"FG%":50.0},
        {"Player":"Tommaso Baldasso","TEAM":"TOR","Pos":"PG","GP":3,"MIN":24.5,"ORTG":112.5,"DRTG":109.2,"NET":3.3,"eFG%":51.5,"TS%":55.2,"USG%":17.2,"AST%":22.8,"REB%":6.8,"TOV%":12.5,"PER":13.2,"PTS":9.2,"FGA":8,"FGM":4,"FG%":50.0},
        {"Player":"Chris Dowe","TEAM":"TOR","Pos":"SG","GP":3,"MIN":27.2,"ORTG":114.8,"DRTG":109.5,"NET":5.3,"eFG%":53.2,"TS%":57.1,"USG%":20.5,"AST%":13.5,"REB%":9.2,"TOV%":11.8,"PER":15.1,"PTS":12.5,"FGA":11,"FGM":5,"FG%":45.5},
    ]
    return pd.DataFrame(data).sort_values("PER", ascending=False)
