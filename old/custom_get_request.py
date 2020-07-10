import sys
from requests import post, get

client_ip = ""

def custom_get(url):
    """

    :param url:
    :return:
    """
    res = post(client_ip, json={"request_url": url})
    if res.status_code == 200:
        proxy_url = res.json()["proxy_url"]
        proxy = {"http": proxy_url}
        res_via_proxy = get(url, proxies=proxy)
        if res_via_proxy.status_code == 200:
            print("OK")
        else:
            print("Something goes wrong")


if __name__ == "__main__":
    url = sys.argv[1]
