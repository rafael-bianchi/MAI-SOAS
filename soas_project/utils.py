class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, pos=None):
        self.parent = parent
        self.pos = pos

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.pos == other.pos

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

def getNeighbors(city_model, pos):
        children = []
        for c in city_model.iter_neighbors(pos, False, False, 1):
            cell_to_contents = city_model.get_cell_list_contents([c.pos])
            
            road = [obj for obj in cell_to_contents if type(obj).__qualname__ == 'Road']

            if (len(road) <= 0):
                continue

            children.append(c.pos)
        
        return set(children)

def getShortestPaths(city_roads):
    debug_count = 0
    directions = {}
    roads_pos = list(city_roads.keys()) 

    for i in range(0, len(roads_pos)):
        pos_from = roads_pos[i]
        for j in range(i+1, len(roads_pos)):
            pos_to = roads_pos[j]

            #print(f'Looking for path {pos_from} to {pos_to}')

            debug_count = debug_count + 1

            if(debug_count % 1000 == 0):
                print (debug_count)

            path = shortest_path(city_roads, pos_from, pos_to)#astar(city_model, pos_from, pos_to)

            if(len(path) > 0):
                if(pos_from not in directions):
                    directions[pos_from] = {}
                
                if(pos_to not in directions):
                    directions[pos_to] = {}

                directions[pos_from][pos_to] = {"next_pos": path[1], "distance": len(path) - 1}
                directions[pos_to][pos_from] = {"next_pos": path[-2], "distance": len(path) - 1}
                debug_count = debug_count + 1

    # for cell_from, row_from, col_from in city_roads.coord_iter():
    #     pos_from = (row_from,col_from)
        
    #     cell_from_contents = city_roads.get_cell_list_contents([pos_from])
        
    #     road = [obj for obj in cell_from_contents if type(obj).__qualname__ == 'Road']
        
    #     if (True):#(len(road)> 0):
    #         for cell_to, row_to, col_to in city_roads.coord_iter():
    #             debug_count = debug_count + 1
    #             #pos_to = (row_to, col_to)
                
    #             # if((pos_to == pos_from) or ((pos_from in directions and pos_to in directions[pos_from]) and
    #             #                             (pos_from in directions and pos_from in directions[pos_to]))):
    #             #     continue

    #             # cell_to_contents = city_model.get_cell_list_contents([pos_to])
                
    #             # road_to = [obj for obj in cell_to_contents if type(obj).__qualname__ == 'Road']

    #             # if (len(road_to) > 0):
    #             #     if (debug_count % 100 == 1):
    #             #         print(f'Looking for path {pos_from} to {pos_to}')
    #             #     path = shortest_path(city_model, pos_from, pos_to)#astar(city_model, pos_from, pos_to)

    #             #     if(len(path) > 0):
    #             #         if(pos_from not in directions):
    #             #             directions[pos_from] = {}
                        
    #             #         if(pos_to not in directions):
    #             #             directions[pos_to] = {}

    #             #         directions[pos_from][pos_to] = {"next_pos": path[1], "distance": len(path) - 1}
    #             #         directions[pos_to][pos_from] = {"next_pos": path[-2], "distance": len(path) - 1}
    #             #         debug_count = debug_count + 1

                        
    return directions

def astar(city_model, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.pos)
                current = current.parent
            return path[::-1] # Return reversed path


        children = []
        for c in city_model.iter_neighbors(current_node.pos, False, False, 1):
            cell_to_contents = city_model.get_cell_list_contents([c.pos])
            
            road = [obj for obj in cell_to_contents if type(obj).__qualname__ == 'Road']

            if (len(road) <= 0):
                continue

            # Create new node
            new_node = Node(current_node, c.pos)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.pos[0] - end_node.pos[0]) ** 2) + ((child.pos[1] - end_node.pos[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)