from conn import dbConnection
from flask import Flask
from flask_restx import Api
from uc12 import ViewTitle, ViewDetails

app = Flask(__name__)
api = Api(app)


api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)