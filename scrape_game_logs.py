import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

import DBInfo

# THIS FILE WILL SCRAPE EACH INDIVIDUAL GAME FROM THE 2021-2022 NFL SEASON, AND PUT ALL THIS DATA INTO A DATABASE.
# THE REASON THIS IS ALL DONE WITH THE SAME WEBDRIVER IS THE WEBDRIVER IS PRETTY SLOW, SO ALTHOUGH SEPERATING ALL OF
# THIS OUT INTO THREE DIFFERENT PY FILES WOULD BE BETTER ORGANIZED, IT WOULD ALSO TAKE FOREVER * 3

def scrape_game_logs(parsed_game_logs_info, parsed_game_logs_team_stats, parsed_passing_tuples, parsed_rush_receive_tuples, parsed_snap_count_tuples):
    name_to_abr = {
        "New England Patriots": "NWE",
        "Buffalo Bills": "BUF",
        "Arizona Cardinals": "ARI",
        "Atlanta Falcons": "ATL",
        "Baltimore Ravens": "BAL",
        "Carolina Panthers": "CAR",
        "Chicago Bears": "CHI",
        "Cincinnati Bengals": "CIN",
        "Cleveland Browns": "CLE",
        "Dallas Cowboys": "DAL",
        "Denver Broncos": "DEN",
        "Detroit Lions": "DET",
        "Green Bay Packers": "GNB",
        "Houston Texans": "HOU",
        "Indianapolis Colts": "IND",
        "Jacksonville Jaguars": "JAX",
        "Kansas City Chiefs": "KAN",
        "Las Vegas Raiders": "LVR",
        "Los Angeles Chargers": "LAC",
        "Los Angeles Rams": "LAR",
        "Miami Dolphins": "MIA",
        "Minnesota Vikings": "MIN",
        "New Orleans Saints": "NOR",
        "New York Giants": "NYG",
        "New York Jets": "NYJ",
        "Philadelphia Eagles": "PHI",
        "Pittsburgh Steelers": "PIT",
        "San Francisco 49ers": "SFO",
        "Seattle Seahawks": "SEA",
        "Tampa Bay Buccaneers": "TAM",
        "Tennessee Titans": "TEN",
        "Washington Football Team": "WAS"
    }



    rows_parsed = []
    driver = webdriver.Edge('C:/Program Files/EdgeWebDriver/msedgedriver')
    diver_driver = webdriver.Edge('C:/Program Files/EdgeWebDriver/msedgedriver')

    for i in range(1, 19):
        driver.get('https://www.pro-football-reference.com/years/2021/week_' + str(i) + '.htm')

        sleep(1)
        sourceCode = driver.page_source

        soup = BeautifulSoup(sourceCode, 'html.parser')
        links = soup.find_all('div', class_='game_summaries')[1].find_all("td", class_="right gamelink")

        for log in links:
            print('Start')

            a = log.find('a', href=True)
            url = a['href']
            game_id = url[12:len(url) - 4]

            diver_driver.get('https://www.pro-football-reference.com/' + url)

            sleep(1)
            logSourceCode = diver_driver.page_source

            log_soup = BeautifulSoup(logSourceCode, 'html.parser')

            # BUILDING THE OVERALL GAME LOG
            parsed_game_log = {"GameID": game_id, 'Week': i}
            parsed_winning_team = {}
            parsed_losing_team = {}

            OT = get_linescore(parsed_game_log, parsed_winning_team, parsed_losing_team, log_soup)

            parsed_winning_team['GameID'] = game_id
            parsed_winning_team['IsAWin'] = True
            parsed_losing_team['GameID'] = game_id
            parsed_losing_team['IsAWin'] = False

            get_scorebox(parsed_game_log, parsed_winning_team, parsed_losing_team, log_soup)
            get_gameinfo(parsed_game_log, log_soup, OT)
            get_teamstats(name_to_abr, parsed_game_log, parsed_winning_team, parsed_losing_team, log_soup)


            print(parsed_game_log)

            parsed_game_logs_info.append(parsed_game_log)
            parsed_game_logs_team_stats.append(parsed_winning_team)
            parsed_game_logs_team_stats.append(parsed_losing_team)

            # BUILDING INDIVIDUAL PLAYER GAME LOGS
           # get_snapcounts(log_soup, game_id, parsed_game_log['WinningTeamInfo']['TeamName'],
            #                parsed_game_log['LosingTeamInfo']['TeamName'], parsed_snap_count_tuples)
            #get_playerlogs(log_soup,parsed_passing_tuples, parsed_rush_receive_tuples, game_id)




