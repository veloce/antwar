#!/usr/bin/env python
import ants
import logging

logging.basicConfig(filename='../game_logs/ants.log', level=logging.DEBUG)

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        self.aims = {}

    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.hills = []
        self.unseen = []
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))

    def do_turn(self, ants):
        # track all moves, prevent collisions
        orders = {}
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if (ants.unoccupied(new_loc) and new_loc not in orders):
                ants.issue_order((loc, direction))
                orders[new_loc] = loc
                return new_loc
            else:
                return False

        target_dests = {}
        def do_move_location(loc, dest, path=None):
            # if path given use it
            if path:
                direction = path.popleft()
                # ant who has an aim will be in new_loc next turn
                new_loc = do_move_direction(loc, direction)
                if new_loc and ants.passable(new_loc):
                    self.aims[new_loc] = dest, path
                    target_dests[dest] = loc
                    return True
            # or use direction from manhattan distance
            else:
                directions = ants.manhattan_direction(loc, dest)
                for direction in directions:
                    if do_move_direction(loc, direction):
                        target_dests[dest] = loc
                        return True
            return False

        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None

        # find close food
        if len(ants.my_ants()) < 5:
            ant_dist = []
            for ant_loc in ants.my_ants():
                for food_loc in ants.food():
                    path = ants.bfs_shortest_path(ant_loc, food_loc, 10000)
                    if path:
                        dist = len(path)
                        ant_dist.append((dist, ant_loc, path))
            ant_dist.sort()
            for dist, ant_loc, path in ant_dist:
                if food_loc not in target_dests and ant_loc not in target_dests.values():
                    if do_move_location(ant_loc, food_loc, path):
                        logging.info('FEEDER (1): ' + str(ant_loc) + ' ' + str(food_loc) + ' ' + str(path))
        else:
            for food_loc in ants.food():
                ant_loc, path = ants.find_closest_ant(food_loc)
                if ant_loc and (food_loc not in target_dests) and (ant_loc not in target_dests.values()):
                    path = ants.reverse_path(path)
                    if do_move_location(ant_loc, food_loc, path):
                        logging.info('FEEDER (2): ' + str(ant_loc) + ' ' + str(food_loc) + ' ' + str(path))

        # ants who have an aim shall continue first
        for ant_loc in self.aims.keys():
            # be sure that ant is not dead nor assigned
            if (ant_loc not in ants.my_ants()) or (ant_loc in orders.values()):
                del(self.aims[ant_loc])
                continue
            dest, path = self.aims[ant_loc]
            # are we at the end of the road?
            if path:
                # got stuck somewhere? repath
                if not do_move_location(ant_loc, dest, path):
                    new_path = ants.bfs_shortest_path(ant_loc, dest)
                    if do_move_location(ant_loc, dest, new_path):
                        logging.info('REPATH: ' + str(ant_loc) + ' ' + str(dest) + ' ' + str(new_path))
                else:
                    logging.info('CONTINUE PATH: ' + str(ant_loc) + ' ' + str(dest) + ' ' + str(path))
            # in all cases delete current loc from aims
            del(self.aims[ant_loc])

        # attack hills
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
        ant_dist = []
        for hill_loc in self.hills:
            for ant_loc in iter(ants.my_ants()):
                if ant_loc not in orders.values():
                    dist = ants.manhattan_distance(ant_loc, hill_loc)
                    ant_dist.append((dist, ant_loc))
        ant_dist.sort()
        for dist, ant_loc in ant_dist:
            do_move_location(ant_loc, hill_loc)

        # explore unseen areas
        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.unseen.remove(loc)
        for ant_loc in iter(ants.my_ants()):
            if ant_loc not in orders.values():
                unseen_dist = []
                for unseen_loc in self.unseen:
                    dist = ants.manhattan_distance(ant_loc, unseen_loc)
                    unseen_dist.append((dist, unseen_loc))
                unseen_dist.sort()
                for dist, unseen_loc in unseen_dist:
                    if do_move_location(ant_loc, unseen_loc):
                        logging.info('SCOUT: ' + str(ant_loc) + ' ' + str(unseen_loc))
                        break

        # unblock own hill
        for hill_loc in ants.my_hills():
            if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                for direction in ('s','e','w','n'):
                    if do_move_direction(hill_loc, direction):
                        break

        # track idle ants
        for ant in iter(ants.my_ants()):
            if ant not in orders.values():
                logging.info('IDLE: ' + str(loc))


if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        ants.Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
