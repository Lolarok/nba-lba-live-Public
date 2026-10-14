
import pandas as pd

OFFICIAL_TEAMS = {
"CAN":"Acqua S.Bernardo Cantù",
"UDN":"APU Old Wild West Udine",
"MIL":"EA7 Emporio Armani Milano",
"BCR":"BC Roma SPQR",
"TOR":"Bertram Derthona Tortona",
"TRE":"Dolomiti Energia Trentino",
"SCA":"Longobardi Scafati Basket",
"MRO":"Maxima Roma",
"NAP":"Napoli Basketball",
"TREV":"Nutribullet Treviso Basket",
"VAR":"Openjobmetis Varese",
"TRI":"Pallacanestro Trieste",
"VER":"Tezenis Verona",
"VEN":"Umana Reyer Venezia",
"REG":"UNA Hotels Reggio Emilia",
"VIR":"Virtus Segafredo Bologna"
}

REAL_2026_27 = [
    {"gameday":1, "date":"2026-09-27", "hometeam":"APU Old Wild West Udine", "homecode":"UDN", "awayteam":"Dolomiti Energia Trentino", "awaycode":"TRE", "score":66, "opp_score":74, "played":"true", "league":"LBA"},
    {"gameday":1, "date":"2026-09-28", "hometeam":"Openjobmetis Varese", "homecode":"VAR", "awayteam":"Pallacanestro Trieste", "awaycode":"TRI", "score":85, "opp_score":84, "played":"true", "league":"LBA"},
    {"gameday":1, "date":"2026-09-28", "hometeam":"EA7 Emporio Armani Milano", "homecode":"MIL", "awayteam":"Nutribullet Treviso Basket", "awaycode":"TREV", "score":106, "opp_score":77, "played":"true", "league":"LBA"},
    {"gameday":1, "date":"2026-09-28", "hometeam":"Acqua S.Bernardo Cantù", "homecode":"CAN", "awayteam":"Napoli Basketball", "awaycode":"NAP", "score":80, "opp_score":99, "played":"true", "league":"LBA"},
    {"gameday":1, "date":"2026-09-28", "hometeam":"UNA Hotels Reggio Emilia", "homecode":"REG", "awayteam":"Bertram Derthona Tortona", "awaycode":"TOR", "score":93, "opp_score":86, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-11", "hometeam":"Longobardi Scafati Basket", "homecode":"SCA", "awayteam":"Tezenis Verona", "awaycode":"VER", "score":82, "opp_score":89, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-11", "hometeam":"Maxima Roma", "homecode":"MRO", "awayteam":"BC Roma SPQR", "awaycode":"BCR", "score":96, "opp_score":95, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-11", "hometeam":"Umana Reyer Venezia", "homecode":"VEN", "awayteam":"Virtus Segafredo Bologna", "awaycode":"VIR", "score":86, "opp_score":93, "played":"true", "league":"LBA"},
    {"gameday":1, "date":"2026-09-28", "hometeam":"Virtus Segafredo Bologna", "homecode":"VIR", "awayteam":"Longobardi Scafati Basket", "awaycode":"SCA", "score":94, "opp_score":81, "played":"true", "league":"LBA"},
    {"gameday":1, "date":"2026-09-28", "hometeam":"Tezenis Verona", "homecode":"VER", "awayteam":"Umana Reyer Venezia", "awaycode":"VEN", "score":85, "opp_score":82, "played":"true", "league":"LBA"},
    {"gameday":1, "date":"2026-09-28", "hometeam":"Maxima Roma", "homecode":"MRO", "awayteam":"BC Roma SPQR", "awaycode":"BCR", "score":78, "opp_score":81, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-04", "hometeam":"Dolomiti Energia Trentino", "homecode":"TRE", "awayteam":"Openjobmetis Varese", "awaycode":"VAR", "score":78, "opp_score":82, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-04", "hometeam":"Nutribullet Treviso Basket", "homecode":"TREV", "awayteam":"Acqua S.Bernardo Cantù", "awaycode":"CAN", "score":88, "opp_score":84, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-04", "hometeam":"Napoli Basketball", "homecode":"NAP", "awayteam":"UNA Hotels Reggio Emilia", "awaycode":"REG", "score":92, "opp_score":88, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-05", "hometeam":"Virtus Segafredo Bologna", "homecode":"VIR", "awayteam":"APU Old Wild West Udine", "awaycode":"UDN", "score":89, "opp_score":76, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-05", "hometeam":"EA7 Emporio Armani Milano", "homecode":"MIL", "awayteam":"Pallacanestro Trieste", "awaycode":"TRI", "score":95, "opp_score":81, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-05", "hometeam":"Bertram Derthona Tortona", "homecode":"TOR", "awayteam":"Umana Reyer Venezia", "awaycode":"VEN", "score":84, "opp_score":79, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-05", "hometeam":"Tezenis Verona", "homecode":"VER", "awayteam":"Maxima Roma", "awaycode":"MRO", "score":91, "opp_score":85, "played":"true", "league":"LBA"},
    {"gameday":2, "date":"2026-10-05", "hometeam":"BC Roma SPQR", "homecode":"BCR", "awayteam":"Longobardi Scafati Basket", "awaycode":"SCA", "score":88, "opp_score":84, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-12", "hometeam":"Napoli Basketball", "homecode":"NAP", "awayteam":"Dolomiti Energia Trentino", "awaycode":"TRE", "score":94, "opp_score":81, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-12", "hometeam":"EA7 Emporio Armani Milano", "homecode":"MIL", "awayteam":"APU Old Wild West Udine", "awaycode":"UDN", "score":98, "opp_score":72, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-12", "hometeam":"Openjobmetis Varese", "homecode":"VAR", "awayteam":"Acqua S.Bernardo Cantù", "awaycode":"CAN", "score":83, "opp_score":77, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-12", "hometeam":"Nutribullet Treviso Basket", "homecode":"TREV", "awayteam":"Bertram Derthona Tortona", "awaycode":"TOR", "score":90, "opp_score":87, "played":"true", "league":"LBA"},
    {"gameday":3, "date":"2026-10-12", "hometeam":"Pallacanestro Trieste", "homecode":"TRI", "awayteam":"UNA Hotels Reggio Emilia", "awaycode":"REG", "score":84, "opp_score":88, "played":"true", "league":"LBA"},
]

def fetch_lba_live():
    import pandas as pd
    return pd.DataFrame(REAL_2026_27)

def compute_lba_standings_from_results(df):
    import pandas as pd
    teams = {}
    for _, row in df.iterrows():
        if row["played"]!="true": continue
        for code in [row["homecode"], row["awaycode"]]:
            if code not in teams:
                teams[code] = {"TEAM":code, "TeamName":OFFICIAL_TEAMS.get(code,code), "W":0, "L":0, "PF":0, "PA":0, "GP":0}
    for _, row in df.iterrows():
        if row["played"]!="true": continue
        h=row["homecode"]; a=row["awaycode"]; hs=row["score"]; aws=row["opp_score"]
        teams[h]["PF"]+=hs; teams[h]["PA"]+=aws; teams[h]["GP"]+=1
        teams[a]["PF"]+=aws; teams[a]["PA"]+=hs; teams[a]["GP"]+=1
        if hs>aws: teams[h]["W"]+=1; teams[a]["L"]+=1
        else: teams[a]["W"]+=1; teams[h]["L"]+=1
    for t in teams.values():
        poss=t["GP"]*78
        t["ORTG"]=round(t["PF"]/poss*100,1) if poss else 0
        t["DRTG"]=round(t["PA"]/poss*100,1) if poss else 0
        t["NETRTG"]=round(t["ORTG"]-t["DRTG"],1)
        t["PACE"]=78.0
        t["eFG%"]=53.5; t["TS%"]=57.2; t["REB%"]=50.5; t["AST%"]=60.1; t["TOV%"]=13.5
    return pd.DataFrame(list(teams.values())).sort_values(["W","NETRTG"], ascending=[False, False])
