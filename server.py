import os
from flask import Flask
from flask_restful import reqparse, Api, Resource
from adal import AuthenticationContext
import requests
import json
import gunicorn

app = Flask(__name__)
api = Api(app)

PBI = {
    'domain': 'dominio.com.br', #domínio do locatário
    'client_id': '00000000-0000-0000-0000-000000000000', # Id do cliente no azure
    'user_name': 'suporte@dominio.com.br', # nome do usuário Power BI
    'user_password': 'senha_123', # senha do usuário Power BI
}

parser = reqparse.RequestParser()
parser.add_argument('group_id')
parser.add_argument('dataset_id')


class AtualizarPowerBI(Resource):
    def post(self):
        args = parser.parse_args()
        group_id = args['group_id']
        dataset_id = args['dataset_id']

        resource_uri = "https://analysis.windows.net/powerbi/api"
        auth_context = AuthenticationContext("https://login.microsoftonline.com/" + PBI['domain'])
        token_response = auth_context.acquire_token_with_username_password(resource_uri, PBI['user_name'],
                                                                           PBI['user_password'], PBI['client_id'])
        token = "Bearer " + token_response["accessToken"]
        headers = {"Authorization": token, "Content-type": "application/json"}
        #body = {"notifyOption": "MailOnCompletion"}
        body = {}
        post_url = "https://api.powerbi.com/v1.0/myorg/groups/" + group_id + "/datasets/" + dataset_id + "/refreshes"
        requests.post(post_url, headers=headers, data=json.dumps(body))
        return "OK", 200


api.add_resource(AtualizarPowerBI, '/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
