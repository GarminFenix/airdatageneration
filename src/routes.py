"""
A module to define the Flask blueprint and API endpoints.
"""


from datetime import datetime
from flask import Blueprint, make_response, jsonify, request
from pseudo_air_pollution_data import pollution_data, simulate_live_data      # removed src. prefix to avoid import issues
from subscriptions_utils import subscriptions



pollution_bp = Blueprint('pollution-data', __name__, url_prefix='/pollutiondata')



@pollution_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """
    Endpoint to subscribe to live pollution data updates.
    """
    req_data = request.get_json()
    notification_url = req_data.get('notificationUrl')
    datasets = req_data.get("subscriptions", [])

    if not notification_url or not datasets:
        return make_response(jsonify("Missing 'notificationUrl' or 'subscriptions'."), 400)
    
    print(f"New subscription request: {notification_url}")  # Debugging 
    subscriptions.append({
        "notificationUrl": notification_url,
        "subscriptions": datasets
    })
    # Push latest data to subscribers
    print("Subscription setup. Pushing latest data push to subscribers...")  # Debugging
    simulate_live_data()
    return make_response(jsonify({"SubscriptinID": len(subscriptions)}), 201)


@pollution_bp.route('/simtime', methods=['GET'])
def get_simulation_time():
    """
    Returns the current timestamp used in the live simulation.
    """
    return make_response(
        jsonify({"current_simulation_time": simulate_live_data.timestamp.isoformat()}),
        200
    )

@pollution_bp.route('/simtime', methods=['POST'])
def set_simulation_time():
    """
    Manually sets the simulation timestamp.
    Give the request in the body in this format {"timestamp": "2025-05-19T18:30:00+00:00"}
    """
    req_data = request.get_json()
    ts_str = req_data.get("timestamp")

    try:
        simulate_live_data.timestamp = datetime.strptime(ts_str, '%Y-%m-%dT%H:%M:%S%z')
        return make_response(jsonify({"message": "Simulation time updated."}), 200)
    except Exception as e:
        return make_response(jsonify({"error": f"Invalid timestamp: {str(e)}"}), 400)


@pollution_bp.route('/', methods=['GET'])
def requested_pollution_data():
    """
    Returns pollution data for a given timestamp and site.
    """
    if request.method != 'GET':
        return make_response(jsonify("Method not supported."), 404)
    
    timestamp = request.args.get('timestamp')
    site = request.args.get('site')
    
    # Debugging timestamp issues
    print(f"Received timestamp: {timestamp}")

    if timestamp is None or site is None:
        return make_response(jsonify("Missing parameters required: timestamp and site"), 400)
    
    try:    
        timestamp = timestamp.replace(" ", "+")  # Format timestamp
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')


    except ValueError:
        return make_response(jsonify("Invalid timestamp format. Use 'YYYY-MM-DDTHH:MM:SS.sss+0000'."), 400)

    
    data = pollution_data.get_pollution_data(timestamp, site)
    coordinates = pollution_data.get_site_coordinates(site)

    if coordinates is None:
        return make_response(jsonify("No coordinates found for the given site."), 404)

    if data is None or not data:
        return make_response(jsonify("No pollution data available for the given timestamp and site."), 400)
    
    response = {
        "coordinates": coordinates,
        "pollution_data": data
    }

    return make_response(jsonify(response), 200)

@pollution_bp.route('/sitemetadata', methods=['GET'])
def get_all_coordinates():
    """
    Returns all static site metadata, ie coordinates.
    """
       
    site_coords = pollution_data.get_all_sites_coordinates()

    if not site_coords:
        return make_response(jsonify("No site metadata available."), 404)

    return make_response(jsonify(site_coords), 200)