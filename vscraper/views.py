from .forms import SearchForm

from django.shortcuts import render

import requests
from bs4 import BeautifulSoup


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

            context = {'form': form,
                       'resR': resR, 'urlR': urlR,
                       'resW': resW, 'urlW': urlW,
                       'resH': resH, 'urlH': urlH,
                       'resD': resD, 'urlD': urlD}

    else:
        # if GET with no search_string request creating empty form
        form = SearchForm()
        context = {'form': form}

    return render(request, 'vscraper/scraper.html', context)


class Scraper:

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}

    def __init__(self, search_string, q_type):
        self.search_string = search_string
        self.q_type = q_type
        self.scrape_url = self.get_url(self.search_string, self.q_type)
        self.res = []

    def get_page(self, url=None):
        if url is None:
            r = requests.get(self.scrape_url, headers=self.headers)
        else:
            r = requests.get(url, headers=self.headers)
        text = r.text
        return BeautifulSoup(text, "lxml")


class RabotauaScraper(Scraper):

    def get_url(self, search_string, q_type):
        if q_type == 1:
            # rabota.ua вся украина 7 дней удаленно
            url = f'https://rabota.ua/zapros/{search_string}/украина?scheduleId=3&period=3'
        elif q_type == 2:
            # rabota.ua другие страны 7 дней удаленно
            url = f'https://rabota.ua/zapros/{search_string}/другие_страны?scheduleId=3&period=3'
        elif q_type == 3:
            # rabota.ua харьков 7 дней полная занятость
            url = f'https://rabota.ua/zapros/{search_string}/харьков?scheduleId=1&period=3'
        else:
            raise ValueError
        print(url)
        return url

    def scrape(self, url=None):

        soup = self.get_page(url)

        # кол-во вакансий в выборке
        cnt = int(soup.find('span', attrs={'id': 'ctl00_content_vacancyList_ltCount'}).find('span').string.strip())

        if cnt > 0:
            tab = soup.table    # vacancies table

            trs = tab.findAll('tr')  # looking for rows
            for tr in trs:
                try:
                    title = tr.find('h2', 'card-title').find('a', 'ga_listing').string.strip()
                    url = 'https://rabota.ua' + tr.find('h2', 'card-title').find('a', 'ga_listing').get('href')
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
                    if tr.find('dd', 'nextbtn'):
                        try:
                            nextpage_url = 'https://rabota.ua' + tr.find('dd', 'nextbtn').find('a').get('href')
                            print(nextpage_url)
                            self.scrape(nextpage_url)
                        except Exception:
                            pass
                else:
                    self.res.append({'title': title,
                                     'url': url,
                                     'company': company,
                                     'location': location,
                                     'salary': salary,
                                     'shdescr': shdescr})
        return self.res


class WorkuaScraper(Scraper):

    def get_url(self, search_string, q_type):
        if q_type == 1:
            # work.ua вся украина 7 дней удаленно
            url = f'https://www.work.ua/jobs-{search_string}/?advs=1&employment=76&days=123'
        elif q_type == 2:
            # work.ua другие страны 7 дней удаленно
            url = f'https://www.work.ua/jobs-other-{search_string}/?advs=1&employment=76&days=123'
        elif q_type == 3:
            # work.ua харьков 7 дней полная занятость
            url = f'https://www.work.ua/jobs-kharkiv-{search_string}/?advs=1&employment=74&days=123'
        else:
            raise ValueError
        print(url)
        return url

    def scrape(self, url=None):

        soup = self.get_page(url)

        tab = soup.find('div', id='pjax-job-list')    # vacancies table

        if tab is not None:
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


class HHruScraper(Scraper):

    def get_url(self, search_string, q_type):
        if q_type == 1:
            # hh.ru вся украина 7 дней удаленно
            url = f'https://hh.ru/search/vacancy?search_period=7&area=5&text={search_string}&schedule=remote'
        elif q_type == 2:
            # hh.ru другие страны 7 дней удаленно
            url = f'https://hh.ru/search/vacancy?search_period=7&area=113&text={search_string}&schedule=remote'
        elif q_type == 3:
            # hh.ru харьков 7 дней полная занятость
            url = f'https://hh.ru/search/vacancy?search_period=7&area=2206&text={search_string}&schedule=fullDay'
        else:
            raise ValueError
        print(url)
        return url

    def scrape(self, url=None):
        soup = self.get_page(url)
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


class DouScraper(Scraper):

    def get_url(self, search_string, q_type):
        if q_type == 1:
            # dou.ua вся украина удаленно
            url = f'https://jobs.dou.ua/vacancies/?remote&search={search_string}'
        elif q_type == 2:
            # dou.ua другие страны удаленно такая же как первая ссылка
            url = f'https://jobs.dou.ua/vacancies/?remote&search={search_string}'
        elif q_type == 3:
            # dou.ua харьков 7 дней полная занятость
            url = f'https://jobs.dou.ua/vacancies/?city=Харьков&search={search_string}'
        else:
            raise ValueError
        print(url)
        return url

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
