import json
import os

class ConfigManager:
    def __init__(self):
        self.config = {
            'env': 'UAT',
            'envs': {
                'UAT': {'admin_url': 'УКАЗАТЬ_URL'},
                'ETALON': {'admin_url': 'УКАЗАТЬ_URL'}
            },
            'token': None,
            'gate': 'PRODUCT_GATE',
            'gates': ['PRODUCT_GATE','CONTENT_GATE','USER_GATE','CMS_GATE'],
            'username': ''
            }
                 
    @property
    def env(self):
        return self.config['env']
    
    @env.setter
    def env(self,value):
        self.config['env'] = value

    @property
    def token(self):
        return self.config['token']
    
    @token.setter
    def token(self,value):
        self.config['token'] = value

    @property
    def current_env_config(self):
        return self.config['envs'][self.env]
    
    @property
    def envs(self):
        return self.config['envs']
    
    @property
    def gate(self):
        return self.config['gate']
    
    @gate.setter
    def gate(self,value):
        self.config['gate'] = value

    @property
    def gates(self):
        return self.config['gates']
    
config_manager = ConfigManager()