import time
import random
from collections import defaultdict

import requests
from google import google
from bs4 import BeautifulSoup


AFISHA_URL = 'https://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_SERACH_URL = 'https://www.kinopoisk.ru/index.php'
COOKIES = {
    "PHPSESSID": "c645bf6910a9b7d4f005d80f7ddf18ce",
    "_ym_isad": "2",
    "_ym_uid": "1491905531975794387",
    "_ym_visorc_22663942": "b",
    "_ym_visorc_40504750": "b",
    "csrftoken": "s%3AdNDFl6r5hRUIWgVabYjlOl4e.xMjF6lDd0sNzEqnCjPmg0uCwnaJv9AgEjUkBwNR3A2g",
    "fuid01": "58c3c6655d137eab.cGsZ55hL7PyzJa7thCV0B9EYfxUBo75lKMlk_E-Eek5j6wG8lf4TShBOCLvP1jJSKFLXcvkqbGuvu31QQR6Ff5_M02_n7poZLb1e4m53fbJcFQnUHCcuXqWnOQ1DSVzI",
    "last_visit": "2017-05-18+23%3A04%3A25",
    "my_perpages": "%5B%5D",
    "session_key": "eyJzZWNyZXQiOiJxWkhHZGVEYnh1VmZqemstTkczSjd1QTYiLCJfZXhwaXJlIjoxNDk1MTkwMDMzMjU4LCJfbWF4QWdlIjo4NjQwMDAwMH0=",
    "session_key.sig": "md-aLCOZVKV127MkzBqL6Beiwjs",
    "user-geo-city-id": "1",
    "user-geo-country-id": "2",
    "user-geo-region-id": "213",
    "yandex_gid": "213",
    "yandexuid": "2235172201489225301"
}


def fetch_proxy(proxy_list):
    proxy = None
    while True:
        url = 'http://google.com'
        proxy = {"http": '{}'.format(random.choice(proxy_list))}
        try:
            response = requests.get(url, proxies=proxy)
            print('RESPONSE ', response)
            if response.status_code == 200:
                break
        except IOError:
            print('Not working')
        except ConnectionResetError:
            print('Not working')
    print(proxy)
    return proxy


def load_user_proxies(filepath):
    proxies_stack = []
    with open(filepath, 'r') as proxies_pool:
        for proxy in proxies_pool:
            if proxy:
                proxies_stack.append(proxy.strip())
    return proxies_stack


def load_user_agent(filepath):
    user_agent_stack = []
    with open(filepath, 'r') as user_agent_pool:
        for user_agent in user_agent_pool:
            if user_agent:
                user_agent_stack.append(user_agent.strip()[1:-1-1])
    return user_agent_stack


def get_http_response(url, requests_session=None, **kwargs):
    if requests_session:
        result = requests_session.get(url, **kwargs)
        return result.content
    else:
        result = requests.get(url, **kwargs)
        return result.content


def ask_google(movie_title):
    kinopoisk_string = ' Кинопоиск'
    search_result = google.search(movie_title + kinopoisk_string)
    movie_url = search_result[0].link
    return movie_url


def parse_afisha_page(url) -> defaultdict:
    raw_html = get_http_response(url)
    movies = defaultdict(list)
    raw_soup = BeautifulSoup(raw_html, 'html.parser')
    movies_pool = raw_soup.find_all(
                    'div', {
                            'class': 'object s-votes-hover-area collapsed'
                            })
    for movie in movies_pool:
        title = movie.find('h3', {'class': 'usetags'}).text
        cinemas = len(movie.find_all('td', {'class': 'b-td-item'}))
        movies[title].append(cinemas)
    return movies


def fetch_movie_rating(session, **kwargs) -> list:
    raw_movie_data = get_http_response(KINOPOISK_SERACH_URL, session, **kwargs)
    soup = BeautifulSoup(raw_movie_data, 'html.parser')
    movie_rating = soup.find('span', {'class': 'rating_ball'}).text
    votes_score = soup.find('span', {'class': 'ratingCount'}).text.split()
    print(votes_score)
    if len(votes_score) == 2:
        votes_score = votes_score[0] + votes_score[1]
    else:
        votes_score = votes_score[0]
    return movie_rating, votes_score


def get_top10_movie_by_rating(movies: defaultdict):
        sorted_movies = sorted(movies.items(), key=lambda movie: movie[1], reverse=True)
        top10_movies = sorted_movies[:10]
        return top10_movies


def output_movies_to_console(movies):
    for title, info in movies.items():
        print('Movie: {}, Rating: {}',format(title, info[1]))
        print('==============================================================')


def main():
    movies = parse_afisha_page(AFISHA_URL)
    print(movies)
    proxy_stack = load_user_proxies('proxy_hidemy_https.txt')
    user_agent_stack = load_user_agent('user_agents.txt')
    with requests.Session() as kinopoisk_session:
        for i in range(3):
            for title in movies.keys():
                proxy = fetch_proxy(proxy_stack)
                print('MAIN FUNCTION ', proxy)
                headers = {'User-Agent': random.choice(user_agent_stack)}
                movie_query = {'kp_query': title, 'first':  'yes'}
                rating, votes = fetch_movie_rating(
                                                   kinopoisk_session,
                                                   headers=headers,
                                                   params=movie_query,
                                                   cookies=COOKIES,
                                                   proxies=proxy,
                                                   )
                movies[title].append(rating)
                movies[title].append(votes)
                print(title, movies[title])
                print('Sleeping 10 sec....')
                time.sleep(10)
    output_movies_to_console(get_top10_movie_by_rating(movies))


if __name__ == '__main__':

    main()
