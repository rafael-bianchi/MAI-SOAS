# MAI-SOAS
Final project for the [SOAS(Self Organizing Multiagent Systems)](https://www.fib.upc.edu/en/studies/masters/master-artificial-intelligence/curriculum/syllabus/SOAS-MAI) class.

![Main Window](/resources/images/Screenshot-20200212143049-2326x1890.png)

## 1.  Introduction
Carpooling is a way to share a car so that more than one person rides thesame vehicle at the same time.  This might bring a lot of benefits as reducingthe costs (fuel consumption,  tolls,  parking,  etc.),  the stress of driving andthe most impacting in a town, the number of cars running at the same time.
Carpooling is encouraged in cities that have problems with high trafficnot only because it reduces it, but because it is also eco-friendly.
In touristic cities, in which the taxis have a lot of influence on the transport system and the city traffic, taxi carpooling could help the city increasethe number of passengers traveling at the same time, less waiting time andbenefit from a less polluted and stressful environment.  This project aims tocreate a simulation of a taxi carpool system in a grid world using the MESAABM framework.

## 2. Model

### 2.1 Environment

The environment selected for this simulation was constrained by the [MESA](https://github.com/projectmesa/mesa/) ABM framework and the MultiGrid; it is a grid where each cell can contain one or more object. This choice simplifies the process of making the agents (cabs) moving on the grid.

The roads on the grid are always two-way streets, and the movements allowed are up, down, left and right. The cabs are allowed to walk through the grid only on white cells (which are roads), and the passengers appear on the sidewalks (gray cells). The green cells are grass and are just for visualization purposes and have no influence on the map.
The maps are read from a text file and can be modified as desired to make more complex simulations.

To speed up the decisions of the cab and always use the best route, all the paths are calculated when the program starts and a tuple, for every position to another position in the map with the next coordinate and the total distance. This makes every decision for a cab to do the next movement a constant.

There are only few input parameters(figure 1) for this simulation: number of cabs, passenger population and percentage of passengers carpooling.
The **number of cabs** is the number of cabs that will be available for the current simulation on the grid. The valid range goes from 1 to 10.
The **passenger population** is the percentage of the available spots for passengers that will be filled with passengers. The valid range goes from 10% to 100%.
The **percentage of passengers** carpooling is the probability that a passenger will be create as a carpooling passenger. The valid range goes from 10% to 100%.

<p align="center">
  <img src="/resources/images/fig1_model_params.png" width="20%" alt="Figure 1: Model parameters.">
</p>

### 2.2  
AgentsIn this simulator, there are two main agent types: the Cab and the Passenger.There is a third agent in the code, Grass, but it is only used for visualizationpurposes.

#### 2.2.1  Cab

The cab agent is the agent picks up the passengers and delivers them aroundthe grid.  Cab agents can be in three states:  empty(2b) (yellow),  carpool-ing(2c) (blue), and carrying a regular passenger(2a) (black).

<p align="center">
  <img src="/resources/images/fig2_agents.png" width="40%" alt="Figure 2:  Cab agents representations on the grid.">
</p>

Every time step, there are five stages, defined to use the MESA StagedAc-tivation property.  A Cab agent can walk on the grid, and has a one blockdiameter of sightseeing, to detect passengers on the sidewalks.  If a Cab agentdetects a passenger, the first thing is to communicate this discovery to theother Cab agents, using a simple communication.  The at the same timestep,after all the Cab agents detected and notified the other Cab agents, the Cabagents make a bid for the known passengers and the winners have the passengers assigned to them.  The bidding system is very simple and only considerthe distance from the Cabs and the passenger, matching them according tothe shortest distance and current state of the Cab agent, if it is carpooling,it can only take carpooling passengers.
There are few norms in order to regulate the Cab agents:
*Cab agents can only transport one regular passenger (not carpooling)or up to 3(hardcoded) carpooling passengers.
*Cab agents can only bid if they have the car empty or if they have onlycarpooling passenger and still have free seats.
*Carpooling Cab agents can bid for a close carpooling passenger rightafter dropping a passenger and freeing a seat.  If the carpooling passenger is far away (hardcoded at two blocks), they might decide for not bidding for this passenger.

### 2.2.2  Passenger

When the passenger is created, it can be create as a carpooling passenger, or aregular passenger.  If a passenger is created as a regular passenger, it will onlybe served by a empty cab. If the passenger is created as carpooling passenger,it will be served only by a empty cab or a not completely full cab carpooling.While waiting, a internal counter starts counting right after creation in orderto be used as a index metric.  In order to facilitate the visualization of thegrid, there are six possible representations on the grid for a passenger: regularpassenger not spotted(3a), regular passenger spotted(3b), regular passengerwith  a  cab  assigned(3c),  carpooling  passenger  not  spotted(3d),  carpoolingpassenger spotted(3e) and carpooling passenger with a cab assigned(3f).

<p align="center">
  <img src="/resources/images/fig3_passengers.png" width="40%" alt="Figure 3:  Passenger agents representations on the grid.">
</p>
