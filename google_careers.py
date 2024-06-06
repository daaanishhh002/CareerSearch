# imports
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import numpy as np
import time

# timing
start_time = time.time()

# acknowledging https status code
main_url = "https://www.google.com/about/careers/applications/jobs/results/"
response = requests.get(main_url)
print(response)

# creating a beautifulsoup object and extracting text from html
doc = BeautifulSoup(response.text, "html.parser")

# calculating total job listings initially
job_listings = int(
    doc.find(class_='VfPpkd-wZVHld-gruSEe-j4LONd').text[-4:]
)
print(f'Total Job Listings: {job_listings}')

# calculating total pages initially
total_pages = job_listings//20 + 1
print(f'Total Pages: {total_pages}')

# gathering relative job urls from all pages
rel_urls = []

for _ in tqdm(range(1,total_pages+1),desc='Gathering Job Links',colour='green',ascii=True):

    page_url = f"https://www.google.com/about/careers/applications/jobs/results/?page={_}"
    response = requests.get(page_url)
    doc = BeautifulSoup(response.text, "html.parser")

    jobs = doc.find_all(class_='lLd3Je')
    for job in jobs:
        rel_urls.append(
            job.find(class_='WpHeLc VfPpkd-mRLv6 VfPpkd-RLmnJb')['href']
        )

print(f'Total Collected Job Listings: {len(rel_urls)}')

# storing relative job urls in series 
rel_urls_s = pd.Series(rel_urls).str[13:]

# creating a dataframe
col_names = ['Job Title','Organisation','Location','Experience',
             'Remote Work','Minimum Qualification',
             'Preferred Qualification','Job Description',
             'Responsibilities','URL']

google_jobs_df = pd.DataFrame(columns=col_names)

# scraping job data and collecting in dataframe
for _ in tqdm(range(2553),desc='Scraping and Creating a Pandas DataFrame',colour='#A020F0',ascii=True):

    job_url = main_url + rel_urls_s[_]
    response = requests.get(job_url)
    doc = BeautifulSoup(response.text,'html.parser')
    
    # lists for temp dataframe
    org = []; jbt = []; loc = []; exp = []; rmt = [];
    mnq = []; pfq = []; jbd = []; rsp = []; url = [];
    
    # dictionary for temp dataframe
    dct = {
        'Job Title':jbt,
        'Organisation':org,
        'Location':loc,
        'Experience':exp,
        'Remote Work':rmt,
        'Minimum Qualification':mnq,
        'Preferred Qualification':pfq,
        'Job Description':jbd,
        'Responsibilities':rsp,
        'URL':url
    }

    # job title
    jbt.append(doc.find(class_='p1N2lc').text)
    # organisation
    org.append(doc.find(class_='RP7SMd').span.text)
    # location
    loc.append(doc.find(class_='r0wTof').text)
    # experience
    try:
        exp.append(doc.find(class_='wVSTAb').text)
    except AttributeError as e:
        exp.append(doc.find_all(class_='RP7SMd')[-1].span.text)
    # remote eligibility
    if len(doc.find_all(class_='RP7SMd')) != 1:
        if doc.find_all(class_='RP7SMd')[1].span.text.lower() == 'remote eligible':
            rmt.append(True)
        else:
            rmt.append(False)
    else:
        rmt.append(False)
    # minimum qualification
    try:
        mnq.append(doc.find(class_='KwJkGe').find_all('ul')[0].text.replace('\n',''))
    except IndexError:
        mnq.append(np.nan)
        pass
    except AttributeError:
        mnq.append(np.nan)
        pass
    # preferred qualification
    try:
        pfq.append(doc.find(class_='KwJkGe').find_all('ul')[1].text.replace('\n',''))
    except IndexError:
        pfq.append(np.nan)
        pass
    except AttributeError:
        pfq.append(np.nan)
        pass
    # job description
    jbd.append(doc.find(class_='aG5W3').text.replace('\n','')[13:])
    # responsilibities
    try:
        rsp.append(doc.find(class_='BDNOWe').text[16:].replace('\n',''))
    except AttributeError:
        rsp.append(np.nan)
        pass
    # job url
    url.append(job_url)
    
    # creating a temp dataframe
    col_names = ['Job Title','Organisation','Location','Experience','Remote Work',
             'Minimum Qualification','Preferred Qualification',
             'Job Description','Responsibilities','URL']
    
    temp = pd.DataFrame(data=dct,columns=col_names)
    
    # appending entries into dataframe
    google_jobs_df = pd.concat([google_jobs_df,temp])
    google_jobs_df = google_jobs_df.reset_index().drop(columns='index')

# seeing shape of dataframe
print(f'Shape of DataFrame: {google_jobs_df.shape}')

# storing data in csv file
google_jobs_df.to_csv('google_careers.csv')

# celebration 🥳
print('Mission Complete'+'\U0001F389'*2 +'\U0001F973'*2)

# timing
end_time = time.time()
print(f'Execution Time: {end_time-start_time}s or {(end_time-start_time)/60}mins')