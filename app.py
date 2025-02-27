from flask import Flask
from flask_cors import CORS
from romanoaketest import romanoake_bp
app = Flask(__name__)
CORS(romanoake_bp)
app.register_blueprint(romanoake_bp)
if __name__ == '__main__':
    app.run(debug=True)

