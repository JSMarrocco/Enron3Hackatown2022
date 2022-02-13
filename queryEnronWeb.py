import requests

config = {}
config['CONTAINER_ID'] = '001' # stay constant
config['ENRON3WEB_URI'] = 'http://51.222.45.44:3000/api/container/post/%s/%d' 

capacity = 80 # normalize between 0-1000

response = requests.post(config['ENRON3WEB_URI'] % ( config['CONTAINER_ID'] ,  capacity)) # stay constant

print(response)
