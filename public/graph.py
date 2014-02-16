import csv
from decimal import Decimal

def main():
    # inputs
    start = 'a'
    targets = ['Callahan Cemetery', 'Elkinsville Cemetery', 'Cornett Cemetery']
    speed = 1
    graph = build_graph(speed, targets)
    for node in graph._nodes.values():
        print '%s: %s' % (node, node._neighbors)
    # return run(start, targets, bonuses, speed)

def run(start_id, target_ids, bonuses, speed):
    graph = build_graph(speed, target_ids)
    results = find_routes(graph, start_id, target_ids, bonuses)
    return serialize(results)

def serialize(results):
    obj = {
        'routes': [],
    }
    for route, cost in results:
        obj['routes'].append({
                'nodes': [node.serialize() for node in route],
                'cost': float(cost),
        })
    return obj

def find_routes(graph, start, targets, bonuses):
    choices = []
    for permutation in permutations(targets):
        graph.set_bonuses(bonuses)
        waypoints = [start] + permutation + [start]
        route = [graph.get(start)]
        cost = 0
        for n in range(len(waypoints)-1):
            leg = graph.route(waypoints[n], waypoints[n+1])
            route += leg[1:]
            cost += graph.total_cost(leg)

            # bonuses for visited nodes are now used up
            for node in leg:
                node.bonus = 0
        choices.append((route, cost))

    # restore bonuses to their initial state
    graph.set_bonuses(bonuses)

    best = sorted(choices, key=lambda c: c[1])[0]

    # Return list of all results whose costs are equal to the best one
    return [c for c in choices if c[1] == best[1]]

def permutations(sequence):
    if len(sequence) == 1:
        return [sequence]
    perms = []
    for x in sequence:
        i = sequence.index(x)
        sequence_without_x = sequence[:i] + sequence[i+1:]
        perms += [[x] + p for p in permutations(sequence_without_x)]
    return perms

def build_graph(speed, targets=[]):
    with open('/var/www/graveyard/public/graph_data.csv', 'rb') as f:
        reader = csv.DictReader(f)
        locations = reader.fieldnames[1:]
        graph = Graph([ Node(location) for location in locations ], speed)
        for row in reader:
            for key, value in row.items():
                if value and key != 'name':
                    graph.connect(row['name'], key, distance=value)

    for target_id in targets:
        graph.get(target_id).is_target = True

    return graph

class Graph(object):
    def __init__(self, nodes, speed):
        self.speed = speed
        self._nodes = {}
        for node in nodes:
            self._nodes[node.id] = node

    def set_bonuses(self, bonuses):
        for node_id, bonus in bonuses.items():
            self._nodes[node_id].bonus = bonus

    def get(self, id):
        return self._nodes[id]

    def connect(self, source_id, dest_id, distance, bidirectional=True):
        source = self.get(source_id)
        dest = self.get(dest_id)
        source.connect(dest, distance)
        if bidirectional:
            dest.connect(source, distance)

    def route(self, start_id, dest_id):
        def backtrack(node):
            if came_from.get(node) is None:
                return [node]
            return backtrack(came_from.get(node)) + [node]
        start = self.get(start_id)
        dest = self.get(dest_id)
        came_from = {}
        explored = []
        frontier = PriorityQueue()
        frontier.put(start, 0)
        while not frontier.empty():
            node, cost = frontier.get()
            if node == dest:
                return backtrack(dest)
            explored.append(node)
            for neighbor in node.neighbors():
                if not neighbor in explored:
                    new_cost = cost + self.cost(node, neighbor)
                    if not frontier.contains(neighbor):
                        frontier.put(neighbor, new_cost)
                        came_from[neighbor] = node
                    elif frontier.get_cost(neighbor) > new_cost:
                        frontier.set_cost(neighbor, new_cost)
                        came_from[neighbor] = node
        return None

    def cost(self, node, neighbor):
        try:
            distance = node._neighbors[neighbor]
        except KeyError:
            raise Exception("Not neighbors")
        return Decimal(distance) / Decimal(self.speed) + Decimal(neighbor.bonus)

    def total_cost(self, route):
        if len(route) < 2:
            return 0
        cost = 0
        for n in range(len(route) - 1):
            cost += self.cost(route[n], route[n+1])
        return cost

class Node(object):
    def __init__(self, id, bonus=0):
        self.id = id
        self.bonus = bonus
        self.is_target = False
        self._neighbors = {}

    def __repr__(self):
        return '<Node: %s>' % self.id

    def connect(self, dest, distance):
        self._neighbors[dest] = distance

    def neighbors(self):
        return self._neighbors.keys()

    def serialize(self):
        return { "id": self.id,
                 "bonus": self.bonus,
                 "is_target": self.is_target,
                 }

class PriorityQueue(object):
    def __init__(self):
        self._queue = []

    def __repr__(self):
        return self._queue.__repr__()

    def put(self, item, cost):
        self._queue.append([item, cost])

    def get(self):
        item = sorted(self._queue, key=lambda x: x[1])[0]
        self._queue.remove(item)
        return item

    def empty(self):
        return len(self._queue) == 0

    def get_cost(self, item):
        x = self._search(item)
        if x:
            return x[1]

    def set_cost(self, item, cost):
        x = self._search(item)
        if x:
            x[1] = cost
        else:
            raise IndexError

    def contains(self, item):
        return self._search(item) is not None

    def _search(self, item):
        for x in self._queue:
            if x[0] == item:
                return x
        return None

if __name__ == '__main__':
    print main()
