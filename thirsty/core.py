import io
import math
import re

import folium
import gpxpy
import requests
import rich.console
import rich.progress

console = rich.console.Console()


OVERPASS_URL = "http://overpass-api.de/api/interpreter"


AMENITIES = {
    "water": "[amenity=drinking_water]",
    "point": "[amenity=water_point][drinking_water=yes]",
    "tap": "[man_made=water_tap][drinking_water=yes]",
    "spring": "[natural=spring][drinking_water=yes]",
    "fountain": "[amenity=fountain][drinking_water=yes]",
    "bakery": "[shop=bakery]",
}


def display_gpx_on_map(data, pois):
    """
    Display the GPX route and POIs on a map
    """

    # Create a base map centered around the middle of the GPX track
    track_latitudes = [ point.latitude
                        for track in data.tracks
                        for segment in track.segments
                        for point in segment.points ]

    track_longitudes = [ point.longitude
                         for track in data.tracks
                         for segment in track.segments
                         for point in segment.points ]

    center_lat = sum(track_latitudes) / len(track_latitudes)
    center_lon = sum(track_longitudes) / len(track_longitudes)

    map_center = [center_lat, center_lon]
    folium_map = folium.Map(location=map_center, zoom_start=12)

    # Plot the GPX track on the map
    for track in data.tracks:
        for segment in track.segments:
            # Create a list of coordinates from the GPX track segment
            track_coords = [(point.latitude, point.longitude) for point in segment.points]
            folium.PolyLine(track_coords, color="blue", weight=2.5, opacity=1).add_to(folium_map)

    # Plot POIs on the map
    for poi in pois:
        poi = normalize_osm_poi(poi)

        folium.Marker(
            location=[poi['lat'], poi['lon']],
            popup=folium.Popup(poi["name"], max_width=300),
            icon=folium.Icon(color="blue", icon=poi["icon"], prefix="fa")
        ).add_to(folium_map)

    return folium_map


def download_gpx(url):
    """
    Download GPX from URL
    """

    console.print(f"⏳ Downloading GPX from {url}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("Content-Length", 0))

    data = io.BytesIO()

    with rich.progress.Progress() as progress:
        task = progress.add_task("[cyan] Downloading", total=total_size)

        for chunk in response.iter_content(chunk_size=1024):
            data.write(chunk)
            progress.update(task, advance=len(chunk))

    data.seek(0)
    return data

def get_bounds(gpx):
    """
    Return GPX trace bounding box [south, west, north, est]
    """

    min_lat = min(pt.latitude for trk in gpx.tracks for seg in trk.segments for pt in seg.points)
    max_lat = max(pt.latitude for trk in gpx.tracks for seg in trk.segments for pt in seg.points)
    min_lon = min(pt.longitude for trk in gpx.tracks for seg in trk.segments for pt in seg.points)
    max_lon = max(pt.longitude for trk in gpx.tracks for seg in trk.segments for pt in seg.points)
    return min_lat, min_lon, max_lat, max_lon


def query_overpass(bbox, poi_types):
    """
    Generate an Overpass QL query for potable drinking water POIs.
    """

    south, west, north, east = bbox
    bbox_str = f"({south},{west},{north},{east})"

    query_parts = []
    for poi_type in poi_types:
        tag_filter = AMENITIES[poi_type]
        for osm_type in ["node", "way", "relation"]:
            query_parts.append(f'{osm_type}{tag_filter}{bbox_str};')

    query = "[out:json][timeout:25];(" + "".join(query_parts) + ");out center;"
    response = requests.post(OVERPASS_URL, data=query)
    response.raise_for_status()
    return response.json()["elements"]


def add_waypoints_to_gpx(gpx, pois):
    """
    Add POI to GPX trace
    """

    for poi in pois:
        poi = normalize_osm_poi(poi)
        wpt = gpxpy.gpx.GPXWaypoint()
        wpt.latitude = poi["lat"]
        wpt.longitude = poi["lon"]
        wpt.name = poi["name"]
        wpt.description = poi["type"]
        wpt.symbol = poi["sym"]
        gpx.waypoints.append(wpt)

    return gpx


def normalize_osm_poi(poi):
    tags = poi.get("tags", {})

    categories = ["amenity", "shop"]
    category = next((k for k in categories if k in tags), None)
    poi_type = tags.get(category) if category else None

    assert(category is not None)
    assert(poi_type is not None)

    # Symbols used for HTML/Folium
    icons = {
        "bakery": "shopping-cart",
        "drinking_water": "tint",
        "supermarket": "shopping-cart",
        "cafe": "coffee",
        "restaurant": "cutlery",
    }
    icon = icons.get(poi_type, "info-sign")

    # Symbols used for Garmin
    syms = {
        "bakery": "Food Source",
        "drinking_water": "Drinking Water",
        "supermarket": "Shopping Center",
        "cafe": "Bar",
        "restaurant": "Restaurant",
    }
    sym = syms.get(poi_type, "Pin")

    return {
        "lat": poi["lat"],
        "lon": poi["lon"],
        "category": category,
        "type": poi_type,
        "name": tags.get("name", poi_type),
        "icon": icon,
        "sym": sym,
    }


def haversine(lat1, lon1, lat2, lon2):
    """
    Return distance in meter between two GPS points
    """

    R = 6371000 # Earth radius in meter
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def filter_pois_near_track(gpx, pois, max_distance_m=100):
    """
    Keep only POI near trace
    """

    points = [pt for trk in gpx.tracks for seg in trk.segments for pt in seg.points]
    nearby_pois = []

    for poi in rich.progress.track(pois, description="Filtering POI"):
        lat, lon = poi["lat"], poi["lon"]
        if any(haversine(lat, lon, pt.latitude, pt.longitude) < max_distance_m for pt in points):
            nearby_pois.append(poi)

    return nearby_pois


def sanitize_gpx_text(data):
    """
    Fix GPX content by replacing unescaped '&' with '&amp;'
    """

    return re.sub(r'&(?!amp;|quot;|lt;|gt;|apos;)', '&amp;', data)
