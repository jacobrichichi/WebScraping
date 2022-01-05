import requests
from bs4 import BeautifulSoup
import pymysql
import configparser
from selenium import webdriver
from time import sleep
import DBInfo

def web_scrape():
    team_abrvs = ['nwe', 'buf', 'mia', 'nyj', 'cin', 'rav', 'pit', 'cle',
                  'oti', 'clt', 'htx', 'jax', 'kan', 'sdg', 'rai', 'den',
                  'dal', 'phi', 'was', 'nyg', 'gnb', 'min', 'chi', 'det',
                  'tam', 'nor', 'atl', 'car', 'ram', 'crd', 'sfo', 'sea']

    team_mapping = {
        "nwe": "New England Patriots",
        "buf": "Buffalo Bills",
        "crd": "Arizona Cardinals",
        "atl": "Atlanta Falcons",
        "rav": "Baltimore Ravens",
        "car": "Carolina Panthers",
        "chi": "Chicago Bears",
        "cin": "Cincinnati Bengals",
        "cle": "Cleveland Browns",
        "dal": "Dallas Cowboys",
        "den": "Denver Broncos",
        "det": "Detroit Lions",
        "gnb": "Green Bay Packers",
        "htx": "Houston Texans",
        "clt": "Indianapolis Colts",
        "jax": "Jacksonville Jaguars",
        "kan": "Kansas City Chiefs",
        "rai": "Las Vegas Raiders",
        "sdg": "Los Angeles Chargers",
        "ram": "Los Angeles Rams",
        "mia": "Miami Dolphins",
        "min": "Minnesota Vikings",
        "nor": "New Orleans Saints",
        "nyg": "New York Giants",
        "nyj": "New York Jets",
        "phi": "Philadelphia Eagles",
        "pit": "Pittsburgh Steelers",
        "sfo": "San Francisco 49ers",
        "sea": "Seattle Seahawks",
        "tam": "Tampa Bay Buccaneers",
        "oti": "Tennessee Titans",
        "was": "Washington Football Team"
    }

    rows_parsed = []
    driver = webdriver.Edge('C:/Program Files/EdgeWebDriver/msedgedriver')

    for team in team_abrvs:

        driver.get('https://www.pro-football-reference.com/teams/' + team + '/2021.htm')

        sleep(1)
        sourceCode = driver.page_source

        soup = BeautifulSoup(sourceCode, 'html.parser')
        pass_table = soup.find("table", id="passing")

        names_arr = pass_table.findAll("a")

        names = []
        for name in names_arr:
            names.append(name.contents[0])

        attrs = pass_table.findAll("td")

        i = 0
        while i <len(attrs):
            if(attrs[i].contents[0] == 'Team Total'):
                break

            parsed_data = {
                'Year': 2021,
                'Team': team_mapping[team],
                'Name': names[int(i/28)],
                'Age': attrs[i+1].contents[0],
                'Position': 'qb' if len(attrs[i+2].contents) == 0 else attrs[i+2].contents[0],
                'Games': int(attrs[i+3].contents[0]),
                'GamesStarted': int(attrs[i+4].contents[0]),
                'QBRecord': '0-0-0' if len(attrs[i+5].contents) == 0 else attrs[i+5].contents[0],
                'PassCompletions': 0 if len(attrs[i+6].contents) == 0 else int(attrs[i+6].contents[0]),
                'PassAttempts': int(attrs[i+7].contents[0]),
                'PassingYards': int(attrs[i+9].contents[0]),
                'PassingTDs': int(attrs[i+10].contents[0]),
                'PassingInterceptions': int(attrs[i+12].contents[0]),
                "LongestPass": int(attrs[i+14].contents[0]),
                'PasserRating': 0 if len(attrs[i+19].contents) == 0 else float(attrs[i+19].contents[0]),
                'QBR': 0 if len(attrs[i+20].contents) == 0 else float(attrs[i+20].contents[0]),
                'Comebacks':  0 if len(attrs[i+26].contents) == 0 else int(attrs[i+26].contents[0]),
                'GWD': 0 if len(attrs[i+27].contents) == 0 else int(attrs[i+27].contents[0])
            }

            print(parsed_data)


            i+=28

            rows_parsed.append(parsed_data)

    return rows_parsed

def mysql_insertion(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD, database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = 'INSERT INTO `PlayerSeasonPassing` (`Year`, `Team`, `Name`, `Age`, `Position`, `Games`, `GamesStarted`, ' \
          '`QBRecord`, `Completions`, `PassAttempts`, `PassingYards`, `PassingTDs`, `PassingInterceptions`' \
          ',`LongestPass`, `PasserRating`, `QBR`, `Comebacks`, `GWD`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
          '%s, %s, %s, %s, %s, %s)'

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['Year'], tuple['Team'], tuple['Name'], int(tuple['Age']), tuple['Position'], int(tuple['Games'])
                        , int(tuple['GamesStarted']), tuple['QBRecord'], int(tuple['PassCompletions']),
                               int(tuple['PassAttempts']), int(tuple['PassingYards']), int(tuple['PassingTDs']),
                                int(tuple['PassingInterceptions']), int(tuple['LongestPass']), float(tuple['PasserRating']),
                                float(tuple['QBR']), int(tuple['Comebacks']), int(tuple['GWD'])))

    db.commit()

if __name__ == '__main__':

    rows_parsed = web_scrape()
    mysql_insertion(rows_parsed)