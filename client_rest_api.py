from flask import Flask, request
from flask_restful import Resource, Api
from time import time
from requests import post

app = Flask(__name__)
api = Api(app)
START_TIME = 0
CACHE_TIME = 10
cache_dict = {}
controller_ip = ""
client_ip = ""


class ClientCachingDB(Resource):
    def request_controller(self, url, client_ip):
        """

        :return:
        """
        controller_data = post(controller_ip, json={"url": url, "client_ip": client_ip}).json()
        cache_dict = controller_data["cache_dict"]
        # START_TIME = controller_data["START_TIME"]
        proxy_url = controller_data["proxy_url"]
        return cache_dict, START_TIME, proxy_url

    def post(self):
        # global START_TIME, cache_dict, CACHE_TIME
        global START_TIME, cache_dict, CACHE_TIME
        post_data = request.get_json()
        if post_data.get("request_url", None):
            url = post_data["request_url"]
            if not bool(cache_dict):
                # cache dict is empty
                # cache_dict, START_TIME, proxy_url = self.request_controller(url, client_ip)
                cache_dict, proxy_url = self.request_controller(url, client_ip)
            else:
                if cache_dict.get(url, None):
                    proxy_url = cache_dict[url]["proxy_url"]
                else:
                    cache_dict, proxy_url = self.request_controller(url, client_ip)
                # if time() - START_TIME < CACHE_TIME:
                #     # START_TIME is not expired
                #     if cache_dict.get(url, None):
                #         # The asking url exist in cache_dict
                #         # First check if its timestamp is not expired
                #         timestamp = cache_dict[url]["timestamp"]
                #         if time() - timestamp < CACHE_TIME:
                #             proxy_url = cache_dict[url]["proxy_url"]
                #         else:
                #             cache_dict, START_TIME, proxy_url = self.request_controller(url, client_ip)
                #     else:
                #         cache_dict, START_TIME, proxy_url = self.request_controller(url, client_ip)
                # else:
                #     # START_TIME is expired get new cache_dict and new START_TIME
                #     cache_dict, START_TIME, proxy_url = self.request_controller(url, client_ip)
        else:
            raise Exception("Something goes wrong")
        return {
                    "proxy_url": proxy_url
                }


api.add_resource(ClientCachingDB, '/')
# TODO get as argument the ip of client or get it with some other way
if __name__ == '__main__':
    app.run(debug=True)
