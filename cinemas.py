import argparse
import random
import json


import requests
from bs4 import BeautifulSoup


AFISHA_URL = "https://www.afisha.ru/msk/schedule_cinema/"
KP_SEARCH_URL = "https://www.kinopoisk.ru/index.php"
CAPTCHA_PAGE_LENGTH = 14000


def parse_afisha(raw_page: bytes) -> list:
    afisha_movies = list()
    raw_soup = BeautifulSoup(raw_page, "html.parser")
    movies_pool = raw_soup.find_all(
                    "div", {
                            "class": "object s-votes-hover-area collapsed"
                            })
    for movie in movies_pool:
        title = movie.find("h3", {"class": "usetags"}).text
        cinemas = len(movie.find_all("td", {"class": "b-td-item"}))
        afisha_movies.append([title, cinemas])
    return afisha_movies


def parse_kinopoisk(raw_page: bytes) -> tuple:
    soup = BeautifulSoup(raw_page, "html.parser")
    if soup.find("span", {"class": "rating_ball"}):
        movie_rating = float(soup.find("span", {"class": "rating_ball"}).text)
    else:
        movie_rating = None

    if soup.find("span", {"class": "ratingCount"}):
        votes = soup.find("span", {"class": "ratingCount"}).text.split()
        votes_score = int("".jont(votes))
        print("DEBUG: ", votes_score)
        # if len(votes_score) >= 2:
        #     votes_score = int(votes_score[0] + votes_score[:1])
        # elif len(votes_score) == 1:
        #     votes_score = int(votes_score[0])
    else:
        votes_score = None
    return movie_rating, votes_score


def fetch_movies_data(movies,
                      u_agents=None,
                      proxies=None,
                      usr_cookies=None):

    with requests.Session() as kp_session:
        request_timeout = 10
        for movie in movies:
            title = movie[0]
            proxy = fetch_working_proxy(proxies) if proxies else None
            header = {"User-Agent": random.choice(u_agents)} if u_agents else None
            cookie = random.choice(usr_cookies) if usr_cookies else None
            movie_querry = {"kp_query": title, "first":  "yes"}
            movie_raw_page = kp_session.get(
                                        KP_SEARCH_URL,
                                        headers=header,
                                        params=movie_querry,
                                        cookies=cookie,
                                        proxies=proxy,
                                        timeout=request_timeout
                                        ).content
            rating, votes = parse_kinopoisk(movie_raw_page)
            if len(movie_raw_page) < CAPTCHA_PAGE_LENGTH:
                rating, votes = None, None
            movie.append(rating)
            movie.append(votes)

    return movies


def sort_by_cinemas(movies: list) -> list:
    return sorted(movies, key=lambda v: v[1], reverse=True)


def sort_by_rating(movies: list) -> list:
    return sorted(movies, key=lambda v: v[2], reverse=True)


def replace_none(movies: list) -> list:
    for data in movies:
        for i, _ in enumerate(data):
            if data[i] is None:
                data[i] = 0
    return movies


def pretty_console_print(movies: list) -> None:
    for movie in movies:
        print("Название фильма: {}".format(movie[0]))
        print("Идет в кинотеатрах (количество): {}".format(movie[1]))
        print("Рейтинг (кинопоиск): {}".format(movie[2]))
        print("Количество оценок (кинопоиск): {}".format(movie[3]))
        print('==========================================================')


def load_cookies(json_data: json) -> dict:
    try:
        cookies = json.load(json_data)
        return cookies
    except AttributeError:
        return None


def load_data(external_data: bytes) -> list:
    try:
        user_data = []
        for item in external_data:
            user_data.append(item.strip())
        return user_data
    except TypeError:
        return None


def get_raw_page(url: str, session=None, **kwargs) -> requests.models.Response:
    if session:
        return session.get(url, **kwargs).content
    return requests.get(url, **kwargs).content


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


def parse_args() -> argparse:
    parser = argparse.ArgumentParser(description="Geeks way to find movie for\
                                     the watching in a cinemas (only Moscow)")
    parser.add_argument("-q", "--quantity",
                        type=int,
                        default=10,
                        help="Quantity of movies for request (by default 10)"
                        )
    parser.add_argument("-ua", "--u_agent",
                        default=None,
                        help="Path to the custom user agents list")
    parser.add_argument("-p", "--proxies",
                        default=None,
                        help="Path to the user's proxies list")
    parser.add_argument("-c", "--cookies",
                        default=None,
                        help="Path to the user's cookies json")
    parser.add_argument("-r", "--rating",
                        action="store_true",
                        help="If option is specified, movies will sort by\
                        rating. By default, sort by cinemas")
    args = parser.parse_args()
    return args


def main():
    options = parse_args()

    user_agents = load_data(options.u_agent)
    proxies = load_data(options.proxies)
    usr_cookies = load_cookies(options.cookies)
    quantity = options.quantity
    sorting_by_rating = options.rating

    afisha_raw_page = get_raw_page(AFISHA_URL)
    afisha_movies_data = parse_afisha(afisha_raw_page)
    movies_sorted_by_cinemas = sort_by_cinemas(afisha_movies_data)[:quantity]

    print('Loading data from kinopoisk.ru it may take up a few minutes...')
    kp_movies_data = fetch_movies_data(movies_sorted_by_cinemas,
                                       u_agents=user_agents,
                                       proxies=proxies,
                                       usr_cookies=usr_cookies)

    movies_without_none = replace_none(kp_movies_data)
    if sorting_by_rating:
        pretty_console_print(sort_by_rating(movies_without_none))
    else:
        pretty_console_print(movies_without_none)


if __name__ == '__main__':

    main()
