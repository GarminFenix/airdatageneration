from datetime import datetime
from flask import Blueprint, make_response, jsonify, request
from pseudo_air_pollution_data import pollution_data


pollution_bp = Blueprint('pollution data', __name__, url_prefix='/pollutiondata')

@pollution_bp.route('/', methods=['GET'])
def pollution_data():
    """
    Returns pollution data for a given timestamp and site.
    """
    if request.method != 'GET':
        return make_response(jsonify("Method not supported."), 404)
    
    timestamp = request.args.get('timestamp')
    site = request.args.get('site')
    
    if timestamp is None or site is None:
        return make_response(jsonify("Missing parameters required: timestamp and site"), 400)
    
    try:    
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        return make_response(jsonify("Invalid timestamp format. Use 'YYYY-MM-DDTHH:MM:SS.ssssss+00:00'."), 400)
    
        
    return make_response(jsonify(pollution_data.get_pollution_data(timestamp, site)), 200)