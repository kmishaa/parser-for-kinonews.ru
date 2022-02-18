import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import subprocess

URL = 'https://www.kinonews.ru/top100/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.1.932 Yowser/2.5 Safari/537.36',
               'accept': '*/*'}
HOST = 'https://www.kinonews.ru'
FILE = 'results_kinonews.csv'


def get_html(url):
    r = requests.get(url, headers = HEADERS)
    return r

def get_genres(soup):
    genre = ''
    all_spans = soup.find_all('span')
    for span in all_spans:
        genre += span.get_text() + ', '
    return genre[:len(genre) - 2]

def get_number(string):
    result = ''
    for char in string:
        if (char.isdigit()):
            result += char
    return int(result)

def get_directors(directors):
    director = ''
    for direct in directors:
        director += direct.get_text() + ', '
    return director[:len(director) - 2]

def get_movie_content(html, rating):
    soup_movie = BeautifulSoup(html, 'html.parser')

    director = ''
    all_tr = soup_movie.find('table', class_='tab-film').find_all('tr')
    for tr in all_tr:
        if not(tr.get_text().find('Режиссеры:') == -1):
            director = get_directors(tr.find_all('span'))
        elif not(tr.get_text().find('Страна:') == -1):
            country = tr.find_all('td')[1].get_text()
        elif not(tr.get_text().find('Жанр:') == -1):
            genre = get_genres(tr)
        elif not(tr.get_text().find('Год выпуска:') == -1):
            year = tr.find('a').get_text()

    review = 0
    reviews = soup_movie.find('div', class_='game_menu relative').find_all('div')
    for r in reviews:
        re = r.find_all('div')
        for rev in re:
            if not(rev.get_text().find('отзывов:') == -1): 
                if rev.find('a'):
                    review = rev.find('a').get_text()
                else:
                    review = rev.get_text()
    
            
    
    movie = [{
        'title': soup_movie.find('h1', class_='film').get_text(),
        'director': director,
        'country': country,
        'genre': genre,
        'year': int(year),
        'rating': int(rating[:len(rating)-1]),
        'mark': float(soup_movie.find('span', class_='numraitview').get_text()),
        'reviews': get_number(review)
    }]
        
    return movie
        

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    movies = []
    all_titles = soup.find_all('div', class_='bigtext')
    all_content = soup.find_all('div', class_='relative')
    rating = soup.find_all('div', class_='bigtext')

    for title_soup in range (0, len(all_titles)):
        if (title_soup % 10 == 0):
            print (f'Обработано {title_soup + 10} фильмов из {len(all_titles)}')
        link = HOST + all_titles[title_soup].find('a', class_='titlefilm').get('href')

        html_movie = get_html(link)
        movie = get_movie_content(html_movie.content, rating[title_soup].find('b').get_text())
        movies.extend(movie)
        
    
    return movies

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Режиссёр', 'Страна производства', 'Жанр', 'Год выхода', 'Место в рейтинге', 'Средняя оценка пользователей сайта', 'Количество отзывов'])
        for item in items:
            writer.writerow([item['title'], item['director'], item['country'], item['genre'], item['year'], item['rating'], item['mark'], item['reviews']])


def parse():
    print ('Установка соединения...')
    movies = []
    html = get_html(URL)
    if (html.status_code == 200):
        for page in range (1, 11):
            print (f'Парсинг страницы {page} из 10...')
            if (page != 0):
                html = get_html(URL[:-1] + '_p' + f'{page}' + '/')

            movies += get_content(html.text)
        save_file(movies, FILE)
        print (f'Всего обработано {len(movies)} фильмов')
        
        os.startfile(FILE) #запуск созданного excel-файла для Windows

        #subprocess.call(['open', FILE]) #запуск созданного excel-файла для Mac os
    else:
        print ('Ошибка соединения(')

parse()
