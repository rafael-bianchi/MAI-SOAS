from mesa import Agent

import random
from itertools import permutations

class Passenger(Agent):
    def __init__(self, unique_id, model, pos, destination, road_access, isCarPooler):
        super().__init__(unique_id, model)
        self.pos = pos
        self.time_waiting = 0
        self.destination = destination
        self.isCarPooler = isCarPooler
        self.road_access = road_access

        self.visualized = False
        self.has_cab_assigned = False

        self.last_step_executed = False
        self.set_to_be_removed = False

        self.distance_travelled = 0
        self.distance_estimation = 0

    def auto_remove(self):
        if(self.last_step_executed):
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
        else:
            self.set_to_be_removed = True

    def step(self):
        self.time_waiting = self.time_waiting + 1
        self.last_step_executed = True

        if(self.set_to_be_removed):
            self.auto_remove()

    #Stage 1
    def stage_1(self):
        self.last_step_executed = False
        pass
    
    #Stage 2
    def stage_2(self):
        pass

    #Stage 3
    def stage_3(self):
        pass

    #Stage 4
    def stage_4(self):
        pass

class Grass(Agent):
    def __init__(self, unique_id, model, pos, isBlockCenter):
        super().__init__(unique_id, model)
        self.pos = pos
        self.isBlockCenter = isBlockCenter

    def step(self):
        pass

    #Stage 1
    def stage_1(self):
        pass
    
    #Stage 2
    def stage_2(self):
        pass

    #Stage 3
    def stage_3(self):
        pass

    #Stage 4
    def stage_4(self):
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
        self.sighted_passengers = dict()

    @property
    def is_empty(self):
        return len(self.passengers) == 0

    @property
    def has_free_seats(self):
        return self.has_free_seats_normal or self.has_free_seats_car_pooling

    @property
    def has_free_seats_car_pooling(self):
        return self.is_empty or (self.car_pooling and len(self.passengers) < self.model.max_seats)

    @property
    def has_free_seats_normal(self):
        return self.is_empty

    @property
    def has_passenger_assigned(self):
        for passg in self.sighted_passengers.keys():
            if (self.sighted_passengers[passg] != None and self.sighted_passengers[passg].unique_id == self.unique_id):
                return True

        return False

    @property
    def passenger_assigned(self):
        for passg in self.sighted_passengers.keys():
            if (self.sighted_passengers[passg] != None and self.sighted_passengers[passg].unique_id == self.unique_id):
                return passg

        return None

    @property
    def unasigned_passenger(self):
        unasigned_passengers = [a for a in self.sighted_passengers.keys() if self.sighted_passengers[a] == None]

        return unasigned_passengers

    def broadcast_sighted_passengers(self, passengers):
        for p in passengers:
            if (p not in self.sighted_passengers):
                self.sighted_passengers[p] = None
                p.visualized = True

    def remove_pickedup(self, passenger):
        self.sighted_passengers.pop(passenger)

    def broadcast_pickup(self, passenger):
        self.sighted_passengers.pop(passenger)
        for agent in [a for a in self.model.schedule.agents if isinstance(a, Cab) and a.unique_id != self.unique_id]:
            agent.remove_pickedup(passenger)

    #Stage 1
    def stage_1(self):
        #print(f'Entering stage 1 - {self.unique_id}')
        #drop_passengers

        #Check if there are passengers to be
        # dropped at the current cab's location
        while(not self.is_empty and self.pos == self.destination):
            self.drop_passenger()

        #print(f'Leaving stage 1 - {self.unique_id}')
    #Stage 2
    def stage_2(self):
        #print(f'Entering stage 2 - {self.unique_id}')
        #look_around_and_notify_drivers
        #print('Lookding around')
        passengers = self.get_passengers_around()

        #print('Updating local sighted_list')
        for p in [pas for pas in passengers if pas not in self.sighted_passengers.keys()]:
            self.sighted_passengers[p] = None

        if(len(passengers) > 0):
            #print('Notifying other cabs')
            for agent in [a for a in self.model.schedule.agents if isinstance(a, Cab) and a.unique_id != self.unique_id]:
                agent.broadcast_sighted_passengers(passengers)

        #print(f'Leaving stage 2 - {self.unique_id}')
    #Stage 3
    def stage_3(self):
        #print(f'Entering stage 3 - {self.unique_id}')
        #bid_for_passengers
        if(self.has_free_seats and not self.has_passenger_assigned and len(self.unasigned_passenger) > 0):
            dist_pass = {}
            for p in self.unasigned_passenger:
                distance = self.get_distance(self.pos, p.road_access)
                
                if(self.has_free_seats_normal or (p.isCarPooler and self.has_free_seats_car_pooling and distance <= 1)):
                    dist_pass[p] = distance
        
            self.model.bid(self, dist_pass)

        #print(f'Leaving stage 3 - {self.unique_id}')
    #Stage 4
    def stage_4(self):
        #print(f'Entering stage 4 - {self.unique_id}')
        #get_auction_results
        self.model.update_winners()

        for passenger in self.model.current_bidding_results.keys():
            cab = self.model.current_bidding_results[passenger]
            self.sighted_passengers[passenger] = cab
            
            passenger.has_cab_assigned = cab != None

            #print(f'Cab {cab.unique_id if cab != None else "No one"} is assigned to passenger {passenger.unique_id if passenger != None else "No one"}')

        #print(f'Leaving stage 4 - {self.unique_id}')
    
    #Stage 5
    def step(self):
        #print(f'Entering stage step - {self.unique_id}')

        passassigned = self.passenger_assigned

        if(passassigned != None):
            self.destination = passassigned.road_access
            if(self.pos == self.destination):
                self.pickup_passenger(passassigned)

        #if empty and not moved, try to find a random destination
        while(not self.has_passenger_assigned and self.is_empty and self.pos == self.destination):
            r = random.SystemRandom()
            possible_places = list(self.model.roads.keys())
            r.shuffle(possible_places)
            self.destination = possible_places[0]

        nextPos = self.model.routes[self.pos][self.destination]["next_pos"]

        self.heading = (nextPos[0] - self.pos[0], nextPos[1] - self.pos[1])
        self.model.grid.move_agent(self, nextPos)
        self.pos = nextPos

        #Update passengers travelled time
        for p in self.passengers:
            p.distance_travelled += 1

        #print(f'Last known pos = {self.pos}')
        #print(f'Leaving stage step - {self.unique_id}')

    def drop_passenger(self):
        #print(f'Dropping passenger {self.passengers[0].unique_id} with destination to {self.passengers[0]} on {self.pos}')
        temp = self.passengers.pop(0)

        if(not self.is_empty):
            self.destination = self.passengers[0].destination

    def get_passengers_around(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True, include_center=False, radius=1)

        passengers = [obj for obj in neighbors if isinstance(obj, Passenger)]

        return passengers

    def pickup_passenger(self, passenger):
        if(not self.has_free_seats):
            raise('Cannot add any more passengers.')

        passenger.distance_estimation = self.get_distance(self.pos, passenger.destination)

        self.passengers.append(passenger)
        self.destination = self.passengers[0].destination

        if (len(self.passengers) > 1):
            self.prioritize_passenger_order()

        self.car_pooling = passenger.isCarPooler
 
        self.broadcast_pickup(passenger)

        passenger.auto_remove()

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