def get_linescore(parsed_game_log, parsed_winning_team, parsed_losing_team, log_soup):

    # GET LINESCORE
    line_scores = log_soup.find("table", class_='linescore nohover stats_table no_freeze').find('tbody').findAll('tr')
    top_team = line_scores[0]
    bottom_team = line_scores[1]

    #GRAB NAMES FROM LINK ELEMENT
    top_team_name = str(top_team.find_all("a")[2].contents[0])
    bot_team_name = str(bottom_team.find_all("a")[2].contents[0])
    #GRAB SCORES FROM LINESCORE TABLE
    top_team_scores = top_team.find_all('td')
    bot_team_scores = bottom_team.find_all('td')

    #LENGTH OF TABLE INDICATES WHETHER THERE WAS OT
    if len(top_team_scores) > 7:
        OT = True
        top_ot = int(top_team_scores[6].contents[0])
        top_total = int(top_team_scores[7].contents[0])

        bot_ot = int(bot_team_scores[6].contents[0])
        bot_total = int(bot_team_scores[7].contents[0])

    else:
        OT = False
        top_ot = 0
        top_total = int(top_team_scores[6].contents[0])

        bot_ot = 0
        bot_total = int(bot_team_scores[6].contents[0])

    parsed_game_log['OT'] = OT

    if top_total == bot_total:
        parsed_game_log['IsTie'] = True
        parsed_winning_team['TeamName'] = top_team_name
        parsed_winning_team['FirstQuarter'] = int(top_team_scores[2].contents[0])
        parsed_winning_team['SecondQuarter'] = int(top_team_scores[3].contents[0])
        parsed_winning_team['ThirdQuarter'] = int(top_team_scores[4].contents[0])
        parsed_winning_team['FourthQuarter'] = int(top_team_scores[5].contents[0])
        parsed_winning_team['OTTotal'] = top_ot
        parsed_winning_team['TotalScore'] = top_total

        parsed_losing_team['TeamName'] = bot_team_name
        parsed_losing_team['FirstQuarter'] = int(bot_team_scores[2].contents[0])
        parsed_losing_team['SecondQuarter'] = int(bot_team_scores[3].contents[0])
        parsed_losing_team['ThirdQuarter'] = int(bot_team_scores[4].contents[0])
        parsed_losing_team['FourthQuarter'] = int(bot_team_scores[5].contents[0])
        parsed_losing_team['OTTotal'] = bot_ot
        parsed_losing_team['TotalScore'] = bot_total

    # WHICH TEAM WON?
    elif top_total > bot_total:
        parsed_game_log['IsTie'] = False
        parsed_winning_team['TeamName'] = top_team_name
        parsed_winning_team['FirstQuarter'] = int(top_team_scores[2].contents[0])
        parsed_winning_team['SecondQuarter'] = int(top_team_scores[3].contents[0])
        parsed_winning_team['ThirdQuarter'] = int(top_team_scores[4].contents[0])
        parsed_winning_team['FourthQuarter'] = int(top_team_scores[5].contents[0])
        parsed_winning_team['OTTotal'] = top_ot
        parsed_winning_team['TotalScore'] = top_total

        parsed_losing_team['TeamName'] = bot_team_name
        parsed_losing_team['FirstQuarter'] = int(bot_team_scores[2].contents[0])
        parsed_losing_team['SecondQuarter'] = int(bot_team_scores[3].contents[0])
        parsed_losing_team['ThirdQuarter'] = int(bot_team_scores[4].contents[0])
        parsed_losing_team['FourthQuarter'] = int(bot_team_scores[5].contents[0])
        parsed_losing_team['OTTotal'] = bot_ot
        parsed_losing_team['TotalScore'] = bot_total

    else:
        parsed_game_log['IsTie'] = False
        parsed_winning_team['TeamName'] = bot_team_name
        parsed_winning_team['FirstQuarter'] = int(bot_team_scores[2].contents[0])
        parsed_winning_team['SecondQuarter'] = int(bot_team_scores[3].contents[0])
        parsed_winning_team['ThirdQuarter'] = int(bot_team_scores[4].contents[0])
        parsed_winning_team['FourthQuarter'] = int(bot_team_scores[5].contents[0])
        parsed_winning_team['OTTotal'] = bot_ot
        parsed_winning_team['TotalScore'] = bot_total

        parsed_losing_team['TeamName'] = top_team_name
        parsed_losing_team['FirstQuarter'] = int(top_team_scores[2].contents[0])
        parsed_losing_team['SecondQuarter'] = int(top_team_scores[3].contents[0])
        parsed_losing_team['ThirdQuarter'] = int(top_team_scores[4].contents[0])
        parsed_losing_team['FourthQuarter'] = int(top_team_scores[5].contents[0])
        parsed_losing_team['OTTotal'] = top_ot
        parsed_losing_team['TotalScore'] = top_total

    #OT IS NEEDED IN ANOTHER FUNCTION, PASS IT OVER
    return OT

