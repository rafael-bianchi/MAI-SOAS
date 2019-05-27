import copy
import math
import random
import statistics

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import StagedActivation

from .agents import Cab, Grass, Passenger

def get_average_perc_over_travelled_pool_passengers(model):
    cabs = [a for a in model.schedule.agents if isinstance(a, Cab) and a.car_pooling and len(a.passengers) > 0]
    
    perc_values = []

    for c in cabs:
        for p in c.passengers:
            if (p.distance_travelled > p.distance_estimation):
                overtravelled = max( p.distance_travelled / p.distance_estimation, 1 )-1
                perc_values.append( overtravelled * 100.0)

    if(len(perc_values) == 0):
        return 0
    
    median = statistics.median(perc_values) 

    return median

def get_count_passengers_not_pooling_travelling(model):
    passengers = [len(a.passengers) for a in model.schedule.agents if isinstance(a, Cab) and not a.car_pooling and len(a.passengers) > 0]

    return sum(passengers)

def get_count_passengers_pooling_travelling(model):
    passengers = [len(a.passengers) for a in model.schedule.agents if isinstance(a, Cab) and a.car_pooling and len(a.passengers) > 0]

    return sum(passengers)

def get_count_passengers_travelling(model):
    passengers = [len(a.passengers) for a in model.schedule.agents if isinstance(a, Cab)]

    return sum(passengers)

def get_count_cars_empty(model):
    cabs = [a for a in model.schedule.agents if isinstance(a, Cab) and len(a.passengers) == 0]

    return len(cabs)

def get_count_cars_carpooling(model):
    cabs = [a for a in model.schedule.agents if isinstance(a, Cab) and a.car_pooling and len(a.passengers) > 0]

    return len(cabs)

def get_count_cars_not_carpooling(model):
    cabs = [a for a in model.schedule.agents if isinstance(a, Cab) and not a.car_pooling and len(a.passengers) > 0]

    return len(cabs)

def get_average_time_normal_passenger(model):
    normal_passenger = [a.time_waiting for a in model.schedule.agents if isinstance(a, Passenger) and not a.isCarPooler]

    if(len(normal_passenger) == 0):
        return 0

    return sum(normal_passenger) / len(normal_passenger) 

def get_average_time_pooling_passenger(model):
    car_pooler = [a.time_waiting for a in model.schedule.agents if isinstance(a, Passenger) and a.isCarPooler]

    if(len(car_pooler) == 0):
        return 0

    return sum(car_pooler) / len(car_pooler) 

def get_average_time_all_passenger(model):
    passengers = [a.time_waiting for a in model.schedule.agents if isinstance(a, Passenger)]

    if(len(passengers) == 0):
        return 0

    return sum(passengers) / len(passengers) 

class CityModel(Model):
    def __init__(self, N=2, PassengerPooling=.5, PassengerPopulation=.2, PassengerBlocks={}, width=20, height=10, city_map=[], roads={}, city_blocks=[], routes={}):
        super().__init__()
        self.N = N    # num of cabs
        self.grid = MultiGrid(width, height, torus=False)
        
        model_stages = ['stage_1', 'stage_2', 'stage_3', 'stage_4', 'step']

        self.schedule = StagedActivation(self, model_stages, shuffle=True)
        self.roads = roads
        self.routes = routes
        self.passenger_blocks = PassengerBlocks
        self.unique_id_counter = 0
        self.city_blocks = city_blocks
        self.passenger_population = PassengerPopulation
        self.passenger_pooling = PassengerPooling
        self.max_seats = 3

        #Bidding properties
        self.current_bidding_results = {}
        self.all_biddings = {}

        
        self.datacollector = DataCollector(model_reporters={
                                           "Normal Passenger": get_average_time_normal_passenger,
                                           "Pooling Passenger": get_average_time_pooling_passenger,
                                           "Average": get_average_time_all_passenger,
                                           "Cars carpooling": get_count_cars_carpooling,
                                           "Cars not carpooling": get_count_cars_not_carpooling,
                                           "Empty cars": get_count_cars_empty,
                                           "Passengers Travelling (not pooling)": get_count_passengers_not_pooling_travelling,
                                           "Passengers Travelling (pooling)": get_count_passengers_pooling_travelling,
                                           "Passengers Travelling": get_count_passengers_travelling,
                                           "Overtravelled (in percentage)": get_average_perc_over_travelled_pool_passengers})

        self.fill_blocks_agents()

        self.make_taxi_agents()
        self.addPassengers()

        self.running = True
        self.datacollector.collect(self)

    def clear_biddings(self):
        self.current_bidding_results = None
        self.all_biddings = {}

    def update_winners(self):
        #Check if it is the first time being called
        if (self.current_bidding_results == None):
            self.current_bidding_results = {}

            if (len(self.all_biddings) == 0):
                return
        
            passenger_assignment = {}

            number_of_cabs_bidding = len(self.all_biddings)
            first_cab = next(iter(self.all_biddings.keys()))

            passengers_being_bidded = set()

            for cab in self.all_biddings.keys():
                for psg in self.all_biddings[cab].keys():
                    passengers_being_bidded.add(psg)

            number_of_passengers = len(passengers_being_bidded)

            while(len(passenger_assignment) < number_of_cabs_bidding and len(passenger_assignment) < number_of_passengers):
                passengers_all_distances = {}
                passenger_assignment_temp = {}
                for cab in self.all_biddings.keys():
                    if (cab not in passenger_assignment.values()):
                        for psg in passengers_being_bidded:
                            if (psg not in passenger_assignment.keys()):
                                cab_bidding_for_this_pass = psg in self.all_biddings[cab].keys()
                                
                                if(cab_bidding_for_this_pass):
                                    pass_dist = self.all_biddings[cab][psg]
                                else:
                                    pass_dist = math.inf

                                if(psg not in passengers_all_distances or passengers_all_distances[psg] > pass_dist):
                                    passengers_all_distances[psg] = pass_dist
                                    passenger_assignment_temp[psg] = cab if cab_bidding_for_this_pass else None

                #order the passengers by the distance to the closest cab
                passengers_all_distances = sorted(passengers_all_distances.items(), key=lambda kv: kv[1])

                #get the passenger who has the closest cab
                passenger = passengers_all_distances[0][0]
                #get the cab
                cab = passenger_assignment_temp[passenger]

                passenger_assignment[passenger] = cab

            self.current_bidding_results = passenger_assignment

    def bid(self, cab, passengers_offers):
        self.all_biddings[cab] = passengers_offers

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
        
        self.clear_biddings()

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
            passenger = Passenger(self.unique_id_counter, self, pos, self.passenger_blocks[destination], self.passenger_blocks[pos], isCarPooler)
            self.schedule.add(passenger)
            
            self.grid.place_agent(passenger, pos)
            self.unique_id_counter = self.unique_id_counter + 1

            passengers_waiting.append(pos)
