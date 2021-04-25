from typing import List

import requests
from bs4 import BeautifulSoup

from django.shortcuts import render

from .forms import SearchForm


def index(request):

    if request.GET and 'search_string' in request.GET:
        form = SearchForm(request.GET)

        if form.is_valid():
            search_string = form.cleaned_data['search_string']
            q_type = int(form.cleaned_data['q_choice'])

            r = RabotauaScraper(search_string=search_string, q_type=q_type)
            resR = r.scrape()
            urlR = r.scrape_url
            w = WorkuaScraper(search_string=search_string, q_type=q_type)
            resW = w.scrape()
            urlW = w.scrape_url
            h = HHruScraper(search_string=search_string, q_type=q_type)
            resH = h.scrape()
            urlH = h.scrape_url
            d = DouScraper(search_string=search_string, q_type=q_type)
            resD = d.scrape()
            urlD = d.scrape_url

            context = {
                'form': form,
                'resR': resR, 'urlR': urlR,
                'resW': resW, 'urlW': urlW,
                'resH': resH, 'urlH': urlH,
                'resD': resD, 'urlD': urlD
            }

    else:
        # if GET with no search_string request creating empty form
        form = SearchForm()
        context = {'form': form}

    return render(request, 'vscraper/scraper.html', context)


class Scraper:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    }

    def __init__(self, search_string: str, q_type: int):
        self.search_string: str = search_string
        self.q_type: int = q_type
        self.scrape_url: str = self.get_url(self.search_string, self.q_type)
        self.res: List = []
        self.urls: List = []

    def get_page(self, url: str = None):
        scrape_url = self.scrape_url
        if url:
            scrape_url = url
        r = requests.get(scrape_url, headers=self.headers)
        return BeautifulSoup(r.text, "lxml")


class RabotauaScraper(Scraper):

    def get_url(self, search_string: str, q_type: int):
        urls = {
            # rabota.ua вся украина 7 дней удаленно
            '1': f'https://rabota.ua/zapros/{search_string}/украина?scheduleId=3&period=3',
            # rabota.ua другие страны 7 дней удаленно
            '2': f'https://rabota.ua/zapros/{search_string}/другие_страны?scheduleId=3&period=3',
            # rabota.ua харьков 7 дней полная занятость
            '3': f'https://rabota.ua/zapros/{search_string}/харьков?scheduleId=1&period=3'
        }
        return urls[str(q_type)]

    def scrape(self, url=None):

        soup = self.get_page(url)

        # кол-во вакансий в выборке
        cnt = int(soup.find('span', attrs={'id': 'ctl00_content_vacancyList_ltCount'}).find('span').string.strip())

        if cnt > 0:
            tab = soup.table    # vacancies table

            trs = tab.findAll('tr')  # looking for rows
            for tr in trs:
                try:
                    row_data = self.scrape_row(tr)
                except AttributeError:
                    if tr.find('dd', 'nextbtn'):
                        try:
                            nextpage_url = 'https://rabota.ua' + tr.find('dd', 'nextbtn').find('a').get('href')
                            print(nextpage_url)
                            self.scrape(nextpage_url)
                        except Exception:
                            pass
                else:
                    self.res.append(row_data)
        return self.res

    def scrape_row(self, tr):
        title = tr.find('h2', 'card-title').find('a', 'ga_listing').string.strip()
        url = 'https://rabota.ua' + tr.find('h2', 'card-title').find('a', 'ga_listing').get('href')
        company = tr.find('p', 'company-name').find('a', 'company-profile-name').string.strip()
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
        result = {
            'title': title,
            'url': url,
            'company': company,
            'location': location,
            'salary': salary,
            'shdescr': shdescr}
        return result


class WorkuaScraper(Scraper):

    def get_url(self, search_string: str, q_type: int):
        urls = {
            # work.ua вся украина 7 дней удаленно
            '1': f'https://www.work.ua/jobs-{search_string}/?advs=1&employment=76&days=123',
            # work.ua другие страны 7 дней удаленно
            '2': f'https://www.work.ua/jobs-other-{search_string}/?advs=1&employment=76&days=123',
            # work.ua харьков 7 дней полная занятость
            '3': f'https://www.work.ua/jobs-kharkiv-{search_string}/?advs=1&employment=74&days=123'
        }
        return urls[str(q_type)]

    def scrape(self, url=None):

        soup = self.get_page(url)

        tab = soup.find('div', id='pjax-job-list')    # vacancies table

        if tab is not None:
            trs = tab.findAll('div', 'job-link')  # looking for rows
            for tr in trs:
                try:
                    row_data = self.scrape_row(tr)
                except AttributeError:
                    continue
                else:
                    self.res.append(row_data)

            if tab.find('nav'):
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

    def scrape_row(self, tr):
        title = tr.find('h2').find('a').string.strip()
        url = 'https://work.ua' + tr.find('h2').find('a').get('href')
        company = tr.find('div', 'add-top-xs').find('b').string.strip()
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
        result = {
            'title': title,
            'url': url,
            'company': company,
            'location': location,
            'salary': salary,
            'shdescr': shdescr}
        return result


