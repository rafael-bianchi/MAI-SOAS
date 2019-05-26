from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from .model import CityModel, Grass, Cab, Passenger
from .utils import getRoads
from mesa.visualization.UserParam import UserSettableParameter


def agent_draw(agent):
    portrayal = {
            "text_color": "white",
        }
    if agent is None:
        pass

    elif isinstance(agent, Passenger):
        icon = "resources/images/taxi_passenger.png"
        
        if(agent.isCarPooler):
            icon = "resources/images/taxi_passenger_blue.png"

        portrayal = {
            "Shape": icon,
            "Layer": 1,
            "IsCarPooler": agent.isCarPooler,
            "text": agent.time_waiting,
            "text_color": "red",
            "scale": .9
        }
    elif isinstance(agent, Grass):
        color =  ["#808080", "#8c8c8c", "#999999"]
        if (agent.isBlockCenter):
            color = ["#00FF00", "#00CC00", "#009900"]

        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": color,
            "w": 1,
            "h": 1
        }
    elif isinstance(agent, Cab):
        icon = "resources/images/taxi_yellow.png"
        
        if(not agent.is_empty):
            if(agent.car_pooling):
                icon = "resources/images/taxi_blue.png"
            else:
                icon = "resources/images/taxi.png"

        portrayal = {
            "Shape": icon,
            "Layer": 1,
            "unique_id": agent.unique_id,
            "text": len(agent.passengers),
            "text_color": "red",
            "scale": 0.8
        }
    else:
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": ["#808080", "#737373", "#666666"],
            "w": 1,
            "h": 1
        }

    return portrayal

def launch_city_model():
    city_map = []

    with open("city_map_21x21.txt","r") as f:
        for line in f:
            l = []
            for cell in line.strip().split('\t'):
                l.append(cell)
            city_map.append(l)

    height = len(city_map)
    width = len(city_map[0])

    num_agents = 6
    pixel_ratio = 5


    city_roads, city_blocks, passenger_blocks, routes = getRoads(city_map, height, width)

    n_slider = UserSettableParameter('slider', "Number of Cabs", 5, 1, 10, 1)

    passenger_population = UserSettableParameter('slider', "Passenger Population", .1, 0, 1, .05)

    passenger_pooling = UserSettableParameter('slider', "Passenger Pooling %", .5, 0, 1, .1)

    # grid = CanvasGrid(agent_draw, width, height,
                    #   width * pixel_ratio, height * pixel_ratio)

    grid = CanvasGrid(agent_draw, width, height,
                      500, 500)

    chart_element = ChartModule([{"Label": "Normal Passenger", "Color": "#000000"},
                             {"Label": "Pooling Passenger", "Color": "#0033cc"},
                             {"Label": "Average", "Color": "#990000"}])

    server = ModularServer(CityModel, [grid, chart_element], "SOAS Project - Rafael Bianchi",
                           {"N": n_slider, "PassengerPopulation":passenger_population, "PassengerPooling": passenger_pooling, "PassengerBlocks": passenger_blocks, "width": width, "height": height, "city_map": city_map, "roads": city_roads, "city_blocks": city_blocks, "routes": routes})
    server.max_steps = 0
    server.port = 8521
    server.launch()


if __name__ == "__main__":
    launch_city_model()
