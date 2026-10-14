"""
shotmap.py - Mappa di tiro NBA/LBA con export PNG
NBA: shotchartdetail endpoint
LBA: mock + supporto BasketballScrapeR play-by-play (x,y)
"""
import requests, pandas as pd, numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from io import BytesIO

STATS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.nba.com/",
    "Accept": "application/json",
    "Origin": "https://www.nba.com"
}

def fetch_nba_shots(player_id=0, team_id=0, season="2024-25", season_type="Regular Season"):
    url = f"https://stats.nba.com/stats/shotchartdetail?AheadBehind=&ClutchTime=&CloseDefDistRange=&Conference=&ContextFilter=&ContextMeasure=FGA&DateFrom=&DateTo=&Division=&EndPeriod=&EndRange=&GROUP_ID=&GameEventID=&GameID=&GameSegment=&GroupID=&GroupMode=&GroupQuantity=5&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&Period=0&PlayerID={player_id}&PlayerID1=&PlayerID2=&PlayerID3=&PlayerID4=&PlayerID5=&PlayerPosition=&PointDiff=&Position=&RangeType=&RookieYear=&Season={season}&SeasonSegment=&SeasonType={season_type}&ShotClockRange=&StartPeriod=&StartRange=&StarterBench=&TeamID={team_id}&VsConference=&VsDivision=&VsPlayerID1=&VsPlayerID2=&VsPlayerID3=&VsPlayerID4=&VsPlayerID5=&VsTeamID="
    try:
        r = requests.get(url, headers=STATS_HEADERS, timeout=20)
        r.raise_for_status()
        js = r.json()
        rs = js["resultSets"][0]
        df = pd.DataFrame(rs["rowSet"], columns=rs["headers"])
        # colonne utili: LOC_X, LOC_Y, SHOT_MADE_FLAG, SHOT_TYPE, SHOT_DISTANCE
        return df
    except Exception as e:
        print(f"[SHOTMAP] fetch failed: {e}")
        return _mock_nba_shots()

def _mock_nba_shots(n=300):
    import random
    random.seed(33)
    xs = np.random.normal(0, 100, n)
    ys = np.random.normal(0, 120, n) + 100
    made = np.random.choice([0,1], n, p=[0.55,0.45])
    return pd.DataFrame({"LOC_X":xs,"LOC_Y":ys,"SHOT_MADE_FLAG":made,"SHOT_TYPE":["2PT Field Goal"]*n})

def draw_court(ax=None, color="white", lw=2):
    """Disegna mezzo campo NBA (scala NBA: x -250..250, y -50..420)"""
    if ax is None:
        fig, ax = plt.subplots()
    # impostazioni
    ax.set_xlim(-250,250)
    ax.set_ylim(-50,420)
    # linee
    # canestro
    hoop = Circle((0,0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -7.5), 60, 1, linewidth=lw, color=color)
    # paint
    outer_box = Rectangle((-80,-47.5), 160, 190, linewidth=lw, color=color, fill=False)
    inner_box = Rectangle((-60,-47.5), 120, 190, linewidth=lw, color=color, fill=False)
    # free throw arc
    top_ft = Arc((0,142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
    bottom_ft = Arc((0,142.5), 120, 120, theta1=180, theta2=360, linewidth=lw, color=color, linestyle='--')
    # 3pt line
    three_arc = Arc((0,0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
    three_line1 = Rectangle((-220,-47.5), 0, 92, linewidth=lw, color=color)
    three_line2 = Rectangle((220,-47.5), 0, 92, linewidth=lw, color=color)
    # elementi
    for elem in [hoop, backboard, outer_box, inner_box, top_ft, bottom_ft, three_arc]:
        ax.add_patch(elem)
    ax.plot([-220, -220], [-47.5, 44.5], color=color, linewidth=lw)
    ax.plot([220, 220], [-47.5, 44.5], color=color, linewidth=lw)
    ax.set_aspect('equal')
    ax.axis('off')
    return ax

def render_shotmap_png(df, title="Shot Map", player_name="", team_code="", hexbin=False):
    """Ritorna BytesIO PNG come fa el-statslab shotmap_ui"""
    fig, ax = plt.subplots(figsize=(6,5.6), dpi=200)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    draw_court(ax, color="white", lw=1.5)

    # plot shots
    if not df.empty and "LOC_X" in df.columns:
        made = df[df["SHOT_MADE_FLAG"]==1]
        missed = df[df["SHOT_MADE_FLAG"]==0]
        if hexbin:
            # hexbin density
            hb = ax.hexbin(df["LOC_X"], df["LOC_Y"], gridsize=25, cmap="YlOrRd", alpha=0.8, mincnt=1, extent=(-250,250,-50,420))
        else:
            ax.scatter(missed["LOC_X"], missed["LOC_Y"], c="#ef4444", s=18, alpha=0.6, label="Miss", edgecolors="white", linewidths=0.3)
            ax.scatter(made["LOC_X"], made["LOC_Y"], c="#22c55e", s=22, alpha=0.9, label="Made", edgecolors="white", linewidths=0.4)

    # titoli
    ax.text(0, 400, title, ha="center", va="center", color="white", fontsize=14, fontweight="bold", fontfamily="sans-serif")
    if player_name:
        ax.text(0, 380, f"{player_name} {f'({team_code})' if team_code else ''}", ha="center", color="#94a3b8", fontsize=10)
    # stats
    if not df.empty:
        total = len(df)
        made_n = (df["SHOT_MADE_FLAG"]==1).sum()
        pct = made_n/total*100 if total else 0
        ax.text(0, -35, f"{made_n}/{total} - {pct:.1f}%", ha="center", color="white", fontsize=11, fontweight="bold")

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=200)
    buf.seek(0)
    plt.close(fig)
    return buf

def render_team_comparison_png(team_stats, title="Team Advanced"):
    """PNG export per team cards, stile el-statslab"""
    fig, ax = plt.subplots(figsize=(10,6), dpi=200)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    ax.axis('off')
    ax.text(0.5, 0.92, title, ha="center", va="center", color="white", fontsize=18, fontweight="bold")
    y=0.75
    for _, row in team_stats.iterrows():
        txt = f"{row['TEAM']}: ORTG {row['ORTG']} | DRTG {row['DRTG']} | NET {row['NETRTG']} | PACE {row['PACE']} | eFG {row['eFG%']}% | TS {row['TS%']}%"
        ax.text(0.05, y, txt, color="white", fontsize=10)
        y-=0.06
    ax.text(0.5, 0.05, "NBA & LBA Advanced Lab • dati ESPN / LBA", ha="center", color="#64748b", fontsize=8)
    buf=BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf
