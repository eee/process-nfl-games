import re
import sys

class Spot:
    def __init__(self,match=None,special=None):
        if match:
            self.summary=match.group(0)
            self.down=int(match.group(1))
            self.distance=int(match.group(2))
            self.half=match.group(3)
            self.mark=int(match.group(4))
            self.special=None
        if special:
            self.summary=special
            self.special=special
            self.down=None
            self.distance=None
            self.half=None
            self.mark=None

    def __str__(self):
        return self.summary# + '\n' + ','.join([str(v) for v in [self.down,self.distance,self.half,self.mark,self.special]])


def extract_drives(game,t1,t2):
    down_dist_re = re.compile('(\d)-(\d+)-(\w+) (\d+)')
    drives = []
    drive = None
    for p in game:
        if t1+' at' in p:
            if drive:
                drives.append(drive)
            drive = (t1,[])
        elif t2+' at' in p:
            if drive:
                drives.append(drive)
            drive = (t2,[])
        else:
            if drive:
                a = down_dist_re.match(p)
                if a:
                    spot = Spot(match=a)
                    #remove pat tries
                    if not (spot.down == 0 and spot.distance == 0):
                        drive[1].append(Spot(match=a))
                elif 'TOUCHDOWN' in p and 'FUMBLE' not in p and 'INTERCEPT' not in p and 'TOUCHDOWN NULLIFIED' not in p:
                    drive[1].append(Spot(special='TOUCHDOWN'))
                elif 'punts' in p:
                    drive[1].append(Spot(special='PUNT'))
                elif 'extra point' in p:
                    drive[1].append(Spot(special='PAT'))
                elif 'END QUARTER 2' in p:
                    drive[1].append(Spot(special='HALFTIME'))
    return drives

def normalize(half,mark,direction):
    if half == direction:
        return 100 - mark
    else:
        return mark


def gained(half,mark,prev_half,prev_mark,direction):
    prev_pos = normalize(prev_half,prev_mark,direction)
    new_pos = normalize(half,mark,direction)
    return new_pos-prev_pos


def process_drives(drives,t1,t1t,t2,t2t):
    results = {t1:[],t2:[]}
    for d in drives:
        prev = None
        team = d[0]
        plays = d[1]
        print team
        if team == t1:
            direction = t2t
        else:
            direction = t1t
        for p in plays:
            result = None
            if not prev:
                prev = p
            else:
                if p.special:
                    if p.special == 'TOUCHDOWN':
                        result = 101
                else:
                    result = gained(p.half,p.mark,prev.half,prev.mark,direction)
                if result is not None:
                    print '('+str(prev)+') '+ str(p) + ' : ' + str(result)
                    cumresults = results[team]
                    cumresults.append(result)
                    results[team] = cumresults
                    prev = p
                else:
                    print '('+str(prev)+') '+ str(p)
    return results


def process_res(res):
    for r in res.keys():
        plays = res[r]
        success = [1 for p in plays if p>=4]
        print ' '.join([str(x) for x in [r,sum(success),'/',len(plays),sum(success)/float(len(plays))]])
            

def run_process(filename,t1,t1t,t2,t2t):
    game = open(filename).readlines()
    drives = extract_drives(game,t1,t2)
    res = process_drives(drives,t1,t1t,t2,t2t)
    process_res(res)


def main():
    if len(sys.argv) == 6:
        filename = sys.argv[1]
        t1 = sys.argv[2]
        t1t = sys.argv[3]
        t2 = sys.argv[4]
        t2t = sys.argv[5]
    else:
        print 'Usage: python process_game.py play_by_play_file_path team_1_name team_1_abbreviation team_2_name team_2_abbreviation'
        filename = './games/packers_steelers_pre'
        t1 = 'Green Bay Packers'
        t1t = 'GB'
        t2 = 'Pittsburgh Steelers'
        t2t = 'PIT'
        print 'Using defaults ' + ' '.join([filename,t1,t1t,t2,t2t])
    run_process(filename,t1,t1t,t2,t2t)


if __name__ == "__main__":
    main()
