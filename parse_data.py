import os
import pandas as pd
from bs4 import BeautifulSoup

SCORE_DIR = "data/scores"
box_scores = os.listdir(SCORE_DIR)
box_scores = [os.path.join(SCORE_DIR, f) for f in box_scores if f.endswith(".html")]


def parse_html(box_score):
    with open(box_score) as f:
        html = f.read()

    soup = BeautifulSoup(html)
    [s.decompose() for s in soup.select("tr.over_header")]
    [s.decompose() for s in soup.select("tr.thread")]
    return soup


def read_line_score(soup):
    line_score = pd.read_html(str(soup), attrs={"id": "line_score"})[0]
    # fixing column names
    cols = list(line_score.columns)
    cols[0] = 'tema'
    cols[-1] = 'total'
    line_score.columns = cols

    # ignoring every other things in between
    line_score = line_score[["team", "total"]]
    return  line_score


def read_stats(soup, team, stat):
    df = pd.read_html(str(soup), attrs={"id": f"box-{team}-game-{stat}"}, index_col=0)[0]
    # converts col to numeric column. where there is no number NAN will be used
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def read_season_info(soup):
    nav = soup.select("#bottom_nav_container")[0]
    hrefs = [a["href"] for a in nav.find_all("a")]
    season = os.path.basename(hrefs[1]).split("_")[0]
    return season


base_cols = None
games = []

for box_score in box_scores:
    soup = parse_html(box_score)
    line_score = read_line_score(soup)
    teams = list(line_score["team"])

    summaries = []
    for team in teams:
        basic = read_stats(soup, team, "basic")
        advanced = read_stats(soup, team, "advanced")

        # get the last row of both basic and advaced and smash them into a single series. the last row of each is total
        # iloc index a dataframe by position
        totals = pd.concat([basic.iloc[-1,:], advanced.iloc[-1:]])
        #takes all the column name and turn them into lower case
        totals.index = totals.index.str.lower()

        # creating maximum value for each player. looking at rows for players and selecting player with highest value points
        # [:-1] => all the rows except the last one
        maxes = pd.concat([basic.iloc[:-1].max(), advanced.iloc[:-1].max()])

        # we need to change index for maxes. the colums are name the same as in total. we want them to be
        # different so pandas treats them as a differn columen
        maxes.index = maxes.index.str.lower() + "_max"  # lowers it and add _max

        # putting them togetehr (total and maxes)
        summary = pd.concat([totals, maxes])

        # making sure we get the same stat for every game as the stat may be different for every box score
        if base_cols is None:
            base_cols = list(summaries.index.drop_duplicates(keep="first"))
            # removing 'bpm'
            base_cols = [b for b in base_cols if "bpm" not in b]

        summary = summary[base_cols]

        summaries.append(summary)

    # concantinating summaries into a single summary
    # .T tuns the rows into column
    summary = pd.concat(summaries, axis=1).T

    # combining summary and line score
    game = pd.concat([summary, line_score], axis=1)

    # assigning a column to indicate which team is at home
    game["home"] = [0, 1]

    # it's good to have stat about opponents. so we can conatenate opponents team with the team playing
    # reversing the dataframe so that the first row becomes the second one.
    # reset the index so we can concat.
    game_opp = game.iloc[::-1].reset_index()

    # reamin our columns
    game_opp.columns += "_opp"  # add _opp to all the column name

    full_game = pd.concat([game, game_opp], axis=1)

    # adding information about the game
    full_game["season"] = read_season_info(soup)
    full_game["date"] = os.path.basename(box_score)[:8]
    full_game['date'] = pd.to_datetime(full_game["date"], format="%Y%m%d")
    full_game['won'] = full_game["total"] > full_game["total_opp"]

    games.append(full_game)

    # progress
    if len(games) % 100 == 0:
        print(f"{len(games)} / {len(box_scores)}")


# once the above is done running
games_df = pd.concat(games, ignore_index=True)



