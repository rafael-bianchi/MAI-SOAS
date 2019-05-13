def shortest_path(city_model, start, goal):
    try:
        return next(bfs_paths(city_model, start, goal))
    except StopIteration:
        return None

def bfs_paths(city_model, start, goal):
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in city_model[vertex] - set(path):
            if next == goal:
                yield path + [next]
            else:
                queue.append((next, path + [next]))

def getShortestPaths(city_roads):
    directions = {}
    roads_pos = list(city_roads.keys()) 

    for i in range(0, len(roads_pos)):
        pos_from = roads_pos[i]
        for j in range(i+1, len(roads_pos)):
            pos_to = roads_pos[j]

            path = shortest_path(city_roads, pos_from, pos_to)

            if(len(path) > 0):
                if(pos_from not in directions):
                    directions[pos_from] = {}
                
                if(pos_to not in directions):
                    directions[pos_to] = {}

                directions[pos_from][pos_to] = {"next_pos": path[1], "distance": len(path) - 1}
                directions[pos_to][pos_from] = {"next_pos": path[-2], "distance": len(path) - 1}

    return directions