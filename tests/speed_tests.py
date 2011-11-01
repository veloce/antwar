from antwar import ants
from collections import defaultdict

ANTS = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4
UNSEEN = -5
MAP_OBJECT = '?%*.!'

def parse_map(map_text):
    """ Parse the map_text into a more friendly data structure """
    ant_list = None
    hill_list = []
    hill_count = defaultdict(int)
    width = height = None
    water = []
    food = []
    ants = defaultdict(list)
    hills = defaultdict(list)
    row = 0
    score = None
    hive = None
    num_players = None

    for line in map_text.split('\n'):
        line = line.strip()

        # ignore blank lines and comments
        if not line or line[0] == '#':
            continue

        key, value = line.split(' ', 1)
        key = key.lower()
        if key == 'cols':
            width = int(value)
        elif key == 'rows':
            height = int(value)
        elif key == 'players':
            num_players = int(value)
            if num_players < 2 or num_players > 10:
                raise Exception("map",
                                "player count must be between 2 and 10")
        elif key == 'score':
            score = list(map(int, value.split()))
        elif key == 'hive':
            hive = list(map(int, value.split()))
        elif key == 'm':
            if ant_list is None:
                if num_players is None:
                    raise Exception("map",
                                    "players count expected before map lines")
                ant_list = [chr(97 + i) for i in range(num_players)]
                hill_list = list(map(str, range(num_players)))
                hill_ant = [chr(65 + i) for i in range(num_players)]
            if len(value) != width:
                raise Exception("map",
                                "Incorrect number of cols in row %s. "
                                "Got %s, expected %s."
                                %(row, len(value), width))
            for col, c in enumerate(value):
                if c in ant_list:
                    ants[ant_list.index(c)].append((row,col))
                elif c in hill_list:
                    hills[hill_list.index(c)].append((row,col))
                    hill_count[hill_list.index(c)] += 1
                elif c in hill_ant:
                    ants[hill_ant.index(c)].append((row,col))
                    hills[hill_ant.index(c)].append((row,col))
                    hill_count[hill_ant.index(c)] += 1
                elif c == MAP_OBJECT[FOOD]:
                    food.append((row,col))
                elif c == MAP_OBJECT[WATER]:
                    water.append((row,col))
                elif c != MAP_OBJECT[LAND]:
                    raise Exception("map",
                                    "Invalid character in map: %s" % c)
            row += 1

    if score and len(score) != num_players:
        raise Exception("map",
                        "Incorrect score count.  Expected %s, got %s"
                        % (num_players, len(score)))
    if hive and len(hive) != num_players:
        raise Exception("map",
                        "Incorrect score count.  Expected %s, got %s"
                        % (num_players, len(score)))

    if height != row:
        raise Exception("map",
                        "Incorrect number of rows.  Expected %s, got %s"
                        % (height, row))


    return {
        'size':        (height, width),
        'num_players': num_players,
        'hills':       hills,
        'ants':        ants,
        'food':        food,
        'water':       water
    }


def setup_ant_map(f):
    file = open(f)
    map_text = file.read()

    map_data = parse_map(map_text)

    file.close()

    Ants = ants.Ants()
    Ants.map = []

    Ants.rows, Ants.cols = map_data['size']

    Ants.map = [[LAND]*Ants.cols for _ in range(Ants.rows)]

    # initialize water
    for row, col in map_data['water']:
        Ants.map[row][col] = WATER

    return Ants



Ants = setup_ant_map('../tools/maps/maze/maze_02p_01.map')

start = (21,6)
end = (40, 32)
# print str(start) +' ', Ants.map[start[0]][start[1]]
# print str(end) +' ', Ants.map[end[0]][end[1]]

def test01():
    print 'testing BFS path finding for 50 ants with no depth limit:'
    for i in range(1, 50):
        result = Ants.bfs_shortest_path((21,6), (40,32), None)

def test03():
    print 'testing BFS path finding for 50 ants with depth limit to 200:'
    for i in range(1, 50):
        result = Ants.bfs_shortest_path((21,6), (40,32), 200)

def test04():
    print 'testing BFS path finding for 100 ants with depth limit to 200:'
    for i in range(1, 100):
        result = Ants.bfs_shortest_path((21,6), (40,32), 200)

test01()
