from dotenv import load_dotenv
import os 

load_dotenv()

class EnviromentVariables:
    _AMI_HOST = os.environ.get('AMI_HOST')
    _AMI_PORT = os.environ.get('AMI_PORT')
    _AMI_USERNAME = os.environ.get('AMI_USERNAME')
    _AMI_SECRET = os.environ.get('AMI_SECRET')

    @classmethod
    def get_ami_host(cls):
        return cls._AMI_HOST

    @classmethod
    def get_ami_port(cls):
        return cls._AMI_PORT

    @classmethod
    def get_ami_username(cls):
        return cls._AMI_USERNAME

    @classmethod
    def get_ami_secret(cls):
        return cls._AMI_SECRET