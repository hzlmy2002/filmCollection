from conn import dbConnection
from flask import Flask
from flask_restx import Api
from uc1 import ViewTitle, ViewDetails

app = Flask(__name__)
api = Api(app)


api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')


if __name__ == '__main__':
    app.run(debug=True)