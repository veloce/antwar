import unittest
from antwar import ants

class PathFindingTestCase(unittest.TestCase):

    def setup_ant_map(self, map_string):
        Ants = ants.Ants()

        Ants.map = []

        for y, line in enumerate(map_string.split('\n')):
            row = []
            for x, square in enumerate(line.strip()):
                if square == '.':
                    row.append(ants.LAND)
                elif square == '%':
                    row.append(ants.WATER)
            Ants.map.append(row)

        Ants.rows = y+1
        Ants.cols = x+1

        return Ants



class TestBFS(PathFindingTestCase):

    def test_shortest_path(self):
        a = self.setup_ant_map("""%%%%%%
                              %..%.%
                              %.%%.%
                              %.....
                              ...%%.
                              %.%%%%""")

        self.assertEqual(a.bfs_shortest_path((1,1), (4,1)), ['s', 's', 's'])
        self.assertEqual(a.bfs_shortest_path((1,1), (1,4)), ['s', 's', 'e', 'e', 'e', 'n', 'n'])
        self.assertEqual(a.bfs_shortest_path((4,1), (4,5)), ['w', 'w'])

    def test_find_closest(self):
        a = self.setup_ant_map("""%%%%%%
                              %..%.%
                              %.%%.%
                              %.....
                              ...%%.
                              %.%%%%""")

        self.assertEqual(a.find_closest((1,1), set([(4,2), (1,4)])), ((4,2), ['w', 'n', 'n', 'n']))

if __name__ == '__main__':
    unittest.main()
