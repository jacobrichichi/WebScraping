import requests
from bs4 import BeautifulSoup
import pymysql
import DBInfo


def web_scraping():
    page = requests.get('https://www.pro-football-reference.com/years/2021/')
    soup = BeautifulSoup(page.content, 'html.parser')

    team_stats_table = str(soup.find("div", {"id": 'all_team_stats'}))

    split_up = team_stats_table.split('tbody')[1]

    each_row = split_up.split('ranker')

    rows_parsed = []

    for row in each_row[1:]:
        firstidx = row.index("htm\">") + 5
        secondidx = row.index("</a>")
        teamName = row[firstidx: secondidx]

        firstidx = row.index("\"g\" >") + 5
        secondidx = row.index("</td><td class=\"right \" data-stat=\"po")

        gamesPlayed = int(row[firstidx: secondidx])

        firstidx = row.index("\"points\" >") + 10
        secondidx = row.index("</td><td class=\"right \" data-stat=\"total_yards\" >")

        points = int(row[firstidx: secondidx])

        firstidx = row.index("\"total_yards\" >") + 15
        secondidx = row.index("</td><td class=\"right \" data-stat=\"plays_offense\" >")

        yards = int(row[firstidx: secondidx])

        firstidx = row.index("\"turnovers\" >") + 13
        secondidx = row.index("</td><td class=\"right \" data-stat=\"fumbles_lost\" >")

        turnovers = int(row[firstidx: secondidx])

        firstidx = row.index("\"pass_yds\" >") + 12
        secondidx = row.index("</td><td class=\"right \" data-stat=\"pass_td\" >")

        passYds = int(row[firstidx: secondidx])

        firstidx = row.index("\"pass_td\" >") + 11
        secondidx = row.index("</td><td class=\"right \" data-stat=\"pass_int\" >")

        passTds = int(row[firstidx: secondidx])

        firstidx = row.index("\"pass_int\" >") + 12
        secondidx = row.index("</td><td class=\"right \" data-stat=\"pass_net_yds_per_att\" >")

        ints = int(row[firstidx: secondidx])

        firstidx = row.index("\"rush_yds\" >") + 12
        secondidx = row.index("</td><td class=\"right \" data-stat=\"rush_td\" >")

        rushYDs = int(row[firstidx: secondidx])

        firstidx = row.index("\"rush_td\" >") + 11
        secondidx = row.index("</td><td class=\"right \" data-stat=\"rush_yds_per_att\" >")

        rushTDs = int(row[firstidx: secondidx])

        parsed_data = {
            "TeamName": teamName,
            "Games": gamesPlayed,
            "Points": points,
            "Yards": yards,
            "TOs": turnovers,
            "PassYards": passYds,
            "PassTDs": passTds,
            "INTs": ints,
            "RushYards": rushYDs,
            "RushTDs": rushTDs
        }

        rows_parsed.append(parsed_data)

    return rows_parsed

def mysql_insertion(tuples):
    db = pymysql.connect(host=DBInfo.DB_HOST, user=DBInfo.DB_USER, password=DBInfo.DB_PASSWORD, database=DBInfo.DB_NAME)
    cursor = db.cursor()

    sql = 'INSERT INTO `TeamStats` (`TeamName`, `Points`, `Games`, `Yards`, `TOs`, ' \
          '`PassYards`, `PassTDs`, `INTs`, `RushYards`, `RushTDs`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

    for tuple in tuples:
        res = cursor.execute(sql, (tuple['TeamName'], int(tuple['Points']), int(tuple['Games']), int(tuple['Yards'])
                             , int(tuple['TOs']), int(tuple['PassYards']), int(tuple['PassTDs']), int(tuple['INTs']), int(tuple['RushYards']), int(tuple['RushTDs'])))

        print('hey')

    db.commit()

if __name__ == '__main__':

    rows_parsed = web_scraping()
    mysql_insertion(rows_parsed)




