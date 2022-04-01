import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import regex as re
from sqlalchemy import create_engine, String, Float, DATE
import pymssql
from datetime import date, datetime
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from empiricaldist import Cdf
import seaborn as sns
from glassdoor.scraper import *
import streamlit as st

def salary_convert(salary):
    if salary == 0:
        return np.nan
    if salary < 1000:
        return salary * 1788
    else:
        return salary


env_path = os.path.join(r'/home/emad/code/emadam/glassdoor/glassdoor/',
                        'postgres_login.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
DATABASE = os.getenv('database')
USERNAME = os.getenv('username')
PASSWORD = os.getenv('password')
HOST = os.getenv('host')

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/92.0.4515.159 Safari/537.36"
}
URL = f'https://www.glassdoor.com.au/Job/melbourne-junior-data-analyst-jobs-SRCH_IL.0,9_IC2264754_KO10,29.htm'
resp = requests.get(URL, headers=headers)
# specifying a desired format of page using the html parser
soup = BeautifulSoup(resp.text, "html.parser")

job_title = scraper.extract_job_title_from_result(soup)
co_name = scraper.extract_company_name_from_result(soup)
co_rate = scraper.extract_company_rate_from_result(soup)
co_loc = scraper.extract_company_location_from_result(soup)
co_sal = scraper.extract_company_salary_from_result(soup)
job_age = scraper.extract_job_age_from_result(soup)

data = list(zip(job_title, co_name, co_rate, co_loc, co_sal,
                job_age))
job_data = pd.DataFrame(data)
job_data = job_data.rename(
    columns={
        0: 'Job Title',
        1: 'Company',
        2: 'Rank',
        3: 'Location',
        4: 'Salary',
        5: 'Ad Date'
    })
job_data['Ad Date'] = pd.to_datetime(job_data['Ad Date'])

engine = create_engine(f"postgres://{USERNAME}:{PASSWORD}@{HOST}:5432/{DATABASE}")

job_data.to_sql("job_data", engine, if_exists='append', index=False)

jobs_stored = pd.read_sql("job_data", engine)

jobs_stored['Ad Date'] = pd.to_datetime(jobs_stored['Ad Date'])
jobs_stored.sort_values(by=['Ad Date'], inplace=True)
jobs_stored.drop_duplicates(subset=['Job Title', 'Company', 'Location'],
                            keep='first',
                            inplace=True)
ad_count = jobs_stored.groupby('Ad Date').size()
jobs_stored = jobs_stored.set_index(pd.DatetimeIndex(
    jobs_stored['Ad Date'])).sort_index()

jobs_stored['Min_Salary'] = jobs_stored['Salary'].str.extract(
    r'([0-9]+,*[0-9]+).*')
jobs_stored['Min_Salary'] = jobs_stored['Min_Salary'].str.replace(
    r'\,', '', regex=True).astype(float).astype(pd.Int64Dtype())

jobs_stored['Max_Salary'] = jobs_stored['Salary'].str.extract(
    r'[0-9]+,*[0-9]+.*?([0-9]+,*[0-9]+)')
jobs_stored['Max_Salary'] = jobs_stored['Max_Salary'].str.replace(
    r'\,', '', regex=True).astype(float).astype(pd.Int64Dtype())

jobs_stored['Min_Salary'] = jobs_stored['Min_Salary'].fillna(value=0)
jobs_stored_min = jobs_stored.apply(lambda x: salary_convert(x['Min_Salary']),
                                    axis=1)
jobs_stored['Min_Salary'] = pd.DataFrame(jobs_stored_min)

jobs_stored['Max_Salary'] = jobs_stored['Max_Salary'].fillna(value=0)
jobs_stored_max = jobs_stored.apply(lambda x: salary_convert(x['Max_Salary']),
                                    axis=1)
jobs_stored['Max_Salary'] = pd.DataFrame(jobs_stored_max)

jobs_stored['Seniority'] = jobs_stored['Job Title'].apply(
    lambda x: 'Senior' if x.find('Senior') != -1 else
    ('Junior' if x.find('Junior') != -1 else
     ('Entry Level' if x.find('Entry level') != -1 else ('Graduate' if x.find(
         'Graduate') != -1 else ('Manager' if x.find('Manager') != -1 else (
             'Internship' if x.find('Internship') != -1 else np.nan))))))
