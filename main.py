import io
from itertools import permutations

import osmnx as ox
import folium
import networkx as nx
from flask import Flask, request
import json

MAX_DISTANCE = 4000

TEL_AVIV_UNI = (32.11373035636576, 34.8058324089434)
TEL_BARUCH_BEACH = (32.11712251881483, 34.780281180242206)
KOBIS_HOME = (32.12313757976184, 34.80815597968024)
ODEDS_HOME = (32.11700290929014, 34.79429373720359)

app = Flask(__name__)



def parse_point(data):
    return float(data["Longitude"]), float(data["Latitude"])


def parse_json_data(data):
    midpoints = []
    if 'midpoints' in data:
        midpoints = [parse_point(point) for point in data['midpoints']]
    return parse_point(data['start']), parse_point(data['end']), midpoints


@app.route('/taucarpoolalgo', methods=['POST'])
def taucarpoolalgo_handler():
    start, end, midpoints = parse_json_data(request.json)
    return json.dumps({"result": get_route(start, end, midpoints).decode("utf-8")})


def shortest_path(graph, start, end, midpoints):
    best_path_length = 99999999999
    best_path = None
    for ordered_points in permutations(midpoints):
        path = None
        path_length = 0
        total_path_points = [start] + list(ordered_points) + [end]
        for path_part in range(len(total_path_points)-1):
            if path is None:
                path = nx.shortest_path(graph, total_path_points[path_part], total_path_points[path_part+1], 'travel_time')
            else:
                path += nx.shortest_path(graph, total_path_points[path_part], total_path_points[path_part+1], 'travel_time')[1:]

            path_length += nx.shortest_path_length(graph, total_path_points[path_part], total_path_points[path_part+1], weight='length')

        if path_length < best_path_length:
            best_path = path
            best_path_length = path_length

    return best_path, best_path_length


def get_route(orig, dest, midpoints):
    G = ox.graph_from_point(orig, dist=MAX_DISTANCE, network_type='drive')
    G = ox.speed.add_edge_speeds(G)
    G = ox.speed.add_edge_travel_times(G)

    orig_node = ox.get_nearest_node(G, orig)
    dest_node = ox.get_nearest_node(G, dest)
    midnodes = list(map(lambda x: ox.get_nearest_node(G, x), midpoints))
    chosen_path, path_length = shortest_path(G, orig_node, dest_node, midnodes)
    route_map = ox.plot_route_folium(G, chosen_path)

    with io.BytesIO() as html_stream:
        route_map.save(html_stream, close_file=False)
        html_stream.seek(0)
        return html_stream.read()


def main():
    ox.config(use_cache=True, log_console=True)
    app.run(port=5000)


if __name__ == '__main__':
    main()
