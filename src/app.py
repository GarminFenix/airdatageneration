from flask import Flask


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
    from src.routes import pollution_bp
    app.register_blueprint(pollution_bp)

    # Debugging for container deployment issues to azure
    print("Create_app successfully executed.")
    
    return app

app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=80, debug=True)


