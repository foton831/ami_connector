from env_const import EnviromentVariables as ev
import requests
import logging
import json

class ElmaAPI:
    def send_request(data:dict) -> requests.Response:
        url = ev.get_elma_weebhook_url()
        logging.info(f'Sending request to ELMA: {url}')
        logging.info(f'Data: {data}')

        headers = {
            'Content-Type': 'application/json'
        }

        data_json = json.dumps(data)

        response = requests.request(method='POST', url=url, data=data_json, headers=headers)

        return response