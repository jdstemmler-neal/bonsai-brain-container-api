import requests
import uuid

class Brain():
    def __init__(self, url:str='http://localhost', port:str='5000', clientId=None):

        self.base_url = url
        self.port = port

        if clientId is None:
            self.clientId = str(uuid.uuid1())
        else:
            self.clientId = clientId

        self.v2endpoint = f'/v2/clients/{self.clientId}/predict'

        self.url = f'{self.base_url}:{self.port}{self.v2endpoint}'
        self.name = requests.get(f'{self.base_url}:{self.port}/exportedBrain').json()['artifact']['provenance']['brainName']

    def _validate_brain_input(self, data:dict):
        if data.get('state') is None:
            return {'state': data}
        else:
            return data

    def get_prediction(self, data:dict):
        
        brain_data = self._validate_brain_input(data)
        response = requests.post(self.url, json=brain_data)
        if response.status_code == 200:
            return response.json()

    def condense_output(self, output:dict):
        condensed_output = {}
        concepts = output.get('concepts')
        
        for concept, actions in concepts.items():
            for action, value in actions['action'].items():
                condensed_output.update({action: value})
        
        return condensed_output