jobs_stored.dropna(subset=['Ad Date'], how='all', inplace=True)

plt.style.use('seaborn-whitegrid')
sns.set()
fig, ax = plt.subplots(2, 2)
fig.set_size_inches(16, 11)
min_salary = jobs_stored['Min_Salary']
before_Date = jobs_stored['Ad Date'] < pd.to_datetime('2021-10-15')
ax[0, 0].plot(Cdf.from_seq(min_salary[before_Date].dropna()),
              label='Before 2021 October 15')
ax[0, 0].plot(Cdf.from_seq(min_salary[~before_Date].dropna()),
              label='After 2021 October 15')
x_min = np.sort(jobs_stored['Min_Salary'].dropna())
y_min = np.arange(1, len(x_min) + 1) / len(x_min)
x_max = np.sort(jobs_stored['Max_Salary'].dropna())
y_max = np.arange(1, len(x_max) + 1) / len(x_max)
pct_list = np.array([25, 50, 75])
maxpct_val = np.percentile(jobs_stored['Max_Salary'].dropna(), pct_list)
minpct_val = np.percentile(jobs_stored['Min_Salary'].dropna(), pct_list)
ax[0, 0].set_ylabel('CDF')
ax[0, 0].set_title(
    'Distribution of minimum salary of "Data Analyst" jobs on Glassdoor')
ax[0, 0].legend()
ax[0, 0].set_xlabel('Estimated salary')

ax[0, 1].plot(x_min,
              y_min,
              marker='.',
              linestyle='none',
              color='r',
              label='Minimum salary')
ax[0, 1].plot(x_max,
              y_max,
              marker='.',
              linestyle='none',
              color='b',
              label='Maximum salary')
ax[0, 1].plot(maxpct_val,
              pct_list / 100,
              marker='^',
              linestyle='none',
              color='c',
              label='25th, 50th and 75th Percentile')
ax[0, 1].plot(minpct_val,
              pct_list / 100,
              marker='^',
              linestyle='none',
              color='k',
              label='25th, 50th and 75th Percentile')
ax[0, 1].annotate(
    'Mean:',
    xy=(jobs_stored['Min_Salary'].mean().astype('int64'), 0.5),
    xytext=(40000, 0.9),
    arrowprops=dict(arrowstyle="fancy",
                    facecolor='green',
                    connectionstyle="angle3,angleA=0,angleB=-90"),
)
ax[0, 1].set_ylabel('ECDF')
ax[0, 1].set_title(
    'Distribution of min and max salary of "Data Analyst" on Glassdoor')
ax[0, 1].legend()
ax[0, 1].set_xlabel('Estimated salary')

ax[1, 0].bar(jobs_stored.index.unique(), ad_count, linestyle='None', color='r')
ax[1, 0].figure.canvas.draw()
ax[1, 0].tick_params(axis='x',
                     which='major',
                     rotation=20,
                     direction='inout',
                     length=6,
                     width=2,
                     color='k',
                     labelcolor='royalblue')
ax[1, 0].set_xlabel('Date of Advertisement', labelpad=0.0, color='magenta')
ax[1, 0].set_ylabel('Number of Ads', color='purple')
ax[1, 0].set_title('\'Data Analyst Job\' Advertisements in Glassdoor website',
                   color='limegreen')

ax[1, 1].pie(jobs_stored['Seniority'].value_counts(),
             labels=jobs_stored['Seniority'].dropna().unique(),
             normalize=True,
             autopct='%1.1f%%',
             shadow=True,
             startangle=0)
ax[1, 1].set_title('Job Ads seniority level count')
fig.savefig("glassdoor" + np.datetime64(date.today()).astype('str') + ".png")

st.set_page_config(page_title='Data Analyst Job: Market Analysis',
                   page_icon='favicon.png',
                   layout="wide")

# Remove the menu button from Streamlit
st.markdown(""" <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style> """,
            unsafe_allow_html=True)


st.title('Data Analyst Job: Market Analysis')
st.markdown('Based on job ads on Glassdoor')
st.image('glassdoor2022-03-28.png', use_column_width='always', output_format='JPEG', caption='Created by EMAD AMINMOGHADAM')
