# Cinemas

## Description
The script collect and console print information about movies are going in a cinemas at now (only Moscow, Russia) from [afisha.ru](https://www.afisha.ru/msk/schedule_cinema/) (about movies are going in a cinemas and number of cinemas for each movie) and from [kinopoisk.ru](https://www.kinopoisk.ru) (about movie rating and quantity of votes).


## How to use
Just run the script ```python3 cinemas.py```. 
By default script will try to collect information about up 10 movies. If you would specify quantitiy of movies or use your proxies, user agents or cookies, you should running the script with options:


Name | Type | Key | Desription
--- | --- | --- | ---|
**Quantity** | int | `-q`| Quantity of movies for requests
**User Agent** | File object | `-ua`| Path to the custom user agents list
**Proxies** | File object | `-p`| Path to the user's proxies list
**Cookies** | File object | `-c`|  Path to the user's cookies JSON file
**Rating** | Bool | '-r'| If specify sort by movie's rating. By default sort by cinemas.

**User data requirement:** *Each line must contain only one item (user agent or proxy), cookies must be JSON file.*

### Examples
```python cinemas.py -q 5 -r -ua /some/path -p /some/path -c /some/path```

```
Название фильма: Нелюбовь
Идет в кинотеатрах (количество): 118
Рейтинг (кинопоиск): 7.72
Количество оценок (кинопоиск): 2843
==========================================================
Название фильма: Чудо-женщина
Идет в кинотеатрах (количество): 162
Рейтинг (кинопоиск): 7.146
Количество оценок (кинопоиск): 13073
==========================================================
Название фильма: Пираты Карибского моря: Мертвецы не рассказывают сказки
Идет в кинотеатрах (количество): 171
Рейтинг (кинопоиск): 6.693
Количество оценок (кинопоиск): 32159
==========================================================
```

### Requirements
Install the dependencies from requirements.txt using pip:

```pip install -r requirements.txt```


# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