def get_scorebox(parsed_game_log, parsed_winning_team, parsed_losing_team, log_soup):
    score_box = log_soup.find("div", class_='scorebox')
    # SCORE BOX DIVS CORRESPOND TO DATA NEEDED
    score_box_divs = score_box.findAll("div")

    #WHICH TEAM IS WHICH IS STILL UNKNOWN, NEED TO CHECK THEIR NAMES
    first_team = score_box_divs[0]
    second_team = score_box_divs[8]
    game_info = score_box.find('div', class_='scorebox_meta')

    # VERIFY WHICH TEAM IS WHICH
    if first_team.find_all("a")[2].contents[0] == parsed_winning_team['TeamName']:

        parsed_winning_team['Record'] = str(first_team.find_all('div')[4].contents[0])
        parsed_winning_team['Coach'] = str(first_team.find('div', class_='datapoint').find('a').contents[0])

        parsed_losing_team['Record'] = str(second_team.find_all('div')[4].contents[0])
        parsed_losing_team['Coach'] = str(second_team.find('div', class_='datapoint').find('a').contents[0])

    else:
        parsed_first = first_team.find_all('div')

        parsed_winning_team['Record'] = str(first_team.find_all('div')[4].contents[0])
        parsed_winning_team['Coach'] = str(first_team.find('div', class_='datapoint').find('a').contents[0])

        parsed_losing_team['Record'] = str(second_team.find_all('div')[4].contents[0])
        parsed_losing_team['Coach'] = str(second_team.find('div', class_='datapoint').find('a').contents[0])

    sep_game_info = game_info.findAll('div')

    parsed_game_log['DayOfWeek'] = sep_game_info[0].contents[0].split()[0][0:2]
    # DATE HAS A SMALL PIECE OF UNNECESSARY TEXT IN FRONT, NEED TO PARSE IT OUT
    date_split = sep_game_info[0].contents[0].split()[1:]

    # DATE NEEDS TO BE PROPERLY FORMATTED TO SQL DATE TYPE
    month_to_num = {'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12', 'Jan': '01'}
    day_iso = date_split[1].replace(',', '')
    if len(day_iso) == 1:
        day_iso = '0' + day_iso

    parsed_game_log['Date'] = date_split[2] + '-' + month_to_num[date_split[0]] + '-' + day_iso

    # TIME NEEDS TO BE PROPERLY FORMATTED TO SQL TIME TYPE
    start_time = str(sep_game_info[1].contents[1][2:])
    start_time_split = start_time.split(':')
    hours = start_time_split[0]

    if start_time[len(start_time)-2:len(start_time)] == 'pm':
        hours = str(int(hours) + 12)

    if len(hours) == 1:
        hours = '0' + hours
    start_time = hours + ':' + start_time_split[1][0:2] + ':00'

    parsed_game_log['StartTime'] = start_time
    parsed_game_log['Stadium'] = str(sep_game_info[2].find('a').contents[0])

