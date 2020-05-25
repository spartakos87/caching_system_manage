from flask import Flask, request
from flask_restful import Resource, Api
from time import time
from random import randint
from math import factorial, pow
from requests import get

app = Flask(__name__)
api = Api(app)
# START_TIME = 0
# CACHE_TIME = 10
# cache_dict = {}
# # TODO parse proxy_to_clients as file or as argument
# proxy_to_clients = {}
# proxy_list = []
# LEN_PROXIES = len(proxy_to_clients)
# THREHOLD = 0.8
# LAMBDA = 30
# E = 2.718


class CachingDB(Resource):
    def __init__(self):
        self.on_deman_caching_datastructure = {}  # A dict with key the URI and R the rate (# of requests )
        self.proxy_list = []  # Initialize in the begin of the rest api
        self.LEN_PROXIES = len(self.proxy_list)
        self.cache_dict = {}
        self.THREHOLD = 0.8
        self.LAMBDA = 30
        self.E = 2.718


    def popularity_probability(self, r):
        """

        :param R:
        :return:
        """
        g = 0
        for i in range(r+1):
            self.g += (pow(self.LAMBDA, i) * pow(self.E, -self.LAMBDA)) / factorial(i)
        return g

    def on_demand_caching(self, uri):
        """
        Implement the On-demand caching algorithm base to paper,
         DOI: http://dx.doi.org/10.1145/2836183.2836189 (section 3.1 )

        :return:
        """
        if bool(self.on_deman_caching_datastracture):
            # Case the data structure is not empty
            if self.on_deman_caching_datastructure.get(uri, None):
                r = self.on_deman_caching_datastructure[uri]
                if self.popularity_probability(r+1) > self.THREHOLD:
                    for proxy in self.proxy_list:
                        proxy = {"http": proxy}
                        res_via_proxy = get(uri, proxies=proxy)
                        if res_via_proxy.status_code == 200:
                            print("Cach object {} in proxy {}".format(uri, proxy))
                            # Update self.cache_dict
                            self.update_cache_dict(uri, proxy)
                        else:
                            print("Something goes wrong")
                else:
                    self.on_deman_caching_datastructure[uri] = r + 1

    def clean_cache_dict(self, cache_dict):
        # TODO remove it we don't need it
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

    # def export_data(self, proxy_url, cache_dict, START_TIME):
    def export_data(self, proxy_url):
        """

        :param proxy_url: a list of proxies
        :param cache_dict:
        :param START_TIME:
        :return:
        """
        if len(proxy_url) == 1:
            proxy_url = proxy_url[0]
        else:
            proxy_url = proxy_url[randint(0, len(proxy_url))]
        return {
                 "proxy_url": proxy_url,
                 "cache_dict": self.cache_dict
                 # "START_TIME": START_TIME
                                    }

    def update_cache_dict(self, request_url, proxy_url):
        """

        :param request_url:
        :param proxy_url:
        :return:
        """
        temp_proxies_list = self.cache_dict[request_url]
        self.cache_dict[request_url] = temp_proxies_list.append(proxy_url)
        # return {
        #             request_url: {
        #                             # "timestamp": time(),
        #                             "proxy_url": proxy_url
        #                                         }
        #             }

    def post(self):
        """
        Example how to call it post('http://localhost:5000',json={"A":1,"B":2}).json()
        As input will get a dict with key the url which client is requested and the ip of client
        :return:
        """
        # global START_TIME, cache_dict
        post_data = request.get_json()
        request_url = post_data.get("url", None)
        # Call on demand caching
        self.on_demand_caching(request_url)
        # client_ip = post_data.get("client_ip", None)
        if request_url is None:
            raise Exception("There isn't url")
        # Check if cache_dict is empty
        if bool(self.cache_dict):
            # cache_dict is not empty
            # Check if the request url is in cache_dict
            if self.cache_dict.get(request_url, None):
                # return_json = self.export_data(self.cache_dict[request_url]["proxy_url"], self.cache_dict)
                return_json = self.export_data(self.cache_dict[request_url]["proxy_url"])
            else:
                # Get random proxy
                proxy_url = self.proxy_list[randint(0, self.LEN_PROXIES)]
                # proxy_url = proxy_to_clients.get(client_ip, None)
                # START_TIME = time()
                # self.cache_dict.update(self.update_cache_dict(request_url))
                self.update_cache_dict(request_url, proxy_url)
                # return_json = self.export_data(proxy_url, self.cache_dict)
                return_json = self.export_data(proxy_url)
            # if time() - START_TIME < CACHE_TIME:
            #     # The START_TIME is not expired
            #     # Check if the request url is in cache_dict
            #     if cache_dict.get(request_url, None):
            #         # First check if its timestamp is not expired
            #         timestamp = cache_dict[request_url]["timestamp"]
            #         if time() - timestamp < CACHE_TIME:
            #             # Is not expired
            #             return_json = self.export_data(cache_dict[request_url]["proxy_url"], cache_dict, START_TIME)
            #         else:
            #             # Has expired
            #             proxy_url = proxy_to_clients.get(client_ip, None)
            #             cache_dict.update(self.update_cache_dict(request_url, proxy_url))
            #     else:
            #         proxy_url = proxy_to_clients.get(client_ip, None)
            #         cache_dict.update(self.update_cache_dict(request_url, proxy_url))
            #         return_json = self.export_data(proxy_url, cache_dict, START_TIME)
            # else:
            #     # The START_TIME is expired
            #     # Clean cache_dict
            #     cache_dict = self.clean_cache_dict(cache_dict)
            #     if cache_dict.get(request_url, None):
            #         return_json = self.export_data(cache_dict[request_url]["proxy_url"], cache_dict, START_TIME)
            #     else:
            #         proxy_url = proxy_to_clients.get(client_ip, None)
            #         cache_dict.update(self.update_cache_dict(request_url, proxy_url))
            #         return_json = self.export_data(proxy_url, cache_dict, START_TIME)
        else:
            # The cache_dict is empty
            # Get random proxy
            proxy_url = self.proxy_list[randint(0, self.LEN_PROXIES)]
            # proxy_url = proxy_to_clients.get(client_ip, None)
            # START_TIME = time()
            # self.cache_dict.update(self.update_cache_dict(request_url))
            self.update_cache_dict(request_url, proxy_url)
            # return_json = self.export_data(proxy_url, self.cache_dict)
            return_json = self.export_data(proxy_url)
        return return_json


api.add_resource(CachingDB, '/')

if __name__ == '__main__':
    app.run(debug=True)
