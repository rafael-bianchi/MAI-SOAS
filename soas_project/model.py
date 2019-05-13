from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation


import random

class Grass(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
    
    def step(self):
        pass
    
    def advance(self):
        pass

class Walker(Agent):
    def __init__(self, unique_id, model, pos, heading=(1, 0)):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.pos = pos
        self.heading = heading
        self.headings = {(1, 0), (0, 1), (-1, 0), (0, -1)}
        self.destination = pos
    
    def step(self):
        while(self.destination == self.pos):
            r = random.SystemRandom()
            possible_places = list(self.model.roads.keys())
            r.shuffle(possible_places)
            self.destination = possible_places[0]

    def advance(self):
        nextPos = self.model.routes[self.pos][self.destination]["next_pos"]
        
        self.heading = (nextPos[0] - self.pos[0], nextPos[1] - self.pos[1])
        self.model.grid.move_agent(self, nextPos)
        self.pos = nextPos

class CityModel(Model):
    def __init__(self, N=2, width=20, height=10, city_map=[], roads={}, city_blocks=[], routes={}):
        super().__init__()
        self.N = N    # num of cabs
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        self.roads = roads
        self.routes = routes

        unique_id_counter = 0
        unique_id_counter = self.fill_blocks_agents(city_blocks, unique_id_counter)
        
        self.make_taxi_agents(unique_id_counter)
        self.running = True

    def fill_blocks_agents(self, city_blocks, unique_id_counter):
        for pos in city_blocks:
            agent = Grass(unique_id_counter, self, pos)
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)

            unique_id_counter = unique_id_counter + 1

        return unique_id_counter

    def make_taxi_agents(self, unique_id_counter):
        r = random.SystemRandom()
        for _ in range(self.N):
            possible_places = list(self.roads.keys())
            r.shuffle(possible_places)
            pos = possible_places[0]

            agent = Walker(unique_id_counter, self, pos, (1, 0))
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)
            unique_id_counter = unique_id_counter + 1

    def step(self):
        self.schedule.step()
