import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from tqdm import tqdm

from arena_utls import raise_html_status_code, time_zone_whois
from get_arenafan_schedule import get_arenafan_schedule


def get_arena_game_stats(game_id: int):
    """

    """
    col_names = ['season', 'game_id', 'team_id', 'team_name', 'loc', 'opp_team_id',
                 'opp_team_name', 'team_score', 'opp_score', 'is_overtime_game',
                 'player_id', 'player_name', 'passing_comp', 'passing_att',
                 'passing_comp_pct', 'passing_yds', 'passing_td', 'passing_int',
                 'passing_ypa', 'passing_ypc', 'passing_nfl_qbr', 'passing_cfb_qbr',
                 'rushing_att', 'rushing_yds', 'rushing_avg', 'rushing_td',
                 'receiving_rec', 'receiving_yds', 'receiving_avg', 'receiving_td',
                 'defense_tackles_solo', 'defense_tackles_ast', 'defense_tackles_total',
                 'defnese_passes_defended', 'defense_sacks', 'defense_sack_yds',
                 'defense_forced_fumbles', 'defense_fumble_recoveries',
                 'defense_interceptions', 'defense_interception_yds',
                 'defense_interception_avg', 'defense_interception_tds', 'kicking_XPM',
                 'kicking_XPA', 'kicking_XP%', 'kicking_FGM', 'kicking_FGA',
                 'kicking_FG%', 'kicking_2pt_M', 'kicking_2pt_A', 'kicking_2pt%',
                 'kicking_4pt_M', 'kicking_4pt_A', 'kicking_4pt%', 'kick_return_ret',
                 'kick_return_yds', 'kick_return_avg', 'kick_return_td',
                 'missed_fg_return_ret', 'missed_fg_return_yds', 'missed_fg_return_avg',
                 'missed_fg_return_td']

    game_df = pd.DataFrame()

    passing_df = pd.DataFrame()
    rushing_df = pd.DataFrame()
    receiving_df = pd.DataFrame()
    tackling_df = pd.DataFrame()
    interceptions_df = pd.DataFrame()
    kicking_df = pd.DataFrame()
    returns_df = pd.DataFrame()

    season = 0
    game_date = ""
    is_overtime_game = False

    away_team_name = ""
    away_team_id = ""
    away_team_logo_url = ""
    away_team_score = 0

    home_team_name = ""
    home_team_id = ""
    home_team_logo_url = ""
    home_team_score = 0

    time_zones = time_zone_whois()
    print(f'\nGetting data for game #{game_id}.')

    url = f"http://www.arenafan.com/statistics/?page=boxscore&gameid={game_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    response = requests.get(url, headers=headers)
    raise_html_status_code(response.status_code)
    soup = BeautifulSoup(response.text, features='lxml')
    time.sleep(1)
    stat_tables = soup.find_all('div', {'class': 'twocolwrapper'})

    for i in range(0, len(stat_tables)):

        table_html = stat_tables[i]

        if i == 0:
            scores_table = table_html.find('div', {'class': 'coltwo'}).find(
                'table', {'id': 'stats_left'})
            # print(scores_table)
            table_rows = scores_table.find_all('tr')

            if len(table_rows) == 6:
                a_cells = table_rows[3].find_all('td')
                h_cells = table_rows[4].find_all('td')

                away_team_name = str(a_cells[0].text.replace(
                    '\n', '').replace('\xa0', ''))
                away_team_id = str(a_cells[0].find(
                    'a').get('href')).split('/')[2]
                away_team_logo_url = a_cells[0].find('a').get('href')
                away_team_score = int(a_cells[-1].text)

                home_team_name = str(h_cells[0].text.replace(
                    '\n', '').replace('\xa0', ''))

                home_team_id = str(h_cells[0].find(
                    'a').get('href')).split('/')[2]
                home_team_logo_url = h_cells[0].find('a').get('href')
                home_team_score = int(h_cells[-1].text)

                season = int(away_team_logo_url.split('/')[-2])
                game_info = str(table_rows[5].find(
                    'td')).replace('</b>', '').replace('\n', '').replace('<br>', '').replace('<br/>', '').split('<b>')
                game_date = game_info[1].replace('Date: ', '')
                game_date = game_date + \
                    str(game_info[2])
                game_date = game_date.split(', Game Time: ')[0]
                # game_date = parser.parse(game_date, tzinfos=time_zones)
                game_date = datetime.strptime(game_date, "%A %B %d, %Y")

                if len(h_cells) > 6:
                    is_overtime_game = True
                else:
                    is_overtime_game = False

                del scores_table, a_cells, h_cells

            elif len(table_rows) == 5:
                a_cells = table_rows[2].find_all('td')
                h_cells = table_rows[3].find_all('td')

                away_team_name = str(a_cells[0].text.replace(
                    '\n', '').replace('\xa0', ''))
                away_team_id = str(a_cells[0].find(
                    'a').get('href')).split('/')[2]
                away_team_logo_url = a_cells[0].find('a').get('href')
                away_team_score = int(a_cells[-1].text)

                home_team_name = str(h_cells[0].text.replace(
                    '\n', '').replace('\xa0', ''))

                home_team_id = str(h_cells[0].find(
                    'a').get('href')).split('/')[2]
                home_team_logo_url = h_cells[0].find('a').get('href')
                home_team_score = int(h_cells[-1].text)

                season = int(away_team_logo_url.split('/')[-2])
                game_info = str(table_rows[4].find(
                    'td')).replace('</b>', '').replace('\n', '').replace('<br>', '').replace('<br/>', '').split('<b>')
                game_date = game_info[1].replace('Date: ', '')
                game_date = game_date + \
                    str(game_info[2].replace('Game Time: ', ''))
                game_date = parser.parse(game_date)

                if len(h_cells) > 6:
                    is_overtime_game = True
                else:
                    is_overtime_game = False

                del scores_table, a_cells, h_cells
            elif len(table_rows) < 4:
                raise NotImplementedError('It ain\'t ready yet.')

            else:
                raise LookupError(
                    f'Unhandled box score lookup for game ID #{game_id}.')

        elif i == 1:  # Passing
            away_stats = table_html.find(
                'div', {'class': 'colone'}).find('table').find_all('tr')
            home_stats = table_html.find(
                'div', {'class': 'coltwo'}).find('table').find_all('tr')

            for j in range(2, len(away_stats)):
                # player_stats = j.find_all('td')
                p_stats = away_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = away_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': away_team_id, 'team_name': away_team_name,
                        'loc': 'A',
                        'opp_team_id': home_team_id, 'opp_team_name': home_team_name,
                        'team_score': away_team_score, 'opp_score': home_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])
                row_df['passing_comp'] = int(p_stats[1].text)
                row_df['passing_att'] = int(p_stats[2].text)
                row_df['passing_comp_pct'] = None
                row_df['passing_yds'] = int(p_stats[3].text)
                row_df['passing_td'] = int(p_stats[4].text)
                row_df['passing_int'] = int(p_stats[5].text)
                row_df['passing_ypa'] = None
                row_df['passing_ypc'] = None
                row_df['passing_nfl_qbr'] = None
                row_df['passing_cfb_qbr'] = None

                if len(row_df) > 0:

                    passing_df = pd.concat(
                        [passing_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            for j in range(2, len(home_stats)):
                p_stats = home_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = home_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': home_team_id, 'team_name': home_team_name,
                        'loc': 'H',
                        'opp_team_id': away_team_id, 'opp_team_name': away_team_name,
                        'team_score': home_team_score, 'opp_score': away_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])
                row_df['passing_comp'] = int(p_stats[1].text)
                row_df['passing_att'] = int(p_stats[2].text)
                row_df['passing_comp_pct'] = None
                row_df['passing_yds'] = int(p_stats[3].text)
                row_df['passing_td'] = int(p_stats[4].text)
                row_df['passing_int'] = int(p_stats[5].text)
                row_df['passing_ypa'] = None
                row_df['passing_ypc'] = None
                row_df['passing_nfl_qbr'] = None
                row_df['passing_cfb_qbr'] = None

                if len(row_df) > 0:

                    passing_df = pd.concat(
                        [passing_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

        elif i == 2:  # Receiving
            away_stats = table_html.find(
                'div', {'class': 'colone'}).find('table').find_all('tr')
            home_stats = table_html.find(
                'div', {'class': 'coltwo'}).find('table').find_all('tr')

            for j in range(2, len(away_stats)):
                # player_stats = j.find_all('td')

                p_stats = away_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = away_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': away_team_id, 'team_name': away_team_name,
                        'loc': 'A',
                        'opp_team_id': home_team_id, 'opp_team_name': home_team_name,
                        'team_score': away_team_score, 'opp_score': home_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                row_df['receiving_rec'] = int(p_stats[1].text)
                row_df['receiving_yds'] = int(p_stats[2].text)
                row_df['receiving_avg'] = None
                row_df['receiving_td'] = int(p_stats[3].text)

                if len(row_df) > 0:
                    receiving_df = pd.concat(
                        [receiving_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            for j in range(2, len(home_stats)):
                p_stats = home_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = home_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': home_team_id, 'team_name': home_team_name,
                        'loc': 'H',
                        'opp_team_id': away_team_id, 'opp_team_name': away_team_name,
                        'team_score': home_team_score, 'opp_score': away_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                row_df['receiving_rec'] = int(p_stats[1].text)
                row_df['receiving_yds'] = int(p_stats[2].text)
                row_df['receiving_avg'] = None
                row_df['receiving_td'] = int(p_stats[3].text)

                if len(row_df) > 0:

                    receiving_df = pd.concat(
                        [receiving_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            # print(receiving_df)

        elif i == 3:  # Rushing
            away_stats = table_html.find(
                'div', {'class': 'colone'}).find('table').find_all('tr')
            home_stats = table_html.find(
                'div', {'class': 'coltwo'}).find('table').find_all('tr')

            for j in range(2, len(away_stats)):
                # player_stats = j.find_all('td')
                p_stats = away_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = away_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': away_team_id, 'team_name': away_team_name,
                        'loc': 'A',
                        'opp_team_id': home_team_id, 'opp_team_name': home_team_name,
                        'team_score': away_team_score, 'opp_score': home_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                row_df['rushing_att'] = int(p_stats[1].text)
                row_df['rushing_yds'] = int(p_stats[2].text)
                row_df['rushing_avg'] = None
                row_df['rushing_td'] = int(p_stats[3].text)

                if len(row_df) > 0:
                    rushing_df = pd.concat(
                        [rushing_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            for j in range(2, len(home_stats)):
                p_stats = home_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = home_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': home_team_id, 'team_name': home_team_name,
                        'loc': 'H',
                        'opp_team_id': away_team_id, 'opp_team_name': away_team_name,
                        'team_score': home_team_score, 'opp_score': away_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                row_df['rushing_att'] = int(p_stats[1].text)
                row_df['rushing_yds'] = int(p_stats[2].text)
                row_df['rushing_avg'] = None
                row_df['rushing_td'] = int(p_stats[3].text)

                if len(row_df) > 0:
                    rushing_df = pd.concat(
                        [rushing_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            # print(rushing_df)

        elif i == 4:  # Kicking
            away_stats = table_html.find(
                'div', {'class': 'colone'}).find('table').find_all('tr')
            home_stats = table_html.find(
                'div', {'class': 'coltwo'}).find('table').find_all('tr')

            for j in range(2, len(away_stats)):
                # player_stats = j.find_all('td')
                p_stats = away_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = away_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': away_team_id, 'team_name': away_team_name,
                        'loc': 'A',
                        'opp_team_id': home_team_id, 'opp_team_name': home_team_name,
                        'team_score': away_team_score, 'opp_score': home_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                xps = p_stats[1].text
                fg_3 = p_stats[2].text
                fg_2 = p_stats[3].text
                fg_4 = p_stats[4].text

                row_df['kicking_XPM'] = int(xps.split('/')[0])
                row_df['kicking_XPA'] = int(xps.split('/')[1])
                row_df['kicking_XP%'] = 0
                row_df['kicking_FGM'] = int(fg_3.split('/')[0])
                row_df['kicking_FGA'] = int(fg_3.split('/')[1])
                row_df['kicking_FG%'] = 0
                row_df['kicking_2pt_M'] = int(fg_2.split('/')[0])
                row_df['kicking_2pt_A'] = int(fg_2.split('/')[1])
                row_df['kicking_2pt%'] = 0
                row_df['kicking_4pt_M'] = int(fg_4.split('/')[0])
                row_df['kicking_4pt_A'] = int(fg_4.split('/')[1])
                row_df['kicking_4pt%'] = 0

                if len(row_df) > 0:
                    kicking_df = pd.concat(
                        [kicking_df, row_df], ignore_index=True)

                del player_id, player_name, row_df, xps, fg_2, fg_3, fg_4

            for j in range(2, len(home_stats)):
                p_stats = home_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = home_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': home_team_id, 'team_name': home_team_name,
                        'loc': 'H',
                        'opp_team_id': away_team_id, 'opp_team_name': away_team_name,
                        'team_score': home_team_score, 'opp_score': away_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                xps = p_stats[1].text
                fg_3 = p_stats[2].text
                fg_2 = p_stats[3].text
                fg_4 = p_stats[4].text

                row_df['kicking_XPM'] = int(xps.split('/')[0])
                row_df['kicking_XPA'] = int(xps.split('/')[1])
                row_df['kicking_XP%'] = 0
                row_df['kicking_FGM'] = int(fg_3.split('/')[0])
                row_df['kicking_FGA'] = int(fg_3.split('/')[1])
                row_df['kicking_FG%'] = 0
                row_df['kicking_2pt_M'] = int(fg_2.split('/')[0])
                row_df['kicking_2pt_A'] = int(fg_2.split('/')[1])
                row_df['kicking_2pt%'] = 0
                row_df['kicking_4pt_M'] = int(fg_4.split('/')[0])
                row_df['kicking_4pt_A'] = int(fg_4.split('/')[1])
                row_df['kicking_4pt%'] = 0

                if len(row_df) > 0:
                    kicking_df = pd.concat(
                        [kicking_df, row_df], ignore_index=True)

                del player_id, player_name, row_df, xps, fg_2, fg_3, fg_4

            # print(kicking_df)

        elif i == 5:  # Returns
            away_stats = table_html.find(
                'div', {'class': 'colone'}).find('table').find_all('tr')
            home_stats = table_html.find(
                'div', {'class': 'coltwo'}).find('table').find_all('tr')

            for j in range(2, len(away_stats)):
                # player_stats = j.find_all('td')
                p_stats = away_stats[j].find_all('td')
                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = away_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': away_team_id, 'team_name': away_team_name,
                        'loc': 'A',
                        'opp_team_id': home_team_id, 'opp_team_name': home_team_name,
                        'team_score': away_team_score, 'opp_score': home_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                kr_ret = str(p_stats[1].text).split('/')
                mfg_ret = str(p_stats[2].text).split('/')

                row_df['kick_return_ret'] = int(kr_ret[0])
                row_df['kick_return_yds'] = int(kr_ret[1])
                row_df['kick_return_avg'] = None
                row_df['kick_return_td'] = int(kr_ret[2])

                row_df['missed_fg_return_ret'] = int(mfg_ret[0])
                row_df['missed_fg_return_yds'] = int(mfg_ret[1])
                row_df['missed_fg_return_avg'] = None
                row_df['missed_fg_return_td'] = int(mfg_ret[2])

                if len(row_df) > 0:
                    returns_df = pd.concat(
                        [returns_df, row_df], ignore_index=True)

                del player_id, player_name, row_df, kr_ret, mfg_ret

            for j in range(2, len(home_stats)):
                p_stats = home_stats[j].find_all('td')
                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = home_team_id * -1
                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': home_team_id, 'team_name': home_team_name,
                        'loc': 'H',
                        'opp_team_id': away_team_id, 'opp_team_name': away_team_name,
                        'team_score': home_team_score, 'opp_score': away_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                kr_ret = str(p_stats[1].text).split('/')
                mfg_ret = str(p_stats[2].text).split('/')

                row_df['kick_return_ret'] = int(kr_ret[0])
                row_df['kick_return_yds'] = int(kr_ret[1])
                row_df['kick_return_avg'] = None
                row_df['kick_return_td'] = int(kr_ret[2])

                row_df['missed_fg_return_ret'] = int(mfg_ret[0])
                row_df['missed_fg_return_yds'] = int(mfg_ret[1])
                row_df['missed_fg_return_avg'] = None
                row_df['missed_fg_return_td'] = int(mfg_ret[2])

                if len(row_df) > 0:
                    returns_df = pd.concat(
                        [returns_df, row_df], ignore_index=True)

                del player_id, player_name, row_df, kr_ret, mfg_ret

            # print(returns_df)

        elif i == 6:  # Defensive (Tackling)
            away_stats = table_html.find(
                'div', {'class': 'colone'}).find('table').find_all('tr')
            home_stats = table_html.find(
                'div', {'class': 'coltwo'}).find('table').find_all('tr')

            for j in range(2, len(away_stats)):
                # player_stats = j.find_all('td')
                p_stats = away_stats[j].find_all('td')

                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = away_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': away_team_id, 'team_name': away_team_name,
                        'loc': 'A',
                        'opp_team_id': home_team_id, 'opp_team_name': home_team_name,
                        'team_score': away_team_score, 'opp_score': home_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                tack = str(p_stats[1].text).split('/')
                sacs = str(p_stats[3].text).split('/')
                ff_fr = str(p_stats[4].text).split('/')

                row_df['defense_tackles_solo'] = int(tack[0])
                row_df['defense_tackles_ast'] = int(tack[1])
                row_df['defense_tackles_total'] = row_df['defense_tackles_ast'] + \
                    row_df['defense_tackles_solo']

                row_df['defnese_passes_defended'] = int(p_stats[2].text)

                row_df['defense_sacks'] = float(sacs[0])
                row_df['defense_sack_yds'] = int(sacs[1])
                row_df['defense_forced_fumbles'] = int(ff_fr[0])
                row_df['defense_fumble_recoveries'] = int(ff_fr[1])

                if len(row_df) > 0:
                    tackling_df = pd.concat(
                        [tackling_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            for j in range(2, len(home_stats)):
                p_stats = home_stats[j].find_all('td')
                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = home_team_id * -1
                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': home_team_id, 'team_name': home_team_name,
                        'loc': 'H',
                        'opp_team_id': away_team_id, 'opp_team_name': away_team_name,
                        'team_score': home_team_score, 'opp_score': away_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                tack = str(p_stats[1].text).split('/')
                sacs = str(p_stats[3].text).split('/')
                ff_fr = str(p_stats[4].text).split('/')

                row_df['defense_tackles_solo'] = int(tack[0])
                row_df['defense_tackles_ast'] = int(tack[1])
                row_df['defense_tackles_total'] = row_df['defense_tackles_ast'] + \
                    row_df['defense_tackles_solo']

                row_df['defnese_passes_defended'] = int(p_stats[2].text)

                row_df['defense_sacks'] = float(sacs[0])
                row_df['defense_sack_yds'] = int(sacs[1])
                row_df['defense_forced_fumbles'] = int(ff_fr[0])
                row_df['defense_fumble_recoveries'] = int(ff_fr[1])

                if len(row_df) > 0:
                    tackling_df = pd.concat(
                        [tackling_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            # print(tackling_df)

        elif i == 7:  # Defensive (Interceptions)
            away_stats = table_html.find(
                'div', {'class': 'colone'}).find('table').find_all('tr')
            home_stats = table_html.find(
                'div', {'class': 'coltwo'}).find('table').find_all('tr')

            for j in range(2, len(away_stats)):
                # player_stats = j.find_all('td')
                p_stats = away_stats[j].find_all('td')
                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = away_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': away_team_id, 'team_name': away_team_name,
                        'loc': 'A',
                        'opp_team_id': home_team_id, 'opp_team_name': home_team_name,
                        'team_score': away_team_score, 'opp_score': home_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                row_df['defense_interceptions'] = int(p_stats[1].text)
                row_df['defense_interception_yds'] = int(p_stats[2].text)
                row_df['defense_interception_avg'] = None
                row_df['defense_interception_tds'] = int(p_stats[3].text)

                if len(row_df) > 0:
                    interceptions_df = pd.concat(
                        [interceptions_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            for j in range(2, len(home_stats)):
                p_stats = home_stats[j].find_all('td')
                try:
                    player_id = str(p_stats[0].find('a').get(
                        'href')).replace('/players/', '').replace('/', '')
                except:
                    player_id = home_team_id * -1

                player_name = p_stats[0].text
                row_df = pd.DataFrame(
                    {
                        'season': season, 'game_id': game_id,
                        'team_id': home_team_id, 'team_name': home_team_name,
                        'loc': 'H',
                        'opp_team_id': away_team_id, 'opp_team_name': away_team_name,
                        'team_score': home_team_score, 'opp_score': away_team_score, 'is_overtime_game': is_overtime_game,
                        'player_id': player_id, 'player_name': player_name
                    },
                    index=[0])

                row_df['defense_interceptions'] = int(p_stats[1].text)
                row_df['defense_interception_yds'] = int(p_stats[2].text)
                row_df['defense_interception_avg'] = None
                row_df['defense_interception_tds'] = int(p_stats[3].text)

                if len(row_df) > 0:

                    interceptions_df = pd.concat(
                        [interceptions_df, row_df], ignore_index=True)

                del player_id, player_name, row_df

            # print(interceptions_df)

            print('')

    if len(stat_tables) > 1:
        # Passing/Rushing
        if len(passing_df) > 0 and len(rushing_df) > 0:
            game_df = pd.merge(passing_df, rushing_df, how='outer', on=['season', 'game_id', 'team_id', 'team_name', 'loc',
                                                                        'opp_team_id', 'opp_team_name', 'team_score', 'opp_score', 'is_overtime_game', 'player_id', 'player_name'])
            game_df.loc[game_df['passing_att'] > 0,
                        'passing_comp_pct'] = game_df['passing_comp'] / game_df['passing_att']

            game_df.loc[game_df['passing_att'] > 0,
                        'passing_ypa'] = game_df['passing_yds'] / game_df['passing_att']

            game_df.loc[game_df['passing_comp'] > 0,
                        'passing_ypc'] = game_df['passing_yds'] / game_df['passing_comp']

            game_df.loc[game_df['passing_att'] > 0,
                        'passing_nfl_qbr'] = 0

            game_df.loc[game_df['passing_att'] > 0,
                        'passing_cfb_qbr'] = 0

            game_df.loc[game_df['rushing_att'] > 0,
                        'rushing_avg'] = game_df['rushing_yds'] / game_df['rushing_att']

        # Receiving
        if len(receiving_df) > 0:
            game_df = game_df.merge(receiving_df, how='outer', on=['season', 'game_id', 'team_id', 'team_name', 'loc',
                                                                   'opp_team_id', 'opp_team_name', 'team_score', 'opp_score', 'is_overtime_game', 'player_id', 'player_name'])

            game_df.loc[game_df['receiving_rec'] > 0,
                        'receiving_avg'] = game_df['receiving_yds'] / game_df['receiving_rec']

        # Tackling
        if len(tackling_df) > 0:
            game_df = game_df.merge(tackling_df, how='outer', on=['season', 'game_id', 'team_id', 'team_name', 'loc',
                                                                  'opp_team_id', 'opp_team_name', 'team_score', 'opp_score', 'is_overtime_game', 'player_id', 'player_name'])

        # Interceptions
        if len(interceptions_df) > 0:
            game_df = game_df.merge(interceptions_df, how='outer', on=['season', 'game_id', 'team_id', 'team_name', 'loc',
                                                                       'opp_team_id', 'opp_team_name', 'team_score', 'opp_score', 'is_overtime_game', 'player_id', 'player_name'])

            game_df.loc[game_df['defense_interceptions'] > 0,
                        'defense_interception_avg'] = game_df['defense_interception_yds'] / game_df['defense_interceptions']

        # Kicking
        if len(kicking_df) > 0:
            game_df = game_df.merge(kicking_df, how='outer', on=['season', 'game_id', 'team_id', 'team_name', 'loc',
                                                                 'opp_team_id', 'opp_team_name', 'team_score', 'opp_score', 'is_overtime_game', 'player_id', 'player_name'])

            game_df.loc[game_df['kicking_XPA'] > 0,
                        'kicking_XP%'] = game_df['kicking_XPM'] / game_df['kicking_XPA']

            game_df.loc[game_df['kicking_FGA'] > 0,
                        'kicking_FG%'] = game_df['kicking_FGM'] / game_df['kicking_FGA']

            game_df.loc[game_df['kicking_2pt_A'] > 0,
                        'kicking_2pt%'] = game_df['kicking_2pt_M'] / game_df['kicking_2pt_A']

            game_df.loc[game_df['kicking_2pt_A'] > 0,
                        'kicking_4pt%'] = game_df['kicking_4pt_M'] / game_df['kicking_4pt_A']

        # Returns
        if len(returns_df) > 0:
            game_df = game_df.merge(returns_df, how='outer', on=['season', 'game_id', 'team_id', 'team_name', 'loc',
                                                                 'opp_team_id', 'opp_team_name', 'team_score', 'opp_score', 'is_overtime_game', 'player_id', 'player_name'])

            game_df.loc[game_df['kick_return_ret'] > 0,
                        'kick_return_avg'] = game_df['kick_return_yds'] / game_df['kick_return_ret']

            game_df.loc[game_df['missed_fg_return_ret'] > 0,
                        'missed_fg_return_avg'] = game_df['missed_fg_return_yds'] / game_df['missed_fg_return_ret']

        game_df = game_df.reindex(columns=col_names)

    else:
        print(f'No stats found for game #{game_id}.')

    return game_df


def get_arena_season_game_stats(season: int):
    season_df = pd.DataFrame()
    game_df = pd.DataFrame()

    sched_df = get_arenafan_schedule(season)
    sched_df = sched_df.dropna(subset=['game_id'])

    game_id_arr = sched_df['game_id'].to_list()

    for i in tqdm(game_id_arr):
        game_df = get_arena_game_stats(i)
        season_df = pd.concat([season_df, game_df], ignore_index=True)

    return season_df


if __name__ == "__main__":
    # df = get_arena_game_stats(5689)
    # print(df.columns)
    for i in range(1986, 1990):
        df = get_arena_season_game_stats(i)
        if len(df) > 0:
            df.to_csv(
                f'arena_football_league/game_stats/player/csv/{i}_arena_player_game_stats.csv', index=False)
            df.to_parquet(
                f'arena_football_league/game_stats/player/parquet/{i}_arena_player_game_stats.parquet', index=False)