def get_gameinfo(parsed_game_log, log_soup, OT):
    game_info_rows = log_soup.find('table', id='game_info').find('tbody').find_all('td')

    #SOMETIMES THE HEADER OF THE TABLE IS INCLUDED, NEEDS TO BE PARSED OUT
    if str(game_info_rows[0].contents[0]) == 'Game Info':
        game_info_rows = game_info_rows[1:]

    # OT GAMES HAVE AN EXTRA ROW OF DATA THAT NEEDS TO BE ACCOUNTED FOR APPROPIATELY
    if OT:
        parsed_game_log['TossResult'] = str(game_info_rows[0].contents[0])
        parsed_game_log['OTTossResult'] = str(game_info_rows[1].contents[0])
        parsed_game_log['Roof'] = str(game_info_rows[2].contents[0])
        parsed_game_log['Surface'] = str(game_info_rows[3].contents[0])

        #DURATION IS RECORED IN MINUTES
        dur_inter = str(game_info_rows[4].contents[0]).split(':')

        parsed_game_log['Duration'] = int(dur_inter[0]) * 60 + int(dur_inter[1])

        # WEATHER IS ONLY RECORDED FOR SOME GAMES, NUMBER OF ROWS WILL MAKE THIS EVIDENT
        if len(game_info_rows) == 9:
            weather = str(game_info_rows[6].contents[0]).split()
            parsed_game_log['Temperature'] = weather[0]
            wind = weather[6]

            # IF THERES NO WIND, weather[6] WILL BE 'WIND', SO THEN SET WIND MPH TO 0
            if wind == 'wind':
                wind = 0

            parsed_game_log['Wind'] = int(wind)

        else:
            parsed_game_log['Temperature'] = None
            parsed_game_log['Wind'] = None


    else:
        parsed_game_log['TossResult'] = str(game_info_rows[0].contents[0])
        parsed_game_log['OTTossResult'] = None
        parsed_game_log['Roof'] = str(game_info_rows[1].contents[0])
        parsed_game_log['Surface'] = str(game_info_rows[2].contents[0])
        dur_inter = str(game_info_rows[3].contents[0]).split(':')

        parsed_game_log['Duration'] = int(dur_inter[0]) * 60 + int(dur_inter[1])

        if len(game_info_rows) == 8:
            weather = str(game_info_rows[5].contents[0]).split()
            parsed_game_log['Temperature'] = weather[0]
            wind = weather[6]

            if wind == 'wind':
                wind = 0

            parsed_game_log['Wind'] = int(wind)

        else:
            parsed_game_log['Temperature'] = None
            parsed_game_log['Wind'] = None

