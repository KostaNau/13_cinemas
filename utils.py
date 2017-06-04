import requests
import random
import json


def load_cookies(json_data: json) -> dict:
    cookies = json.load(json_data)
    return cookies


def load_user_proxy(proxy_data: bytes) -> list:
    user_data = []
    for item in proxy_data:
        user_data.append(item.strip())
    return user_data


def load_user_uagent(u_agent_data: bytes) -> list:
    user_data = []
    for item in u_agent_data:
        user_data.append(item.strip()[1:-1-1])
    return user_data


def get_raw_page(url: str,
                 session=None,
                 **kwargs
                 ) -> requests.models.Response:
    if session:
        response = session.get(url, **kwargs)
    else:
        response = requests.get(url, **kwargs)
    return response.content


def load_user_data(filepath: str,
                   proxy=False,
                   user_agent=False,
                   cookies=False
                   ) -> list:
    user_data = []
    try:
        with open(filepath, "r") as external_data:
            print(type(external_data))
            if cookies:
                user_data = load_cookies(external_data)
            elif proxy:
                user_data = load_user_proxy(external_data)
            elif user_agent:
                user_data = load_user_uagent(external_data)
        return user_data
    except TypeError:
        return None


def fetch_user_cookies(url: str) -> dict:
    with requests.Session() as cookies_request:
        response = cookies_request.get(url)
        user_cookies = response.cookies.get_dict()
        return user_cookies


def fetch_working_proxy(proxy_list: list) -> dict:
    url = "http://google.com"
    if proxy_list is None:
        return None
    while True:
        proxy = {"http": '{}'.format(random.choice(proxy_list))}
        try:
            response = requests.get(url, proxies=proxy, timeout=10)
            if response:
                break
        except (IOError, ConnectionResetError):
            pass
    return proxy
