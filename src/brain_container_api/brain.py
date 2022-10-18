import requests
import uuid

class Brain():
    def __init__(self, url:str='http://localhost', port:str='5000', clientId=None):

        self.base_url = url
        self.port = port
        self.url = f'{self.base_url}:{self.port}'

        if clientId is None:
            self.clientId = str(uuid.uuid1())
        else:
            self.clientId = clientId

        self._set_brain_information()

    def _set_brain_information(self):
        url = f'{self.url}/exportedBrain'
        req = requests.get(url)
        if req.status_code == 200:
            self.brain_info = req.json()
            self.brain_name = self.brain_info['artifact']['provenance']['brainName']
            self.brain_version = self.brain_info['artifact']['provenance']['brainVersion']

    def _coerce_v1_schema(self, data:dict):
        if data.get('state') is None:
            return data
        else:
            return data.get('state')

    def _coerce_v2_schema(self, data:dict):
        if data.get('state') is None:
            return {'state': data}
        else:
            return data

    def _get_prediction(self, url:str, data:dict):
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()

    def _v1_get_prediction(self, data:dict):
        data = self._coerce_v1_schema(data)
        url = f'{self.url}/v1/prediction'
        response = self._get_prediction(url, data)

        return response

    def _standardize_output(self, output:dict):
        standardized_output = {}
        concepts = output.get('concepts')
        
        for concept, actions in concepts.items():
            for action, value in actions['action'].items():
                standardized_output.update({action: value})
        
        return standardized_output

    def _v2_get_prediction(self, data:dict, standard_output:bool):
        data = self._coerce_v2_schema(data)
        url = f'{self.url}/v2/clients/{self.clientId}/predict'
        response = self._get_prediction(url, data)

        if standard_output:
            return self._standardize_output(response)
        else:
            return response
    
    def get_prediction(self, data:dict, api_version:int=2, standard_output:bool=True):
        
        if api_version == 1:
            prediction = self._v1_get_prediction(data)
        elif api_version == 2:
            prediction = self._v2_get_prediction(data, standard_output)

        return prediction

    # legacy entrypoint for v1 api
    def get_recommendation(self, state:dict):
        return self.get_prediction(data=state, api_version=1)