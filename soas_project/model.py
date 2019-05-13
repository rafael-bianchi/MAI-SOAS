from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation


import random

class Passenger(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
    
    def step(self):
        pass
    
    def advance(self):
        pass


class Grass(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.time_waiting = 0

    def step(self):
        self.time_waiting = self.time_waiting + 1
    
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
        self.lookForPassengers()
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
    def __init__(self, N=2, PassengerPooling=.5, PassengerPopulation=.2, PassengerBlocks=[], width=20, height=10, city_map=[], roads={}, city_blocks=[], routes={}):
        super().__init__()
        self.N = N    # num of cabs
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        self.roads = roads
        self.routes = routes
        self.passenger_blocks = PassengerBlocks
        self.unique_id_counter = 0
        self.city_blocks = city_blocks
        self.passenger_population = PassengerPopulation
        
        self.fill_blocks_agents()

        self.make_taxi_agents()
        self.addPassengers()

        self.running = True

    def fill_blocks_agents(self):
        for pos in self.city_blocks:
            agent = Grass(self.unique_id_counter, self, pos)
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)

            self.unique_id_counter = self.unique_id_counter + 1

    def make_taxi_agents(self):
        r = random.SystemRandom()
        for _ in range(self.N):
            possible_places = list(self.roads.keys())
            r.shuffle(possible_places)
            pos = possible_places[0]

            agent = Walker(self.unique_id_counter, self, pos, (1, 0))
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)
            self.unique_id_counter = self.unique_id_counter + 1

    def step(self):
        self.addPassengers()
        self.schedule.step()

    def addPassengers(self):
        passengers_waiting = [agent.pos for agent in self.schedule.agents if isinstance(agent, Passenger)]
        
        free_spot = list(set(self.passenger_blocks) - set(passengers_waiting))
        r = random.SystemRandom()
        r.shuffle(free_spot)

        while(len(free_spot)> 0 and \
              (len(passengers_waiting)/len(self.passenger_blocks) < self.passenger_population)):
            
            pos = free_spot.pop(0)
            passenger = Passenger(self.unique_id_counter, self, pos)
            self.schedule.add(passenger)
            self.grid.place_agent(passenger, pos)
            self.unique_id_counter = self.unique_id_counter + 1

            passengers_waiting.append(pos)
