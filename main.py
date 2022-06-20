import io
import time
import traceback
from itertools import permutations

import osmnx as ox
import folium
import networkx as nx
from flask import Flask, request
import json
from flask_cors import CORS
import logging

MAX_DISTANCE = 5000
TEL_AVIV_UNI = (32.11373035636576, 34.8058324089434)

app = Flask(__name__)
CORS(app)
G = None


def parse_point(data):
    return float(data["Longitude"]), float(data["Latitude"])


def parse_json_data(data):
    midpoints = []
    if 'midpoints' in data:
        midpoints = [parse_point(point) for point in data['midpoints']]
    return parse_point(data['start']), parse_point(data['end']), midpoints


def get_graph():
    global G

    if G is None:
        G = ox.graph_from_point(
            TEL_AVIV_UNI,
            dist=MAX_DISTANCE,
            network_type='drive',
            custom_filter=
            '["highway"~"primary|motorway|motorway_link|trunk|trunk_link|secondary|tertiary|primary_link|tertiary_link|unclassified|living_street|residential"]'
        )
        G = ox.speed.add_edge_speeds(G)
        G = ox.speed.add_edge_travel_times(G)

    return G


@app.route('/taucarpoolalgo', methods=['POST'])
def taucarpoolalgo_handler():
    try:
        start, end, midpoints = parse_json_data(request.json)
        html, path_length = get_route(start, end, midpoints)
        return json.dumps({"length": path_length, "result": html.decode("utf-8")})
    except Exception:
        return json.dumps({"internal_error": traceback.format_exc()})


def shortest_path(graph, start, end, midpoints):
    best_path_length = 99999999999
    best_path = None
    best_path_order = None
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
            best_path_order = list(ordered_points)

    return best_path, best_path_length, best_path_order


def get_route(orig, dest, midpoints):
    G = get_graph()
    orig_node = ox.get_nearest_node(G, orig)
    dest_node = ox.get_nearest_node(G, dest)
    midnodes = list(map(lambda x: ox.get_nearest_node(G, x), midpoints))
    chosen_path, path_length, best_midpoint_order = shortest_path(G, orig_node, dest_node, midnodes)
    route_map = ox.plot_route_folium(G, chosen_path)
    folium.Marker(
        location=[orig[0], orig[1]],
        tooltip="Origin",
        icon=folium.Icon(color="green", icon="home")
    ).add_to(route_map)
    folium.Marker(
        location=[dest[0], dest[1]],
        tooltip="Destination",
        icon=folium.Icon(color="red", icon="university", prefix="fa")
    ).add_to(route_map)
    for midpoint in midpoints:
        pickup_no = best_midpoint_order.index(ox.get_nearest_node(G, midpoint)) + 1
        folium.Marker(
            location=[midpoint[0], midpoint[1]],
            icon=folium.Icon(color="blue", icon="user"),
            tooltip=f"Pickup {pickup_no}"
        ).add_to(route_map)

    with io.BytesIO() as html_stream:
        route_map.save(html_stream, close_file=False)
        html_stream.seek(0)
        return html_stream.read(), path_length


def main():
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    ox.config(use_cache=True, log_console=True, log_name='gunicorn.error', log_file=True, log_level=logging.DEBUG)
    app.run(port=5000)


if __name__ == '__main__':
    main()
