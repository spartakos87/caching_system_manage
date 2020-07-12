from flask import Flask, request
from flask_restful import Resource, Api
from time import time
from random import randint
from math import factorial, pow
from requests import get
import json
import os
import fcntl

app = Flask(__name__)
api = Api(app)
# START_TIME = 0
# CACHE_TIME = 10
#cache_dict = {}
# # TODO parse proxy_to_clients as file or as argument
# proxy_to_clients = {}
# proxy_list = []
# LEN_PROXIES = len(proxy_to_clients)
# THREHOLD = 0.8
# LAMBDA = 30
# E = 2.718





class CachingDB(Resource):
    def __init__(self):
        #self.on_deman_caching_datastructure = {}  # A dict with key the URI and R the rate (# of requests )
        self.proxy_list = ['http://localhost:7777', 'http://localhost:7778']  # Initialize in the begin of the rest api
        self.LEN_PROXIES = len(self.proxy_list)
        self.cache_dict = {}
        self.THREHOLD = 0.8
        self.LAMBDA = 30
        self.E = 2.718

    def read_write_json(self,f,flag=True,input_data=None):
        if flag:
           with open(f+'.json') as o:
               fcntl.flock(o, fcntl.LOCK_EX)
               data = json.load(o)
               fcntl.flock(o, fcntl.LOCK_UN)
           return data
        else:
            with open(f+'.json','w') as o:
                fcntl.flock(o, fcntl.LOCK_EX)
                json.dump(input_data,o)
                fcntl.flock(o, fcntl.LOCK_UN)
    def popularity_probability(self, r):
        """

        :param R:
        :return:
        """
        g = 0
        for i in range(r+1):
            g += (pow(self.LAMBDA, i) * pow(self.E, -self.LAMBDA)) / factorial(i)
        return g

    def on_demand_caching(self, uri, cache_dict):
        """
        Implement the On-demand caching algorithm base to paper,
         DOI: http://dx.doi.org/10.1145/2836183.2836189 (section 3.1 )

        :return:
        """
        on_deman_caching_datastructure = self.read_write_json('on_deman_caching_datastructure')
        if bool(on_deman_caching_datastructure):
            # Case the data structure is not empty
            if on_deman_caching_datastructure.get(uri, None):
                r = on_deman_caching_datastructure[uri]
                if self.popularity_probability(r+1) > self.THREHOLD:
                    for proxy in self.proxy_list:
                        proxy = {"http": proxy}
                        # res_via_proxy = get(uri, proxies=proxy)
                        # if res_via_proxy.status_code == 200:
                        #     # Update self.cache_dict
                        #     self.update_cache_dict(uri, proxy, cache_dict)
                        self.update_cache_dict(uri, proxy, cache_dict)
                        on_deman_caching_datastructure[uri] = r+1
                        self.read_write_json('on_deman_caching_datastructure', False, on_deman_caching_datastructure)
                        # else:
                        #     print("Something goes wrong")
                else:
                    on_deman_caching_datastructure[uri] = r + 1
                    self.read_write_json('on_deman_caching_datastructure', False, on_deman_caching_datastructure)
            else:
                on_deman_caching_datastructure[uri] = 1
                self.read_write_json('on_deman_caching_datastructure', False, on_deman_caching_datastructure)
        else:
            on_deman_caching_datastructure[uri] = 1
            self.read_write_json('on_deman_caching_datastructure', False, on_deman_caching_datastructure)

    # def clean_cache_dict(self, cache_dict):
    #     # TODO remove it we don't need it
    #     """
    #     Remove the caching objects which theis timestamps are expired
    #
    #     :param cache_dict:
    #     :return:
    #     """
    #     try:
    #         cache_dict = list(filter(lambda x: time()-x[1]["timestamp"] < CACHE_TIME, cache_dict.items()))
    #         return cache_dict
    #     except:
    #         return cache_dict


    def export_data(self, proxy_url, cache_dict):
        """

        :param proxy_url: a list of proxies
        :param cache_dict:
        :param START_TIME:
        :return:
        """
#        if len(proxy_url) == 1:
#            proxy_url = proxy_url[0]
#       else:
#            proxy_url = proxy_url[randint(0, len(proxy_url)-1)]
        return {
                 "proxy_url": proxy_url,
                 "cache_dict": cache_dict
                                    }

    def update_cache_dict(self, request_url, proxy_url, cache_dict):
        """

        :param request_url:
        :param proxy_url:
        :return:
        """
        if cache_dict.get(request_url, None):
           temp_proxies_list = cache_dict[request_url]
        else:
           temp_proxies_list = []
        temp_proxies_list.append(proxy_url)
        cache_dict[request_url] = temp_proxies_list
        self.read_write_json('cache_dict', False, cache_dict)

    def post(self):
        """
        Example how to call it post('http://localhost:5000',json={"A":1,"B":2}).json()
        As input will get a dict with key the url which client is requested and the ip of client
        :return:
        """
        post_data = request.get_json()
        request_url = post_data.get("url", None)
        # Call on demand caching
        # self.on_demand_caching(request_url)
        # client_ip = post_data.get("client_ip", None)
        if request_url is None:
            raise Exception("There isn't url")
        # Check if cache_dict is empty
        cache_dict = self.read_write_json('cache_dict')
        self.on_demand_caching(request_url, cache_dict)
        if bool(cache_dict):
            # cache_dict is not empty
            # Check if the request url is in cache_dict
            if cache_dict.get(request_url, None):
                return_json = self.export_data(cache_dict[request_url], cache_dict)
            else:
                # Get random proxy
                proxy_url = self.proxy_list[randint(0, self.LEN_PROXIES-1)]
                self.update_cache_dict(request_url, proxy_url, cache_dict)
                return_json = self.export_data(proxy_url, cache_dict)
        else:
            # The cache_dict is empty
            # Get random proxy
            proxy_url = self.proxy_list[randint(0, self.LEN_PROXIES-1)]
            self.update_cache_dict(request_url, proxy_url, cache_dict)
            # return_json = self.export_data(proxy_url, self.cache_dict)
            return_json = self.export_data(proxy_url, cache_dict)
        return return_json


api.add_resource(CachingDB, '/')

if __name__ == '__main__':
    app.run(debug=True)
