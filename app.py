from flask import Flask
from flask_cors import CORS

from resources.uploads import uploads_bp

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(uploads_bp)

if __name__ == '__main__':
    app.run(debug=True)