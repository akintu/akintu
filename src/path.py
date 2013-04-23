from Queue import PriorityQueue
from region import Region
from location import Location

class Path(object):

    @staticmethod
    def has_path(start, end, open_locations, all_locations):
        return len(Path.find_path(start, end, open_locations, all_locations)) > 0

    @staticmethod
    def find_path(start, end, open_locations, all_locations):
        '''
        Pathfinding algorithm using Dijkstra's Algorithm
        '''
        if start == end:
            return []
        if start.distance(end) == 1:
            return [end]

        Q = all_locations
        dist = {}
        prev = {}
        q = PriorityQueue()
        for v in Q:
            dist[v] = float('inf')
            prev[v] = None

        dist[start] = 0
        q.put((0, start))

        while not q.empty():
            u = q.get()[1]
            if u == end or dist[u] == float('inf'):
                break

            neighbors = [u.move(dir) for dir in [2, 4, 6, 8]]
            #(self.tile_is_open(v, pid, cPane) or v == end)
            neighbors = [v for v in neighbors if v in Q and (v in open_locations or v == end)]
            for v in neighbors:
                Q.remove(v)
                alt = dist[u] + u.distance(v)
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    q.put((dist[v], v))

        path = []
        u = end

        # Follow the path backwards from destination to reconstitute the shortest path=
        while prev[u]:
            path.append(u)
            u = prev[u]

        path.reverse()
        return path