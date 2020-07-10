from flask import Flask, request
from flask_restful import Resource, Api
from time import time
from requests import post
from random import randint
import json

app = Flask(__name__)
api = Api(app)
START_TIME = 0
CACHE_TIME = 10
# cache_dict = {}
controller_ip = "http://127.0.0.1:5000/"
client_ip = ""


class ClientCachingDB(Resource):
    def read_write_json(self, f, flag=True, input_data=None):
        if flag:
            with open(f+'.json') as o:
                data = json.load(o)
                return data
        else:
            with open(f+'.json', 'w') as o:
                json.dump(input_data, o)

    def request_controller(self, url, client_ip):
        """

        :return:
        """
        controller_data = post(controller_ip, json={"url": url, "client_ip": client_ip}).json()
        print("CONTROLLER DATA--->", controller_data)
        cache_dict = controller_data["cache_dict"]
        self.read_write_json('client_cache', False, cache_dict)
        proxy_url = controller_data["proxy_url"]
        return cache_dict, proxy_url

    def post(self):
        cache_dict = self.read_write_json('client_cache')
        print("PPPP===>", cache_dict)
        post_data = request.get_json()
        if post_data.get("request_url", None):
            url = post_data["request_url"]
            if not bool(cache_dict):
                # cache dict is empty
                cache_dict, proxy_url = self.request_controller(url, client_ip)
                print("LL===>",cache_dict)
            else:
                if cache_dict.get(url, None):
                    proxy_url_lst = cache_dict[url]
                    proxy_url = proxy_url_lst[randint(0, len(proxy_url_lst)-1)]
                else:
                    cache_dict, proxy_url = self.request_controller(url, client_ip)
        else:
            raise Exception("Something goes wrong")
        return {
                    "proxy_url": proxy_url
                }


api.add_resource(ClientCachingDB, '/')
# TODO get as argument the ip of client or get it with some other way
if __name__ == '__main__':
    app.run(debug=True,port=5001)
