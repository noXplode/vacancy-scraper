from django.shortcuts import render
# from django.http import HttpResponse

import requests
from bs4 import BeautifulSoup


def index(request):

    r = RabotauaScraper(search_string='python')
    resR = r.scrape()
    w = WorkuaScraper(search_string='python')
    resW = w.scrape()
    h = HHruScraper(search_string='python')
    resH = h.scrape()

    context = {'resR': resR,
               'resW': resW,
               'resH': resH}

    return render(request, 'vscraper/scraper.html', context)


class RabotauaScraper:

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}

    def __init__(self, search_string):
        self.search_string = search_string
        self.scrape_url = f'https://rabota.ua/zapros/{search_string}/украина?period=3'
        self.res = []

    def scrape(self, url=None):
        if url is None:
            r = requests.get(self.scrape_url, headers=self.headers)
        else:
            r = requests.get(url, headers=self.headers)
        text = r.text
        soup = BeautifulSoup(text, "lxml")
        tab = soup.table    # vacancies table

        trs = tab.findAll('tr')  # looking for rows
        for tr in trs:
            try:
                title = tr.find('p', 'card-title').find('a', 'ga_listing').string.strip()
                url = 'https://rabota.ua' + tr.find('p', 'card-title').find('a', 'ga_listing').get('href')
                company = tr.find('p', 'company-name').find('a', 'company-profile-name').string.strip()
                # print(f'{title}, {url}, {company}')
                try:
                    location = tr.find('span', 'location').string.strip()
                except Exception:
                    location = ''
                try:
                    salary = tr.find('span', 'salary').string.strip()
                except Exception:
                    salary = ''
                try:
                    shdescr = tr.find('div', 'card-description').string.strip()
                except Exception:
                    shdescr = ''
            except AttributeError:
                if tr.find('dd', 'nextbtn').find('a'):
                    nextpage_url = 'https://rabota.ua' + tr.find('dd', 'nextbtn').find('a').get('href')
                    print(nextpage_url)
                    self.scrape(nextpage_url)
            else:
                self.res.append({'title': title,
                                 'url': url,
                                 'company': company,
                                 'location': location,
                                 'salary': salary,
                                 'shdescr': shdescr})
        return self.res


class WorkuaScraper:

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}

    def __init__(self, search_string):
        self.search_string = search_string
        self.scrape_url = f'https://www.work.ua/jobs-{search_string}/?days=123'
        self.res = []

    def scrape(self, url=None):
        if url is None:
            r = requests.get(self.scrape_url, headers=self.headers)
        else:
            r = requests.get(url, headers=self.headers)
        text = r.text
        soup = BeautifulSoup(text, "lxml")

        tab = soup.find('div', id='pjax-job-list')    # vacancies table

        trs = tab.findAll('div', 'job-link')  # looking for rows
        for tr in trs:
            try:
                title = tr.find('h2').find('a').string.strip()
                url = 'https://work.ua' + tr.find('h2').find('a').get('href')
                company = tr.find('div', 'add-top-xs').find('b').string.strip()
                # print(f'{title}, {url}, {company}')
                try:
                    loc = tr.find('div', 'add-top-xs').findAll('span')
                    location = loc[-1].string.strip()
                except Exception:
                    location = ''
                try:
                    salary = tr.find('div', attrs={'class': None}).find('b').string.strip()
                except Exception:
                    salary = ''
                try:
                    shdescr = tr.find('p', 'overflow text-muted add-top-sm add-bottom')
                    shdescr.a.extract()
                    shdescr.br.extract()
                    shdescr = shdescr.get_text().strip()
                except Exception:
                    shdescr = ''
            except AttributeError:
                continue
            else:
                # print(f'{title}, {url}, {company}, {location}, {salary}, {shdescr}')
                self.res.append({'title': title,
                                 'url': url,
                                 'company': company,
                                 'location': location,
                                 'salary': salary,
                                 'shdescr': shdescr})

        nav = tab.find('nav').find('ul', 'pagination hidden-xs')
        try:
            nxt = nav.findAll('li')[-1].find('a').get('href')
            print(nxt)
        except AttributeError:
            print('work.ua last page scraped')
        else:
            nextpage_url = 'https://work.ua' + nxt
            self.scrape(nextpage_url)

        return self.res


class HHruScraper:

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}

    def __init__(self, search_string):
        self.search_string = search_string
        self.scrape_url = f'https://hh.ru/search/vacancy?text={search_string}&area=5'
        self.res = []

    def scrape(self, url=None):
        if url is None:
            r = requests.get(self.scrape_url, headers=self.headers)
        else:
            r = requests.get(url, headers=self.headers)
        text = r.text
        soup = BeautifulSoup(text, "lxml")
        tab = soup.find('div', 'vacancy-serp')    # vacancies table

        trs = tab.findAll('div', 'vacancy-serp-item')  # looking for rows
        for tr in trs:
            try:
                title = tr.find('div', 'vacancy-serp-item__row_header').find('div', 'vacancy-serp-item__info').find('a').string.strip()
                url = tr.find('div', 'vacancy-serp-item__row_header').find('div', 'vacancy-serp-item__info').find('a').get('href')
                company = tr.find('div', 'vacancy-serp-item__meta-info').find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).string.strip()
                # print(f'{title}, {url}, {company}')
                try:
                    location = tr.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).string.strip()
                except Exception:
                    location = ''
                try:
                    salary = tr.find('div', 'vacancy-serp-item__row_header').find('div', 'vacancy-serp-item__sidebar').find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).string.strip()
                except Exception:
                    salary = ''
                try:
                    shdescr = tr.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).get_text()
                    shdescr = shdescr + ' ' + tr.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).get_text()
                except Exception:
                    shdescr = ''
            except AttributeError:
                continue
            else:
                self.res.append({'title': title,
                                 'url': url,
                                 'company': company,
                                 'location': location,
                                 'salary': salary,
                                 'shdescr': shdescr})

        nav = soup.find('div', attrs={'data-qa': 'pager-block'})
        try:
            nxt = nav.find('a', attrs={'data-qa': 'pager-next'}).get('href')    # not working, loads only 1st page
            print(nxt)
        except AttributeError:
            print('hh.ru last page scraped')
        else:
            nextpage_url = 'https://hh.ru' + nxt
            self.scrape(nextpage_url)

        return self.res