class HHruScraper(Scraper):

    def get_url(self, search_string: str, q_type: int):
        urls = {
            # hh.ru вся украина 7 дней удаленно
            '1': f'https://hh.ru/search/vacancy?search_period=7&area=5&text={search_string}&schedule=remote',
            # hh.ru другие страны 7 дней удаленно
            '2': f'https://hh.ru/search/vacancy?search_period=7&area=113&text={search_string}&schedule=remote',
            # hh.ru харьков 7 дней полная занятость
            '3': f'https://hh.ru/search/vacancy?search_period=7&area=2206&text={search_string}&schedule=fullDay'
        }
        return urls[str(q_type)]

    def scrape(self, url=None):
        soup = self.get_page(url)
        tab = soup.find('div', 'vacancy-serp')    # vacancies table

        trs = tab.findAll('div', 'vacancy-serp-item')  # looking for rows
        for tr in trs:
            try:
                row_data = self.scrape_row(tr)
            except AttributeError:
                continue
            else:
                self.res.append(row_data)

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

    def scrape_row(self, tr):
        title = tr.find('div', 'vacancy-serp-item__row_header') \
            .find('div', 'vacancy-serp-item__info').find('a').string.strip()
        url = tr.find('div', 'vacancy-serp-item__row_header') \
            .find('div', 'vacancy-serp-item__info').find('a').get('href')
        company = tr.find('div', 'vacancy-serp-item__meta-info') \
            .find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).string.strip()
        # print(f'{title}, {url}, {company}')
        try:
            location = tr.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).string.strip()
        except Exception:
            location = ''
        try:
            salary = tr.find('div', 'vacancy-serp-item__row_header').find('div', 'vacancy-serp-item__sidebar') \
                .find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).string.strip()
        except Exception:
            salary = ''
        try:
            shdescr = tr.find(
                'div',
                attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}
            ).get_text()
            shdescr = shdescr + ' ' + tr.find(
                'div',
                attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}
            ).get_text()
        except Exception:
            shdescr = ''
        result = {
            'title': title,
            'url': url,
            'company': company,
            'location': location,
            'salary': salary,
            'shdescr': shdescr}
        return result


class DouScraper(Scraper):

    def get_url(self, search_string: str, q_type: int):
        urls = {
            # dou.ua вся украина удаленно
            '1': f'https://jobs.dou.ua/vacancies/?remote&search={search_string}',
            # dou.ua другие страны удаленно такая же как первая ссылка
            '2': f'https://jobs.dou.ua/vacancies/?remote&search={search_string}',
            # dou.ua харьков 7 дней полная занятость
            '3': f'https://jobs.dou.ua/vacancies/?city=Харьков&search={search_string}'
        }
        return urls[str(q_type)]

    def scrape(self, url=None):
        # no pagination, scraping one page
        r = requests.get(self.scrape_url, headers=self.headers)
        text = r.text
        soup = BeautifulSoup(text, "lxml")
        tab = soup.find('div', 'l-items')    # vacancies table

        trs = tab.findAll('div', 'vacancy')  # looking for rows
        for tr in trs:
            try:
                title = tr.find('div', 'title').find('a', 'vt').string.strip()
                url = tr.find('div', 'title').find('a', 'vt').get('href')
                company = tr.find('div', 'title').find('a', 'company').get_text()
                # print(f'{title}, {url}, {company}')
                try:
                    location = tr.find('div', 'title').find('span', 'cities').string.strip()
                except Exception:
                    location = ''
                try:
                    salary = tr.find('div', 'title').find('span', 'salary').string.strip()
                except Exception:
                    salary = ''
                try:
                    shdescr = tr.find('div', 'sh-info').get_text()
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

        return self.res
