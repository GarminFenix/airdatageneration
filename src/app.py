"""
A  module that defines the Flask appliation factory.
Sets up the core instance and registers the pollution
blueprint.
Author: Ross Cochrane
"""



from flask import Flask, jsonify



print("app.py being loaded")    # debugging

def create_app(test_config:dict = {}):
    """
    A factory function to create flask apps with an optional 
    dict input for testing
    """
    
    app = Flask(__name__)
    # Check if app should be configured for testing
    if len(test_config) >0:
        app.config.update(test_config)
    
    # Register pollution_bp with the Flask app so its routes are available
    from routes import pollution_bp                 # debugging: removed src. prefix to avoid 
                                                    #import issues
    app.register_blueprint(pollution_bp)

    # health check route for azure restart issues
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify(status="healthy"), 200

    # Debugging for container deployment issues to azure
    print("Create_app successfully executed.")
    
    return app

app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=8182, debug=True)


