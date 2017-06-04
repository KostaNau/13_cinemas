import argparse
import random
from collections import defaultdict

import utils
import requests
from bs4 import BeautifulSoup


AFISHA_URL = "https://www.afisha.ru/msk/schedule_cinema/"
KP_SEARCH_URL = "https://www.kinopoisk.ru/index.php"
CAPTCHA_PAGE_LENGTH = 14000


def parse_afisha(raw_page: bytes, quantity: int) -> defaultdict:
    afisha_movies = defaultdict(list)
    raw_soup = BeautifulSoup(raw_page, "html.parser")
    movies_pool = raw_soup.find_all(
                    "div", {
                            "class": "object s-votes-hover-area collapsed"
                            })
    for movie in movies_pool[:quantity]:
        title = movie.find("h3", {"class": "usetags"}).text
        cinemas = len(movie.find_all("td", {"class": "b-td-item"}))
        afisha_movies[title].append(cinemas)
    return afisha_movies


def parse_kinopoisk(raw_page: bytes) -> tuple:
    soup = BeautifulSoup(raw_page, "html.parser")
    if soup.find("span", {"class": "rating_ball"}):
        movie_rating = float(soup.find("span", {"class": "rating_ball"}).text)
    else:
        movie_rating = None

    if soup.find("span", {"class": "ratingCount"}):
        votes_score = soup.find("span", {"class": "ratingCount"}).text.split()
        if len(votes_score) == 2:
            votes_score = int(votes_score[0] + votes_score[1])
        elif len(votes_score) == 1:
            votes_score = int(votes_score[0])
    else:
        votes_score = None
    return movie_rating, votes_score


def fetch_afisha_movies(raw_movies_page: bytes, quantity=5) ->defaultdict:
    movies = parse_afisha(raw_movies_page, quantity)
    sorted_by_cinemas = sort_cinemas(movies)
    return sorted_by_cinemas


def sort_cinemas(movies, afisha=True):
    sorted_movies = defaultdict(list)
    sorted_list = sorted(movies.items(), key=lambda v: v[1], reverse=True)
    for movie in sorted_list:
        title = movie[0]
        cinemas = int(movie[1][0])
        sorted_movies[title].append(cinemas)
    return sorted_movies


def sort_movies(movies: defaultdict,
                rating=False,
                afisha=False
                ) -> defaultdict:

    sorted_movies = defaultdict(list)
    if rating:
        movies_without_none = replace_none(movies)
        sorted_list = sorted(movies_without_none.items(), key=lambda v: v[1][1], reverse=True)
    else:
        sorted_list = sorted(movies.items(), key=lambda v: v[1], reverse=True)
    for movie in sorted_list:
        title = movie[0]
        cinemas, rating, votes = movie[1]
        sorted_movies[title].append(cinemas)
        sorted_movies[title].append(rating)
        sorted_movies[title].append(votes)
    return sorted_movies


def replace_none(movies):
    for title, data in movies.items():
        for i in range(len(data)):
            if data[i] is None:
                movies[title][i] = 0
    return movies


def output_movies(movies: defaultdict, sorting_by_rating: bool) -> None:
    if sorting_by_rating:
        sorted_by_rating = sort_movies(movies, sorting_by_rating)
        pretty_console_print(sorted_by_rating)
    else:
        pretty_console_print(movies)


def pretty_console_print(movies: defaultdict) -> None:
    for movie_title, movie_data in movies.items():
        print("Название фильма: {}".format(movie_title))
        print("Идет в кинотеатрах (количество): {}".format(movie_data[0]))
        print("Рейтинг (кинопоиск): {}".format(movie_data[1]))
        print("Количество оценок (кинопоиск): {}".format(movie_data[2]))
        print('==========================================================')


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
    user_agents = utils.load_user_data(options.u_agent, user_agent=True)
    proxies = utils.load_user_data(options.proxies, proxy=True)
    usr_cookies = utils.load_user_data(options.cookies, cookies=True)
    quantity = options.quantity
    sorting_by_rating = options.rating

    afisha_raw_page = utils.get_raw_page(AFISHA_URL)
    afisha_movies_data = fetch_afisha_movies(afisha_raw_page,
                                             quantity=quantity
                                             )
    print('Loading data from kinopoisk.ru it may take up a few minutes...')

    with requests.Session() as kp_session:
        request_timeout = 10
        for title in afisha_movies_data.keys():
            if proxies:
                proxy = utils.fetch_working_proxy(proxies)
            else:
                proxy = None
            if user_agents:
                headers = {"User-Agent": random.choice(user_agents)}
            else:
                headers = None
            if usr_cookies:
                cookie = random.choice(usr_cookies)
            else:
                cookie = None
            movie_querry = {"kp_query": title, "first":  "yes"}
            movie_raw_page = kp_session.get(
                                        KP_SEARCH_URL,
                                        headers=headers,
                                        params=movie_querry,
                                        cookies=cookie,
                                        proxies=proxy,
                                        timeout=request_timeout
                                        ).content
            rating, votes = parse_kinopoisk(movie_raw_page)
            if len(movie_raw_page) < CAPTCHA_PAGE_LENGTH:
                print("{} - can't fetch information, kinopoisk return captcha page".format(title))
                rating, votes = 0, 0
            afisha_movies_data[title].append(rating)
            afisha_movies_data[title].append(votes)
    output_movies(afisha_movies_data, sorting_by_rating)

if __name__ == '__main__':

    main()
