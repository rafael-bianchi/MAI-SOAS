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

def getRoads(city_map, height, width):
    city_roads = {}
    city_blocks = []
    passenger_blocks = {}

    for idx_line, line in enumerate(city_map):
        for idx_col, cell in enumerate(line):
            pos = (idx_line, (height - 1) - idx_col)
            if (cell == '0'):
                neighbors = set()
                for next_pos in [(0,-1), (-1, 0), (1,0), (0,1)]:
                    node_position = (pos[0] + next_pos[0], pos[1] + next_pos[1])
                    
                    if node_position[0] > width - 1 or node_position[0] < 0 or \
                       node_position[1] > height - 1 or node_position[1] < 0:
                        continue

                    if city_map[node_position[0]][node_position[1]] != '0':
                        continue

                    neighbors.add(node_position)
                
                city_roads[pos] = neighbors
            else:
                blocks_around = []
                for next_pos in [(0,-1), (-1, 0), (1,0), (0,1)]:
                    node_position = (pos[0] + next_pos[0], pos[1] + next_pos[1])
                    
                    if node_position[0] > width - 1 or node_position[0] < 0 or \
                        node_position[1] > height - 1 or node_position[1] < 0:
                        continue

                    if city_map[node_position[0]][node_position[1]] != '0':
                        continue

                    blocks_around.append(node_position)
                
                isCenterBlock = len(blocks_around) == 0 
                city_blocks.append((pos, isCenterBlock))
                
                if(len(blocks_around) == 1):
                    passenger_blocks[pos]= blocks_around[0]
                
    routes = getShortestPaths(city_roads)

    return city_roads, city_blocks, passenger_blocks, routes