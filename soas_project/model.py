import random
from itertools import permutations

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation


class Passenger(Agent):
    def __init__(self, unique_id, model, pos, destination, isCarPooler):
        super().__init__(unique_id, model)
        self.pos = pos
        self.time_waiting = 0
        self.destination = destination
        self.isCarPooler = isCarPooler

    def step(self):
        self.time_waiting = self.time_waiting + 1
    
class Grass(Agent):
    def __init__(self, unique_id, model, pos, isBlockCenter):
        super().__init__(unique_id, model)
        self.pos = pos
        self.isBlockCenter = isBlockCenter

    def step(self):
        pass

class Cab(Agent):
    def __init__(self, unique_id, model, pos, heading=(1, 0)):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.pos = pos
        self.heading = heading
        self.destination = pos
        self.passengers = []
        self.car_pooling = False

    @property
    def is_empty(self):
        return len(self.passengers) == 0

    @property
    def has_free_seats(self):
        return self.has_free_seats_normal or self.has_free_seats_normal

    @property
    def has_free_seats_car_pooling(self):
        return self.is_empty or (self.car_pooling and len(self.passengers) < self.model.max_seats)

    @property
    def has_free_seats_normal(self):
        return self.is_empty

    def step(self):
        #Check if there are passengers to be
        # dropped at the current cab's location
        while(not self.is_empty and self.pos == self.destination):
            self.drop_passenger()

        pass_pooling, pass_normal = self.get_passengers_around()

        #Keep picking up passengers while it is possible
        while((self.has_free_seats_car_pooling and len(pass_pooling) > 0) or 
              (self.has_free_seats_normal and len(pass_normal) > 0)):

            #If empty, take the passenger who is waiting longer
            if(self.is_empty):
                all_passengers = pass_normal + pass_pooling
                
                if(len(all_passengers) > 1):
                    all_passengers.sort(key=lambda psg: psg.time_waiting, reverse=True)

                psg = all_passengers[0]

                self.pickup_passenger(psg)

                if(psg.isCarPooler):
                    pass_pooling.remove(psg)
                else:
                    pass_normal.remove(psg)

            elif(self.car_pooling):
                self.pickup_passenger(pass_pooling.pop(0))
            else:
                self.pickup_passenger(pass_normal.pop(0))

        #if empty and not moved, try to find a random destination
        while(self.is_empty and self.pos == self.destination):
            r = random.SystemRandom()
            possible_places = list(self.model.roads.keys())
            r.shuffle(possible_places)
            self.destination = possible_places[0]

        nextPos = self.model.routes[self.pos][self.destination]["next_pos"]

        self.heading = (nextPos[0] - self.pos[0], nextPos[1] - self.pos[1])
        self.model.grid.move_agent(self, nextPos)
        self.pos = nextPos

    def drop_passenger(self):
        #print(f'Dropping passenger {self.passengers[0].unique_id} with destination to {self.passengers[0]} on {self.pos}')
        temp = self.passengers.pop(0)

        if(not self.is_empty):
            self.destination = self.passengers[0].destination

    def get_passengers_around(self):
        neighbors = self.model.grid.get_neighbors(self.pos, False, include_center=False, radius=1)

        pass_pooling = [obj for obj in neighbors if isinstance(obj, Passenger) and obj.isCarPooler]
        pass_normal = [obj for obj in neighbors if isinstance(obj, Passenger) and not obj.isCarPooler]

        if(len(pass_pooling) > 1):
            pass_pooling.sort(key=lambda psg: psg.time_waiting, reverse=True)
        
        if(len(pass_normal) > 1):
            pass_normal.sort(key=lambda psg: psg.time_waiting, reverse=True)

        return pass_pooling, pass_normal 

    def pickup_passenger(self, passenger):
        self.passengers.append(passenger)
        self.destination = self.passengers[0].destination

        if (len(self.passengers) > 1):
            self.prioritize_passenger_order()

        self.car_pooling = passenger.isCarPooler

        self.model.schedule.remove(passenger)
        self.model.grid.remove_agent(passenger)

    def prioritize_passenger_order(self):
        perm = permutations(self.passengers)

        min_dist = None
        best_order = None
        for p in perm:
            total_dist = self.get_distance(self.pos, p[0].destination)
            
            for i in range(0, len(p) - 1):
                d = self.get_distance(p[i].destination, p[i+1].destination)
                total_dist += d
            
            if(min_dist == None or total_dist < min_dist):
                min_dist = total_dist
                best_order = p
        
        self.passengers = list(best_order)
        self.destination = self.passengers[0].destination

    def get_distance(self, pos1, pos2):
        if(pos1 == pos2):
            return 0
        
        return self.model.routes[pos1][pos2]["distance"]