def get_teamstats(name_to_abr, parsed_game_log, parsed_winning_team, parsed_losing_team, log_soup):
    team_stats = log_soup.find('table', id='team_stats')
    ts_headers = team_stats.find('thead').find_all('th')

    # NEED TO KNOW WHICH TEAM IS WHICH BY NAME, CONVERSION FROM ABBREVIATION ON PFR TO FULL NAME ALLOWS THIS TO BE KNOWN
    if name_to_abr[parsed_winning_team['TeamName']] == ts_headers[1].contents[0]:
        left_team = parsed_winning_team
        right_team = parsed_losing_team

    else:
        right_team = parsed_winning_team
        left_team = parsed_losing_team

    ts_rows = team_stats.find('tbody').find_all('td', class_='center')

    # MOST OF THE DATA HERE NEEDED TO BE PARSED BETWEEN DASHES, ( 1 OUT OF 4 FOURTH DOWNS )
    left_team['FirstDowns'] = int(ts_rows[0].contents[0])
    right_team['FirstDowns'] = int(ts_rows[1].contents[0])
    left_team['Penalties'] = int(ts_rows[16].contents[0].split('-')[0])
    right_team['Penalties'] = int(ts_rows[17].contents[0].split('-')[0])
    left_team['PenaltyYards'] = int(ts_rows[16].contents[0].split('-')[1])
    right_team['PenaltyYards'] = int(ts_rows[17].contents[0].split('-')[1])
    left_team['ThirdDownAttempts'] = int(ts_rows[18].contents[0].split('-')[0])
    right_team['ThirdDownAttempts'] = int(ts_rows[19].contents[0].split('-')[0])
    left_team['ThirdDownConversions'] = int(ts_rows[18].contents[0].split('-')[1])
    right_team['ThirdDownConversions'] = int(ts_rows[19].contents[0].split('-')[1])
    left_team['FourthDownAttempts'] = int(ts_rows[20].contents[0].split('-')[0])
    right_team['FourthDownAttempts'] = int(ts_rows[21].contents[0].split('-')[0])
    left_team['FourthDownConversions'] = int(ts_rows[20].contents[0].split('-')[1])
    right_team['FourthDownConversions'] = int(ts_rows[21].contents[0].split('-')[1])
    left_team['ToP'] = int(ts_rows[22].contents[0].split(':')[0]) * 60 + int(ts_rows[22].contents[0].split(':')[1])
    right_team['ToP'] = int(ts_rows[22].contents[0].split(':')[0]) * 60 + int(ts_rows[22].contents[0].split(':')[1])

def get_snapcounts(log_soup, game_id, winning_team_name, losing_team_name, parsed_snap_count_tuples):
    home_snap_count_div = log_soup.find('div', id='all_home_snap_counts')

    home_team_name = home_snap_count_div.find('h2').contents[0].split()[0]

    wtn_split = winning_team_name.split()
    # NORMALISE TEAM NAMES SO THEY ARE CONSISTENT ACROSS DB
    if home_team_name == wtn_split[len(wtn_split)-1] or home_team_name == ' '.join(wtn_split[1:3]):
        home_team_name = winning_team_name
        away_team_name = losing_team_name

    else:
        home_team_name = losing_team_name
        away_team_name = winning_team_name

    home_snap_rows = home_snap_count_div.find('table', id='home_snap_counts').find('tbody').find_all('tr')
    for row in home_snap_rows:
        cells = row.find_all('td')
        if not len(cells) == 0:

            snap_perc = cells[2].contents[0]
            snap_perc = int(snap_perc[0: len(snap_perc) - 1])
            if snap_perc == 0:
                break

            else:
                parsed_snap_tuple = {
                    'GameID': game_id,
                    'TeamName': home_team_name,
                    'Name': row.find('a').contents[0],
                    'Position': cells[0].contents[0],
                    'SnapPercentage': snap_perc
                }

                parsed_snap_count_tuples.append(parsed_snap_tuple)

    away_snap_count_div = log_soup.find('table', id='vis_snap_counts')

    away_snap_rows = away_snap_count_div.find('tbody').find_all('tr')
    for row in away_snap_rows:
        cells = row.find_all('td')
        if not len(cells) == 0:
            snap_perc = cells[2].contents[0]
            snap_perc = int(snap_perc[0: len(snap_perc) - 1])
            if snap_perc == 0:
                break

            else:
                parsed_snap_tuple = {
                    'GameID': game_id,
                    'TeamName': away_team_name,
                    'Name': row.find('a').contents[0],
                    'Position': cells[0].contents[0],
                    'SnapPercentage': snap_perc
                }

                parsed_snap_count_tuples.append(parsed_snap_tuple)






