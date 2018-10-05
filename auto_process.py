import subprocess
import sys
import os.path


def download_game(game_link):
    team_results = {}
    game_sub = game_link.split('/')[-1].split('?')[0]
    filename = "./games/" + game_sub
    if not os.path.isfile(filename):
        download_game_command = "google-chrome --headless --disable-gpu --dump-dom " + game_link + " > " + filename
        print download_game_command
        output = subprocess.check_output(download_game_command,shell=True)

    gamelines = open(filename).readlines()
    for l in gamelines:
        if l.strip().startswith('__INITIAL_DATA__'):
            gamedata = eval(''.join(l.split('=')[1:]).strip().rstrip(';').replace('true','True').replace('false','False').replace('null','None'))
            #print gamedata['instance']['gameDetails'].keys()
            #print gamedata['instance']['gameDetails']['homeTeam']
            #print gamedata['instance']['gameDetails']['visitorTeam']
            #print gamedata['instance']['gameDetails']['stadium']
            #print gamedata['instance']['gameDetails']['homePointsTotal']
            #print gamedata['instance']['gameDetails']['visitorPointsTotal']
            plays = gamedata['instance']['gameDetails']['plays']
            for play in plays:
                if play['playType'] not in ['GAME_START','KICK_OFF','TIMEOUT','END_QUARTER','END_GAME']:
                    team_results = process_play(play,team_results)
    process_res(team_results)

def process_play(play,team_results):
    #print play
    stats = play['playStats']
    desc = play['playDescription']
    #print desc
    special = play['specialTeamsPlay']
    if not special:
        poss = play['possessionTeam']['abbreviation']
        start = play['yardLine']
        end = play['endYardLine']
        score = play['scoringPlayType']
        scoringTeam = play['scoringTeam']
        yards = play['yards']
        result = yards
        if 'INTERCEPTED' in desc:
            result = -1
        if score == 'TD' and scoringTeam['abbreviation'] == poss:
            result = 101
        tr = team_results.get(poss,[])
        tr.append(yards)
        team_results[poss]=tr
    return team_results

    

def process_res(res):
    for r in res.keys():
        plays = res[r]
        success = [1 for p in plays if p>=4]
        print ' '.join([str(x) for x in [r,sum(success),'/',len(plays),sum(success)/float(len(plays))]])

def main():
    if len(sys.argv) == 2:
        game_link = sys.argv[1]
        download_game(game_link)
    else:
        print "Usage: python auto_process.py https://www.nfl.com/gamecenter/2018093003/2018/REG4/bills@packers?icampaign=GC_schedule_rr"

if __name__ == "__main__":
    main()
