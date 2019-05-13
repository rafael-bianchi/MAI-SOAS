from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from .model import CityModel, Grass, Walker
from .utils import getShortestPaths


def agent_draw(agent):
    portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": ["#808080", "#737373", "#666666"],
            "w": 1,
            "h": 1
        }
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


def getRoads(city_map, height, width):
    city_roads = {}
    city_blocks = []

    for idx_line, line in enumerate(city_map):
        for idx_col, cell in enumerate(line):
            pos = (idx_line, (height - 1) - idx_col)
            if (cell == '0'):
                neighbors = set()
                for next_pos in [(0,-1), (-1, 0), (1,0), (0,1)]:
                    node_position = (pos[0] + next_pos[0], pos[1] + next_pos[1])
                    
                    if node_position[0] > width - 1 or node_position[0] < 0 or \
                       node_position[1] > height - 1 or node_position[1] < 0:
                        continue

                    if city_map[node_position[0]][node_position[1]] != '0':
                        continue

                    neighbors.add(node_position)
                
                city_roads[pos] = neighbors
            else:
                city_blocks.append(pos)

    routes = getShortestPaths(city_roads)

    return city_roads, city_blocks, routes

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

    city_roads, city_blocks, routes = getRoads(city_map, height, width)

    grid = CanvasGrid(agent_draw, width, height,
                      width * pixel_ratio, height * pixel_ratio)
    server = ModularServer(CityModel, [grid], "SOAS Project - Rafael Bianchi",
                           {"N": num_agents, "width": width, "height": height, "city_map": city_map, "roads": city_roads, "city_blocks": city_blocks, "routes": routes})
    server.max_steps = 0
    server.port = 8521
    server.launch()


if __name__ == "__main__":
    launch_city_model()