def get_playerlogs(log_soup, parsed_passing_tuples, parsed_rush_receive_tuples, game_id):

    abr_to_name = {
        "NWE": "New England Patriots",
        "BUF": "Buffalo Bills",
        "ARI": "Arizona Cardinals",
        "ATL": "Atlanta Falcons",
        "BAL": "Baltimore Ravens",
        "CAR": "Carolina Panthers",
        "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals",
        "CLE": "Cleveland Browns",
        "DAL": "Dallas Cowboys",
        "DEN": "Denver Broncos",
        "DET": "Detroit Lions",
        "GNB": "Green Bay Packers",
        "HOU": "Houston Texans",
        "IND": "Indianapolis Colts",
        "JAX": "Jacksonville Jaguars",
        "KAN": "Kansas City Chiefs",
        "LVR": "Las Vegas Raiders",
        "LAC": "Los Angeles Chargers",
        "LAR": "Los Angeles Rams",
        "MIA": "Miami Dolphins",
        "MIN": "Minnesota Vikings",
        "NOR": "New Orleans Saints",
        "NYG": "New York Giants",
        "NYJ": "New York Jets",
        "PHI": "Philadelphia Eagles",
        "PIT": "Pittsburgh Steelers",
        "SFO": "San Francisco 49ers",
        "SEA": "Seattle Seahawks",
        "TAM": "Tampa Bay Buccaneers",
        "TEN": "Tennessee Titans",
        "WAS": "Washington Football Team"
    }

    off_table = log_soup.find("table", id="player_offense")
    player_row_cont = off_table.find("tbody")
    player_rows = player_row_cont.findAll("tr")



    for row in player_rows:
        cells = row.find_all("td")
        if len(cells) > 0:
            # IF A PLAYER DID NOT PASS AT ALL, DONT RECORD PASSING STATS, WOULD BE WASTE OF SPACE
            if not str(cells[2].contents[0]) == "0":
                parsed_passing_tuple = {
                    "GameID": game_id,
                    "Name": str(row.find("a").contents[0]),
                    "TeamName": abr_to_name[str(cells[0].contents[0])],
                    "Completions": int(cells[1].contents[0]),
                    "Attempts": int(cells[2].contents[0]),
                    "Yards": int(cells[3].contents[0]),
                    "Touchdowns": int(cells[4].contents[0]),
                    "Interceptions": int(cells[5].contents[0]),
                    "Sacks": int(cells[6].contents[0]),
                    "SackYards": int(cells[7].contents[0]),
                    "PassLong": int(cells[8].contents[0]),
                    "PasserRating": float(cells[9].contents[0])

                }

                parsed_passing_tuples.append(parsed_passing_tuple)

            parsed_rush_receive_tuple = {
                "GameID": game_id,
                "Name": str(row.find("a").contents[0]),
                "TeamName": abr_to_name[str(cells[0].contents[0])],
                "RushAttempts": int(cells[10].contents[0]),
                "RushYards": int(cells[11].contents[0]),
                "RushTouchdowns": int(cells[12].contents[0]),
                "RushLong": int(cells[13].contents[0]),
                "Targets": int(cells[14].contents[0]),
                "Receptions": int(cells[15].contents[0]),
                "ReceivingYards": int(cells[16].contents[0]),
                "ReceivingTouchdowns": int(cells[17].contents[0]),
                "ReceivingLong": int(cells[18].contents[0]),
                "Fumbles": int(cells[19].contents[0]),
                "FumblesLost": int(cells[20].contents[0])
            }

            # ADD IT TO THE LIST
            parsed_rush_receive_tuples.append(parsed_rush_receive_tuple)

def store_game_logs_info_in_DB(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD, database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = (
                'INSERT INTO GameLogsInfo(GameID, Week, OT, IsTie, DayOfWeek, Date, StartTime, Stadium, TossResult, OTTossResult, '
                'Roof, Surface, Duration, Temperature, Wind)' 
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['GameID'], tuple['Week'], tuple['OT'], tuple['IsTie'], tuple['DayOfWeek'], tuple['Date'],
                                   tuple['StartTime'], tuple['Stadium'], tuple['TossResult'], tuple['OTTossResult'],
                                   tuple['Roof'], tuple['Surface'], tuple['Duration'], tuple['Temperature'], tuple['Wind']
                                   ))

    db.commit()

