from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from .utils import getShortestPaths

import random

class Road(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

class Grass(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

class Walker(Agent):
    def __init__(self, unique_id, model, pos, heading=(1, 0)):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.pos = pos
        self.heading = heading
        self.headings = {(1, 0), (0, 1), (-1, 0), (0, -1)}
    
    def step(self):
        self.move()

    def move(self):
        possible_steps = self.city_roads[self.pos]
        
        r = random.SystemRandom()

        r.shuffle(possible_steps)
        
        pos = possible_steps[0]

        self.model.grid.move_agent(self, pos)
        self.pos = pos

class CityModel(Model):
    def __init__(self, N=2, width=20, height=10, city_map=[]):
        super().__init__()
        self.N = N    # num of agents
        self.headings = ((1, 0), (0, 1), (-1, 0), (0, -1))  # tuples are fast
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        
        unique_id_counter = 0
        unique_id_counter = self.create_map(city_map, width, height, unique_id_counter)
        
        self.make_walker_agents(unique_id_counter)
        self.running = True

    def create_map(self, city_map, width, height, unique_id_counter):
        self.city_roads = {}
        for idx_line, line in enumerate(city_map):
           for idx_col, cell in enumerate(line):
                agent = None
                pos = (idx_line, (height - 1) - idx_col)
                if(cell == '1'):
                    agent = Grass(unique_id_counter, self, pos)
                elif(cell == '0'):
                    agent = Road(unique_id_counter, self, pos)
                    neighbors = set()

                    for next_pos in [(0,-1), (-1, 0), (1,0), (0,1)]:
                        node_position = (pos[0] + next_pos[0], pos[1] + next_pos[1])
                        if node_position[0] > width - 1 or node_position[0] < 0 or node_position[1] > height - 1 or node_position[1] < 0:
                            continue

                        # Make sure walkable terrain
                        if city_map[node_position[0]][node_position[1]] != '0':
                            continue

                        neighbors.add(node_position)
                    
                    self.city_roads[pos] = neighbors

                #print(f'Adding {type(agent)} on {pos}')
                self.schedule.add(agent)
                self.grid.place_agent(agent, pos)

                unique_id_counter = unique_id_counter + 1

        self.shortest_paths = getShortestPaths(self.city_roads)

        return unique_id_counter
    def make_walker_agents(self, unique_id_counter):
        for _ in range(self.N):
            while True:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                pos = (x,y)

                this_cell = self.grid.get_cell_list_contents([pos])
                road = [obj for obj in this_cell if isinstance(obj, Road)]

                if (len(road) > 0):
                    print(f'Adding agent on {pos}')
                    heading = self.random.choice(self.headings)
                    agent = Walker(unique_id_counter, self, pos, heading)
                    self.schedule.add(agent)
                    self.grid.place_agent(agent, pos)
                    unique_id_counter = unique_id_counter + 1
                    break
            #agents = self.grid[x][y]

    def step(self):
        self.schedule.step()
