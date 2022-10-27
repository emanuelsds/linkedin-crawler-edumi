from time import sleep
import requests
import os
import csv

from bs4 import BeautifulSoup as bs


def search_jobs(job, location="Brazil"):

    req = requests.get(f"https://www.linkedin.com/jobs/search?keywords={job}&location={location}&geoId=106057199&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0")
    req.raise_for_status()
    page_soup = bs(req.text, 'html.parser')


    job_links = []
    for res_card in page_soup.findAll("ul", {"class": "jobs-search__results-list"})[0:]:
        for links in res_card.findAll('a', {'class': 'base-card__full-link'}):
            job_links.append(links['href'])
    
    # pages = [25]

    # for i in pages:
    #     req = requests.get(f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job}&location={location}&geoId=106057199&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0&start={i}")
    #     req.raise_for_status()
    #     page_soup2 = bs(req.text, 'html.parser')
    #     for links in res_card.findAll('a', {'class': 'base-card__full-link'}):
    #         job_links.append(links['href'])
    get_jobs_info(job_links, location)
    

def get_jobs_info(links, place):
    csv_filename = f'jobs_in_{place}.csv'
    with open(os.path.join("jobs", csv_filename), 'w', encoding='utf-8') as f:
        headers = ['Source', 'Organization', 'Job Title', 'Location', 'Posted', 'Seniority Level',
                    'Employment Type', 'Job Function', 'Industries']
        write = csv.writer(f, dialect='excel')
        write.writerow(headers)

        for job_link in links:
            sleep(3)
            page_req = requests.get(job_link)
            page_req.raise_for_status()

            # Parse HTML
            job_soup = bs(page_req.text, 'html.parser')
            my_data = [job_link]

            # Topcard scraping                
            for content in job_soup.findAll('div', {'class': 'top-card-layout__card'})[0:]:
                # Scraping Organization Names
                orgs = {'Default-Org': [org.text for org in content.findAll('a', {'class': 'topcard__org-name-link topcard__flavor--black-link'})],
                        'Flavor-Org': [org.text for org in content.findAll('span', {'class': 'topcard__flavor'})]}

                if orgs['Default-Org'] == []:
                    org = orgs['Flavor-Org'][0]
                    my_data.append(org)
                else:
                    for org in orgs['Default-Org']:
                        my_data.append(org)

                # Scraping Job Title
                for title in content.findAll('h1', {'class': 'topcard__title'})[0:]:
                    my_data.append(title.text.replace(',', '.'))

                for location in content.findAll('span', {'class': 'topcard__flavor topcard__flavor--bullet'})[0:]:
                    my_data.append(location.text.replace(',', '.'))

                # Scraping Job Time Posted
                posts = {'Old': [posted.text for posted in content.findAll('span', {'class': 'topcard__flavor--metadata posted-time-ago__text'})],
                            'New': [posted.text for posted in content.findAll('span', {'class': 'topcard__flavor--metadata posted-time-ago__text posted-time-ago__text--new'})]}

                if posts['New'] == []:
                    for text in posts['Old']:
                        my_data.append(text)
                else:
                    for text in posts['New']:
                        my_data.append(text)


            # Criteria scraping
            for criteria in job_soup.findAll('span', {'class': 'job-criteria__text job-criteria__text--criteria'})[:4]:
                my_data.append(criteria.text)
            print(my_data)
            write.writerows([my_data])

search_jobs("desenvolvedor")