def store_game_logs_team_stats_in_DB(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD,
                         database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = (
            'INSERT INTO GameLogsTeamData(GameID, TeamName, FirstQuarter, SecondQuarter, ThirdQuarter, FourthQuarter, OTTotal,'
            'TotalScore, Record, Coach, FirstDowns, Penalties, PenaltyYards, ThirdDownAttempts, ThirdDownConversions, '
            'FourthDownAttempts, FourthDownConversions, ToP, IsAWin)'
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    )

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['GameID'],
                                   tuple['TeamName'],
                                   tuple['FirstQuarter'],
                                   tuple['SecondQuarter'],
                                   tuple['ThirdQuarter'],
                                   tuple['FourthQuarter'],
                                   tuple['OTTotal'],
                                   tuple['TotalScore'],
                                   tuple['Record'],
                                   tuple['Coach'],
                                   tuple['FirstDowns'],
                                   tuple['Penalties'],
                                   tuple['PenaltyYards'],
                                   tuple['ThirdDownAttempts'],
                                   tuple['ThirdDownConversions'],
                                   tuple['FourthDownAttempts'],
                                   tuple['FourthDownConversions'],
                                   tuple['ToP'],
                                   tuple['IsAWin']
                                   ))

    db.commit()




def store_player_passing_in_DB(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD, database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = ('INSERT INTO PlayerPassingGameLogs(GameID, Name, TeamName, Completions, Attempts, Yards, TouchDowns,'
           'Interceptions, Sacks, SackYards, PassLong, PasserRating) '
           'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['GameID'],
                                   tuple['Name'],
                                   tuple['TeamName'],
                                   tuple['Completions'],
                                   tuple['Attempts'],
                                   tuple['Yards'],
                                   tuple['Touchdowns'],
                                   tuple['Interceptions'],
                                   tuple['Sacks'],
                                   tuple['SackYards'],
                                   tuple['PassLong'],
                                   tuple['PasserRating']
                                   ))

    db.commit()

def store_player_RR_in_DB(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD, database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = ('INSERT INTO PlayerRushReceiveGameLogs(GameID, Name, TeamName, RushAttempts, RushYards, RushTouchDowns, RushLong,'
           'Targets, Receptions, ReceivingYards, ReceivingTouchDowns, Fumbles, FumblesLost) '
           'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['GameID'],
                                   tuple['Name'],
                                   tuple['TeamName'],
                                   tuple['RushAttempts'],
                                   tuple['RushYards'],
                                   tuple['RushTouchdowns'],
                                   tuple['RushLong'],
                                   tuple['Targets'],
                                   tuple['Receptions'],
                                   tuple['ReceivingYards'],
                                   tuple['ReceivingTouchdowns'],
                                   tuple['Fumbles'],
                                   tuple['FumblesLost']
                                   ))

    db.commit()

def store_player_snapcounts_in_DB(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD, database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = ('INSERT INTO PlayerSnapCountGameLogs(GameID, Name, TeamName, Position, SnapPercentage) '
           'VALUES(%s, %s, %s, %s, %s)')

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['GameID'],
                                   tuple['Name'],
                                   tuple['TeamName'],
                                   tuple['Position'],
                                   tuple['SnapPercentage']
                                   ))

    db.commit()


if __name__ == "__main__":
    parsed_game_logs_info = []
    parsed_game_logs_team_stats = []
    parsed_passing_tuples = []
    parsed_rush_receive_tuples = []
    parsed_snap_count_tuples = []
    scrape_game_logs(parsed_game_logs_info, parsed_game_logs_team_stats, parsed_passing_tuples, parsed_rush_receive_tuples, parsed_snap_count_tuples)

    store_game_logs_info_in_DB(parsed_game_logs_info)
    store_game_logs_team_stats_in_DB(parsed_game_logs_team_stats)
    #store_player_passing_in_DB(parsed_passing_tuples)
    #store_player_RR_in_DB(parsed_rush_receive_tuples)
    #store_player_snapcounts_in_DB(parsed_snap_count_tuples)

