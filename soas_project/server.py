from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from .model import CityModel, Grass, Walker, Passenger
from .utils import getRoads
from mesa.visualization.UserParam import UserSettableParameter


def agent_draw(agent):
    portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": ["#808080", "#737373", "#666666"],
            "w": 1,
            "h": 1
        }
    if agent is None:
        pass

    elif isinstance(agent, Passenger):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 1,
            "Color": ["#3399ff", "#1a8cff", "#0080ff"],
            "w": 1,
            "h": 1
        }
    elif isinstance(agent, Grass):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": ["#00FF00", "#00CC00", "#009900"],
            "w": 1,
            "h": 1
        }
    elif isinstance(agent, Walker):
        portrayal = {
            "Shape": "arrowHead",
            "Layer": 1,
            "Color": ["#0066ff", "#005ce6"],
            "stroke_color": "#666666",
            "Filled": "true",
            "heading_x": agent.heading[0],
            "heading_y": agent.heading[1],
            "text": agent.unique_id,
            "text_color": "white",
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
    pixel_ratio = 40

    city_roads, city_blocks, passenger_blocks, routes = getRoads(city_map, height, width)

    n_slider = UserSettableParameter('slider', "Number of Cabs", 5, 1, 10, 1)

    passenger_population = UserSettableParameter('slider', "Passenger Population", .1, 0, 1, .05)

    passenger_pooling = UserSettableParameter('slider', "Passenger Pooling %", .5, 0, 1, .1)

    grid = CanvasGrid(agent_draw, width, height,
                      width * pixel_ratio, height * pixel_ratio)
    server = ModularServer(CityModel, [grid], "SOAS Project - Rafael Bianchi",
                           {"N": n_slider, "PassengerPopulation":passenger_population, "PassengerPooling": passenger_pooling, "PassengerBlocks": passenger_blocks, "width": width, "height": height, "city_map": city_map, "roads": city_roads, "city_blocks": city_blocks, "routes": routes})
    server.max_steps = 0
    server.port = 8521
    server.launch()


if __name__ == "__main__":
    launch_city_model()
