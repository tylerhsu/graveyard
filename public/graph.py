import csv, settings
from copy import deepcopy
from decimal import Decimal

DATA_FILE = settings.APP_ROOT + '/public/graph_data.csv'

def main():
    targets = ['Hawkins Cemetery']
    speed = 10
    bonuses = {
        'Gil Gal Cemetery': 60,
    }
    return run(targets, bonuses, speed)

def run(target_ids, bonuses, speed, start_id='Start Finish'):
    graph = build_graph(start_id, target_ids, speed, bonuses)

    results = find_routes(graph)
    most_direct = find_routes(graph, ignore_bonuses=True)[0]
    return {
        'routes': [serialize(r) for r in results],
        'most_direct': serialize(most_direct),
    }

def serialize(result):
    route = result['route']
    cost = result['cost']
    cost_without_bonuses = result['cost_without_bonuses']
    distance = result['distance']
    return {
        'nodes': [node.serialize() for node in traverse(route)],
        'cost': str(round(cost, 2)),
        'cost_without_bonuses': str(round(cost_without_bonuses, 2)),
        'distance': str(round(distance, 2)),
    }

def traverse(route):
    route_copy = []
    for node in route:
        node_copy = deepcopy(node)
        if node.id in [n.id for n in route_copy]:
            node_copy.bonus = 0
        route_copy.append(node_copy)
    return route_copy
            

def find_routes(graph, ignore_bonuses=False):
    start = graph.start.id
    targets = [node.id for node in graph.targets()]
    choices = []
    for permutation in permutations(targets):
        waypoints = [start] + permutation + [start]
        route = [graph.get(start)]
        cost = 0
        for n in range(len(waypoints)-1):
            leg, leg_cost = graph.route(waypoints[n], waypoints[n+1], ignore_bonuses_of=route, ignore_all_bonuses=ignore_bonuses)
            route += leg[1:]
            cost += leg_cost
        choices.append({
            'route': route,
            'cost': cost,
            'cost_without_bonuses': graph.total_cost(route, use_bonus=False),
            'distance': graph.total_distance(route),
        })

    return sorted(choices, key=lambda c: c['cost'])

def permutations(sequence):
    if len(sequence) == 1:
        return [sequence]
    perms = []
    for x in sequence:
        i = sequence.index(x)
        sequence_without_x = sequence[:i] + sequence[i+1:]
        perms += [[x] + p for p in permutations(sequence_without_x)]
    return perms

def get_locations():
    with open(DATA_FILE, 'rb') as f:
        reader = csv.DictReader(f)
        locations = reader.fieldnames[1:]
    return locations

def build_graph(start_id, target_ids, speed, bonuses={}):
    with open(DATA_FILE, 'rb') as f:
        reader = csv.DictReader(f)
        locations = reader.fieldnames[1:]
        graph = Graph([ Node(location) for location in locations ], speed)
        for row in reader:
            for key, value in row.items():
                if value and key != 'name':
                    graph.connect(row['name'], key, distance=value)

    graph.start = graph.get(start_id)
    for target_id in target_ids:
        graph.get(target_id).is_target = True

    graph.set_bonuses(bonuses)

    return graph

class Graph(object):
    def __init__(self, nodes, speed):
        self.speed = speed
        self.start = None
        self._nodes = {}
        for node in nodes:
            self._nodes[node.id] = node

    def targets(self):
        return [node for node in self._nodes.values() if node.is_target]

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

    def route(self, start_id, dest_id, ignore_bonuses_of=[], ignore_all_bonuses=False):
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
                return backtrack(dest), cost
            explored.append(node)
            for neighbor in node.neighbors():
                if not neighbor in explored:
                    use_bonus = neighbor not in ignore_bonuses_of and not ignore_all_bonuses
                    new_cost = cost + self.cost(node, neighbor, use_bonus=use_bonus)
                    if not frontier.contains(neighbor):
                        frontier.put(neighbor, new_cost)
                        came_from[neighbor] = node
                    elif frontier.get_cost(neighbor) > new_cost:
                        frontier.set_cost(neighbor, new_cost)
                        came_from[neighbor] = node
        return None

    def cost(self, node, neighbor, use_bonus=True):
        distance = self.distance(node, neighbor)
        cost = Decimal(distance) / Decimal(self.speed)
        if use_bonus:
            cost -= Decimal(neighbor.bonus) / Decimal(60)
        return cost

    def distance(self, node, neighbor):
        try:
            return node._neighbors[neighbor]
        except KeyError:
            raise Exception("Not neighbors")

    def total_cost(self, route, use_bonus=True):
        if len(route) < 2:
            return 0
        cost = 0
        for n in range(len(route) - 1):
            cost += self.cost(route[n], route[n+1], use_bonus=use_bonus)
        return cost

    def total_distance(self, route):
        if len(route) < 2:
            return 0
        distance = 0
        for n in range(len(route) - 1):
            distance += Decimal(self.distance(route[n], route[n+1]))
        return distance

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
        return { "id": str(self.id),
                 "bonus": str(self.bonus),
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
