import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, String, Float, DATE
import pymssql
from datetime import date, datetime
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from empiricaldist import Cdf
import seaborn as sns

class scraper():

    def __init__(self, soup):
        self.soup = soup
        pass

    def extract_job_title_from_result(soup):
        jobs = []
        for a in soup.find_all(name="a", attrs={"data-test": "job-link"}):
            for spans in a.find_all(name="span"):
                jobs.append(spans.text)
        return jobs

    def extract_company_name_from_result(soup):
        coname = []
        for div in soup.find_all(name="div", attrs={"class": "e1rrn5ka0"}):
            for div in div.find_all(
                    name="div",
                    attrs={
                        "class":
                        "d-flex justify-content-between align-items-start"
                    }):
                for a in div.find_all(name="a"):
                    for spans in a.find_all(name="span"):
                        coname.append(spans.text)
        return coname

    def extract_company_rate_from_result(soup):
        corate = []
        for div in soup.find_all(name="div", attrs={"class": "e1rrn5ka1"}):
            if div.find_all(name="span", attrs={"class": "e1cjmv6j0"}):
                for spans in div.find_all(name="span",
                                          attrs={"class": "e1cjmv6j0"}):
                    corate.append(spans.text)
            else:
                corate.append(np.nan)
        return corate

    def extract_company_location_from_result(soup):
        coloc = []
        for div in soup.find_all(name="div", attrs={"class": "e1rrn5ka2"}):
            for spans in div.find_all(name="span"):
                coloc.append(spans.text)
        return coloc

    def extract_company_salary_from_result(soup):
        cosal = []
        for div in soup.find_all(name="div", attrs={"class": "e1rrn5ka0"}):
            if div.find_all(name="div", attrs={"class": "e1rrn5ka3"}):
                for spans in div.find_all(name="span",
                                          attrs={"data-test": "detailSalary"}):
                    cosal.append(spans.text)
            else:
                cosal.append(np.nan)
        return cosal

    def extract_job_age_from_result(soup):
        jobage = []
        for div in soup.find_all(name='div',
                                 attrs={"class": ["e1rrn5ka2", "e1rrn5ka3"]}):
            for age in div.find_all(name='div', attrs={"data-test":
                                                       "job-age"}):
                result = age.text
                result = result.replace('24h', '1d')
                result = result.replace('d', '')
                result = result.replace('30+', '31')
                t_dif = np.timedelta64(result, 'D')
                if t_dif < np.timedelta64(31, 'D'):
                    ad_date = np.datetime64(date.today()) - t_dif
                    ad_date = ad_date.astype(datetime)
                    jobage.append(ad_date)
                else:
                    jobage.append(np.nan)
        return jobage

    def job_seniority(job):
        if job.find('Senior') != -1:
            return 'Senior'
        if job.find('Junior') != -1:
            return 'Junior'
        if job.find('Entry level') != -1:
            return 'Entry level'
        if job.find('Graduate') != -1:
            return 'Graduate'
        if job.find('Manager') != -1:
            return 'Manager'
        if job.find('Internship') != -1:
            return 'Internship'
        else:
            return np.nan

    def extract_job_link_from_result(soup):
        joblink = []
        for div in soup.find_all(name="div", attrs={"class": "e1rrn5ka0"}):
            for a in div.find_all(name='a', href=True):
                joblink.append('glassdoor.com.au' + a['href'])
            else:
                joblink.append(np.nan)
        return joblink
