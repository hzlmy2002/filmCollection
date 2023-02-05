from conn import dbConnection
from flask import Flask
from flask_restx import Api
from uc1 import ViewTitle

app = Flask(__name__)
api = Api(app)


api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')


if __name__ == '__main__':
    app.run(debug=True)