import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

import DBInfo


def scrape_rush_recieve():
    team_abrvs = ['nwe', 'buf', 'mia', 'nyj', 'cin', 'rav', 'pit', 'cle',
                  'oti', 'clt', 'htx', 'jax', 'kan', 'sdg', 'rai', 'den',
                  'dal', 'phi', 'was', 'nyg', 'gnb', 'min', 'chi', 'det',
                  'tam', 'nor', 'atl', 'car', 'ram', 'crd', 'sfo', 'sea']

    team_mapping = {
        "nwe": "New England Patriots",
        "buf": "Buffalo Bills",
        "crd":"Arizona Cardinals",
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
        rushing_receiving = soup.find("table", id="rushing_and_receiving")



        names_arr = rushing_receiving.findAll("a")

        names = []
        for name in names_arr:
            names.append(name.contents[0])

        attrs = rushing_receiving.findAll("td")


        i = 0
        while i < len(attrs):
            if (attrs[i].contents[0] == 'Team Total'):
                break

            parsed_data = {
                'Year': 2021,
                'Team': team_mapping[team],
                'Name': names[int(i / 27)],
                'Age': attrs[i + 1].contents[0],
                'Position': 'rb' if len(attrs[i + 2].contents) == 0 else attrs[i + 2].contents[0],
                'Games': int(attrs[i + 3].contents[0]),
                'GamesStarted': int(attrs[i + 4].contents[0]),
                'RushAttempts': 0 if len(attrs[i + 5].contents) == 0 else int(attrs[i + 5].contents[0]),
                'RushYards': int(attrs[i + 6].contents[0]),
                'RushTDs': int(attrs[i + 7].contents[0]),
                'RushLong': int(attrs[i + 8].contents[0]),
                'Targets': 0 if len(attrs[i + 12].contents) == 0 else int(attrs[i + 12].contents[0]),
                "Receptions": 0 if len(attrs[i + 13].contents) == 0 else int(attrs[i + 13].contents[0]),
                'ReceivingYards': 0 if len(attrs[i + 14].contents) == 0 else int(attrs[i + 14].contents[0]),
                'ReceivingTDs': 0 if len(attrs[i + 16].contents) == 0 else int(attrs[i + 16].contents[0]),
                'ReceivingLong': 0 if len(attrs[i + 17].contents) == 0 else int(attrs[i + 17].contents[0]),
                'Fumbles': 0 if len(attrs[i + 26].contents) == 0 else int(attrs[i + 26].contents[0])
            }

            print(parsed_data)
            i += 27

            rows_parsed.append(parsed_data)

    return rows_parsed

def mysql_insertion(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD, database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = 'INSERT INTO `PlayerSeasonRushReceive` (`Year`, `Team`, `Name`, `Age`, `Position`, `Games`, `GamesStarted`, ' \
          '`RushAttempts`, `RushYards`, `RushTDs`, `RushLong`, `Targets`, `Receptions`' \
          ',`ReceivingYards`, `ReceivingTDs`, `ReceivingLong`, `Fumbles`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
          '%s, %s, %s, %s, %s)'

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['Year'], tuple['Team'], tuple['Name'], int(tuple['Age']), tuple['Position'], int(tuple['Games'])
                        , int(tuple['GamesStarted']), int(tuple['RushAttempts']), int(tuple['RushYards']),
                               int(tuple['RushTDs']), int(tuple['RushLong']), int(tuple['Targets']),
                                int(tuple['Receptions']), int(tuple['ReceivingYards']), int(tuple['ReceivingTDs']),
                                int(tuple['ReceivingLong']), int(tuple['Fumbles'])))

    db.commit()

if __name__ == '__main__':
    data = scrape_rush_recieve()
    mysql_insertion(data)
