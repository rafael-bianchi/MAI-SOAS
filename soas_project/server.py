from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from .model import Walker, CityModel, Grass, Road

def agent_draw(agent):
    portrayal = None
    if agent is None:
        pass
    elif isinstance(agent, Grass):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": ["#00FF00", "#00CC00", "#009900"],
            "w": 1,
            "h": 1
        }
    elif isinstance(agent, Road):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": ["#808080", "#737373", "#666666"],
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

    return portrayal


def launch_city_model():
    city_roads = []

    with open("city_map_21x21.txt","r") as f:
        for line in f:
            l = []
            for cell in line.strip().split('\t'):
                l.append(cell)
                print(f'{cell}', end =" ")
            city_roads.append(l)

    height = len(city_roads)
    width = len(city_roads[0])

    num_agents = 6
    pixel_ratio = 40

    #shortest_paths = utils.

    grid = CanvasGrid(agent_draw, width, height,
                      width * pixel_ratio, height * pixel_ratio)
    server = ModularServer(CityModel, [grid], "SOAS Project - Rafael Bianchi",
                           {"N": num_agents, "width": width, "height": height, "city_map": city_roads})
    server.max_steps = 0
    server.port = 8521
    server.launch()


if __name__ == "__main__":
    launch_city_model()
