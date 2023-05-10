import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from tqdm import tqdm

from arena_utls import raise_html_status_code


def get_arenafan_schedule(season: int, arena_league_level=1):
    """

    """
    if arena_league_level == 1 or arena_league_level == 2:
        pass
    else:
        raise ValueError(
            f"\"arena_league_level\" can only be \"1\" or \"2\".\nYou entered:\n\t{arena_league_level}")

    if season == 2009 and arena_league_level == 1:
        raise ValueError(
            "The Arena Football League did not games in this season due to a bankruptcy.")
    elif season < 2000 and arena_league_level == 2:
        raise ValueError(
            "af2 as an entity did not exist prior to 1999, and started play in 2000.")
    elif season > 2009 and arena_league_level == 2:
        raise ValueError(
            "Following the 2009 af2 season, the af2 league was morphed into the revived Arena Football League. ")

    sched_df = pd.DataFrame()

    url = f"https://www.arenafan.com/history/?page=yearly&histleague=1&fpage=schedule&year={season}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    response = requests.get(url, headers=headers)
    raise_html_status_code(response.status_code)
    soup = BeautifulSoup(response.text, features='lxml')
    time.sleep(1)

    sched_table = soup.find_all('table')[0]
    sched_table = sched_table.find_all('table')[1]

    table_rows = sched_table.find_all('tr')
    current_week = ""
    week_num = 0
    current_day = ""
    game_type = ""

    for i in range(5, len(table_rows)):
        row = table_rows[i]

        is_week = False
        is_date = False

        temp_wk = row.find('th')

        if temp_wk != None:
            current_week = temp_wk.text

            if 'Preseason ' in current_week:
                game_type = "PRE"
                week_num = int(current_week.split(' ')[-1])

            elif 'Playoffs ' in current_week:
                game_type = "POST"
                week_num = int(current_week.split(' ')[-1])

            elif 'ArenaBowl ' in current_week:
                game_type = "POST"
                week_num = week_num + 1

            elif 'All Star ' in current_week:
                game_type = "ASG"
                week_num = 1

            else:
                game_type = "REG"
                week_num = int(current_week.split(' ')[-1])

            is_week = True

        del temp_wk

        temp_day = row.find(
            'td', {'colspan': '9', 'class': 'stats_left_head', 'align': 'center'})

        if temp_day != None:
            current_day = temp_day.text
            current_day = f"{current_day}, {season}"
            current_date = datetime.strptime(current_day, "%A, %B %d, %Y")

            is_date = True

        del temp_day

        sched_row = row.find_all('td')

        if is_week == False and is_date == False and len(sched_row) > 2:
            row_df = pd.DataFrame(
                {'season': season, 'current_week': current_week, 'date': current_date, 'game_type': game_type, 'week_num': week_num}, index=[0])

            away_team_id = sched_row[0].find('a').get('href')
            away_team_id = int(away_team_id.replace(
                '/teams/?page=history&team=', '').replace(f'&year={season}', ''))
            row_df['away_team_id'] = away_team_id
            del away_team_id

            row_df['away_team_name'] = sched_row[0].find('a').text

            home_team_id = sched_row[3].find('a').get('href')
            home_team_id = int(home_team_id.replace(
                '/teams/?page=history&team=', '').replace(f'&year={season}', ''))
            row_df['home_team_id'] = home_team_id
            del home_team_id

            row_df['home_team_name'] = sched_row[3].find('a').text

            row_df['away_team_score'] = int(sched_row[1].text)
            home_team_score = str(sched_row[4].text).replace(
                '\xa0', '').split('(')
            row_df['home_team_score'] = int(home_team_score[0])

            # OT indicator is in the home team's score, if the game went beyond 4 quarters.
            if len(home_team_score) > 1:

                if 'OT' in home_team_score[1]:
                    row_df['is_overtime_game'] = True
            else:
                row_df['is_overtime_game'] = False

            try:
                row_df['attendance'] = int(
                    str(sched_row[5].text).replace('\xa0', ''))
            except:
                row_df['attendance'] = None

            try:
                game_id = sched_row[5].find('a').get('href')
                game_id = int(game_id.replace(
                    '/statistics/?page=boxscore&gameid=', ''))
                row_df['game_id'] = game_id
                del game_id
            except:
                row_df['game_id'] = None

            sched_df = pd.concat([sched_df, row_df], ignore_index=True)

    return sched_df


if __name__ == "__main__":
    for i in tqdm(range(2009, 2020)):
        if i == 2009:
            pass
        else:
            df = get_arenafan_schedule(i)
            df.to_csv(
                f'arena_football_league/schedule/csv/{i}_arena_schedule.csv', index=False)
            df.to_parquet(
                f'arena_football_league/schedule/parquet/{i}_arena_schedule.parquet', index=False)
