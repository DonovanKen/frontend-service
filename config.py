# # config.py
# import os
# from dotenv import load_dotenv

# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)


# class Config:
#     SECRET_KEY = 'y2BH8xD9pyZhDT5qkyZZRgjcJCMHdQ'
#     WTF_CSRF_SECRET_KEY = 'VyOyqv5Fm3Hs3qB1AmNeeuvPpdRqTJbTs5wKvWCS'


# class DevelopmentConfig(Config):
#     ENV = "development"
#     DEBUG = True


# class ProductionConfig(Config):
#     ENV = "production"
#     DEBUG = False





# config.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = 'y2BH8xD9pyZhDT5qkyZZRgjcJCMHdQ'
    WTF_CSRF_SECRET_KEY = 'VyOyqv5Fm3Hs3qB1AmNeeuvPpdRqTJbTs5wKvWCS'
    
    # Microservices URLs - ADD THESE
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-api.microservices:5001')
    PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-api.microservices:5002') 
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-api.microservices:5003')


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    # For local development, use external URLs
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://192.168.2.88:5001')
    PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5002')
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://localhost:5003')


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    # For production, use Kubernetes service names
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-api.microservices:5001')
    PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-api.microservices:5002')
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-api.microservices:5003')

