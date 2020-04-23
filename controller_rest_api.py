from flask import Flask, request
from flask_restful import Resource, Api
from time import time

app = Flask(__name__)
api = Api(app)
START_TIME = 0
CACHE_TIME = 10
cache_dict = {}
# TODO parse proxy_to_clients as file or as argument
proxy_to_clients = {}


class CachingDB(Resource):

    def clean_cache_dict(self, cache_dict):
        """
        Remove the caching objects which theis timestamps are expired

        :param cache_dict:
        :return:
        """
        try:
            cache_dict = list(filter(lambda x: time()-x[1]["timestamp"] < CACHE_TIME, cache_dict.items()))
            return cache_dict
        except:
            return cache_dict

    def export_data(self, proxy_url, cache_dict, START_TIME):
        """

        :param proxy_url:
        :param cache_dict:
        :param START_TIME:
        :return:
        """
        return {
                 "proxy_url": proxy_url,
                 "cache_dict": cache_dict,
                 "START_TIME": START_TIME
                                    }

    def update_cache_dict(self, request_url, proxy_url):
        """

        :param request_url:
        :param proxy_url:
        :return:
        """
        return {
                    request_url: {
                                    "timestamp": time(),
                                    "proxy_url": proxy_url
                                                }
                    }

    def post(self):
        """
        Example how to call it post('http://localhost:5000',json={"A":1,"B":2}).json()
        As input will get a dict with key the url which client is requested and the ip of client
        :return:
        """
        global START_TIME, cache_dict
        post_data = request.get_json()
        request_url = post_data.get("url", None)
        client_ip = post_data.get("client_ip", None)
        if request_url is None:
            raise Exception("There isn't url")
        # Check if cache_dict is empty
        if bool(cache_dict):
            # cache_dict is not empty
            if time() - START_TIME < CACHE_TIME:
                # The START_TIME is not expired
                # Check if the request url is in cache_dict
                if cache_dict.get(request_url, None):
                    # First check if its timestamp is not expired
                    timestamp = cache_dict[request_url]["timestamp"]
                    if time() - timestamp < CACHE_TIME:
                        # Is not expired
                        return_json = self.export_data(cache_dict[request_url]["proxy_url"], cache_dict, START_TIME)
                    else:
                        # Has expired
                        proxy_url = proxy_to_clients.get(client_ip, None)
                        cache_dict.update(self.update_cache_dict(request_url, proxy_url))
                else:
                    proxy_url = proxy_to_clients.get(client_ip, None)
                    cache_dict.update(self.update_cache_dict(request_url, proxy_url))
                    return_json = self.export_data(proxy_url, cache_dict, START_TIME)
            else:
                # The START_TIME is expired
                # Clean cache_dict
                cache_dict = self.clean_cache_dict(cache_dict)
                if cache_dict.get(request_url, None):
                    return_json = self.export_data(cache_dict[request_url]["proxy_url"], cache_dict, START_TIME)
                else:
                    proxy_url = proxy_to_clients.get(client_ip, None)
                    cache_dict.update(self.update_cache_dict(request_url, proxy_url))
                    return_json = self.export_data(proxy_url, cache_dict, START_TIME)
        else:
            # The cache_dict is empty
            proxy_url = proxy_to_clients.get(client_ip, None)
            START_TIME = time()
            cache_dict.update(self.update_cache_dict(request_url, START_TIME))
            return_json = self.export_data(proxy_url, cache_dict, START_TIME)
        return return_json


api.add_resource(CachingDB, '/')

if __name__ == '__main__':
    app.run(debug=True)
