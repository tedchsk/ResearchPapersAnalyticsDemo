# -*- coding: utf-8 -*-
#Import packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
import urllib
import timeit
import time
import requests
import re
ROOT_URL = 'http://www.siit.tu.ac.th/personnel.php?'




def SIIT_staff_crawler():
    print("Start crawling SIIT...")
    max_id = 212
    member_dicts = {
            #Profile
            'title':[],
            'fac':[],
            'name':[],
            'pos':[],
            'email':[],
            'phone_rs':[],
            'phone_bkd':[],
            'phone_ext':[],
            #Education
            'education':[],
            #awards
            'awards':[],
            #research
            'research_area':[],
            'research_area_title':[],
            'research_interest':[],
            #work
            'work_experiences':[],
            #activities
            #publication
            'publication':[]
            }
    
    j=1
    while(j<max_id):
        profileNames= ['fac','name','pos','email','phone_rs','phone_bkd','phone_ext']
        #Start loading from url
        params = urllib.parse.urlencode({'id':j})
        resp = requests.get(ROOT_URL+params)
        while(resp.status_code!=200):
            print("Found status code "+resp.status_code+". Sleeping for 10 minutes....")
            time.sleep(1)  #Wait for 10 minutes if something happen (maybe 429)
            resp = requests.get(ROOT_URL+params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        #Extracting member detail
        member_rank = soup.find('div',{'class':'titlegare'}).text
        if "(" in member_rank and ")" in member_rank:
            member_dicts['title'].append(member_rank[member_rank.find("(")+1:member_rank.find(")")])
        else:
            member_dicts['title'].append(None)
        #if('PROFESSOR' in member_rank):
            #if('ASSOCIATE' in member_rank):member_dicts['title'].append('Associate Professor')
            #elif('ASSISTANT' in member_rank):member_dicts['title'].append('Assistant Professor')
            #else: member_dicts['title'].append('Professor')
        #else:
            #member_dicts['title'].append(None)
        member_detail = soup.find_all("div", { "class" : "member_detail" })
        member_txts = member_detail[0].find_all('div',{'class':'member_txt2'})
        for i,detail in enumerate(member_txts):
            member_dicts[profileNames[i]].append(detail.text)
        #Extracting education
        member_titles = soup.find_all('div',{'class':'member_title'})
        #Initialize all
        education_text = ''
        awards_text = ''
        research_area = ''
        research_area_title = ''
        research_interest = ''
        work_exp = ''
        publication_list = ''
        split_character = '\n'
        #Extract features
        for title in member_titles:
            try:
                if 'Education' in title.text:
                    ul = title.next.next.next.next.next.next.ul
                    
                    li_list = ul.find_all('li')
                    for li in li_list:
                        education_text+=(li.text+split_character)
                        
                elif 'Academic Awards' in title.text:
                    ul = title.next.next.next.next.next.next.ul
                    li_list = ul.find_all('li')
                    for li in li_list:
                        awards_text+=(li.text+split_character)
                elif 'Research Areas' in title.text:
                    research_area = title.next.next.next.next.next.next.text
                elif 'Research Interests' in title.text:     
                    research_div = title.next.next.next.next.next.next
                    research_titles = research_div.find_all('strong')
                    for research_title in research_titles:
                        research_area_title+=(research_title.text+split_character)
                    research_interest = research_div.text
                elif 'Work Experiences' in title.text:
                    work_exps = title.next.next.next.next.next.next.ul
                    for li in work_exps.find_all('li'):
                        work_exp+=(li.text+split_character)
                elif 'Publication' in title.text:
                    publications = title.next.next.next.next.next.next
                    ols = publications.find_all('ol')
                    for ol in ols:
                        lis = ol.find_all('li')
                        for li in lis:
                            publication_list+=(li.text+split_character)
            except Exception:
                print("Error at "+str(j))
        member_dicts['education'].append(education_text)
        member_dicts['awards'].append(awards_text)
        member_dicts['research_area'].append(research_area)
        member_dicts['research_area_title'].append(research_area_title)
        member_dicts['research_interest'].append(research_interest)
        member_dicts['work_experiences'].append(work_exp)
        member_dicts['publication'].append(publication_list)
        print(str(j)+"/"+str(max_id)+" : SLeeping for 2 minutes")
        j+=1
    return member_dicts
        
start = timeit.default_timer()
member_dicts = SIIT_staff_crawler()
stop = timeit.default_timer()
print("Execution time : "+str(round(stop - start,2))+"s.")   
df = pd.DataFrame(member_dicts)
df.to_csv('SIIT_staff.csv',index=False,encoding="utf-8")