def get_average_time_normal_passenger(model):
    normal_passenger = [a.time_waiting for a in model.schedule.agents if isinstance(a, Passenger) and not a.isCarPooler]

    if(len(normal_passenger) == 0):
        return None

    return sum(normal_passenger) / len(normal_passenger) 

def get_average_time_pooling_passenger(model):
    car_pooler = [a.time_waiting for a in model.schedule.agents if isinstance(a, Passenger) and a.isCarPooler]

    if(len(car_pooler) == 0):
        return None

    return sum(car_pooler) / len(car_pooler) 

def get_average_time_all_passenger(model):
    passengers = [a.time_waiting for a in model.schedule.agents if isinstance(a, Passenger)]

    if(len(passengers) == 0):
        return None

    return sum(passengers) / len(passengers) 

class CityModel(Model):
    def __init__(self, N=2, PassengerPooling=.5, PassengerPopulation=.2, PassengerBlocks={}, width=20, height=10, city_map=[], roads={}, city_blocks=[], routes={}):
        super().__init__()
        self.N = N    # num of cabs
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.roads = roads
        self.routes = routes
        self.passenger_blocks = PassengerBlocks
        self.unique_id_counter = 0
        self.city_blocks = city_blocks
        self.passenger_population = PassengerPopulation
        self.passenger_pooling = PassengerPooling
        self.max_seats = 3
        
        self.datacollector = DataCollector(model_reporters={
                                           "Normal Passenger": get_average_time_normal_passenger,
                                           "Pooling Passenger": get_average_time_pooling_passenger,
                                           "Average": get_average_time_all_passenger})

        self.fill_blocks_agents()

        self.make_taxi_agents()
        self.addPassengers()

        self.running = True
        self.datacollector.collect(self)

    def fill_blocks_agents(self):
        for block in self.city_blocks:
            agent = Grass(self.unique_id_counter, self, block[0], block[1])
            self.schedule.add(agent)
            self.grid.place_agent(agent, block[0])

            self.unique_id_counter = self.unique_id_counter + 1

    def make_taxi_agents(self):
        r = random.SystemRandom()
        for _ in range(self.N):
            possible_places = list(self.roads.keys())
            r.shuffle(possible_places)
            pos = possible_places[0]

            agent = Cab(self.unique_id_counter, self, pos, (1, 0))
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)
            self.unique_id_counter = self.unique_id_counter + 1

    def step(self):
        self.addPassengers()
        self.schedule.step()
        self.datacollector.collect(self)

    def addPassengers(self):
        passengers_waiting = [agent.pos for agent in self.schedule.agents if isinstance(agent, Passenger)]
        
        free_spot = list(set(self.passenger_blocks.keys()) - set(passengers_waiting))
        r = random.SystemRandom()
        r.shuffle(free_spot)

        destinations = set(self.passenger_blocks.keys())

        while(len(free_spot)> 0 and \
              (len(passengers_waiting)/len(self.passenger_blocks) < self.passenger_population)):
            
            pos = free_spot.pop(0)

            possible_destinations = list(destinations - set([pos]))
            destination = self.random.choice(possible_destinations)

            #Just to find another position wich has a road block different from
            # the current passenger 
            while(self.passenger_blocks[destination] == self.passenger_blocks[pos]):
                destination = self.random.choice(possible_destinations)

            isCarPooler = random.random() < self.passenger_pooling
            passenger = Passenger(self.unique_id_counter, self, pos, self.passenger_blocks[destination], isCarPooler)
            self.schedule.add(passenger)
            
            self.grid.place_agent(passenger, pos)
            self.unique_id_counter = self.unique_id_counter + 1

            passengers_waiting.append(pos)
