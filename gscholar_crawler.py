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
import os
import uuid; 
import sys
ROOT_URL = 'https://scholar.google.co.th/scholar?'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
paper_root_directory = '../papers/MSME'


def gscholar2pdfUrl(professor_name):
    i=0
    paper_url_list = []
    paper_list = ['Initialize','asd']
    while (i<=60):
        paper_url_list = []
        params = urllib.parse.urlencode({'q':professor_name,'start':i,'hl':'en'})
        resp = requests.get(ROOT_URL+params,headers=headers)
        print(ROOT_URL+params)
        while(resp.status_code!=200):
            print("Found status code "+resp.status_code+". Sleeping for 10 minutes....")
            time.sleep(600)  #Wait for 10 minutes if something happen (maybe 429)
            resp = requests.get(ROOT_URL+params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        papers = soup.find_all("span", text="[PDF]")
        paper_list = []
        for paper in papers:
            tag_a = paper.find_parent('a',href=True)    
            if(tag_a is not None):
                pdf_url = tag_a['href']
                paper_list.append(pdf_url)
        
        
        start = timeit.default_timer()
        #Start timer
        print("Professor : "+professor_name+", Page "+str(int(i/10))+" -> Found "+str(len(paper_list))+" pdf")
        for paper_url in paper_list:
            if(paper_url not in paper_url_list):
                if pdfUrl2pdf(professor_name,paper_url): #If Success
                        paper_url_list.append(paper)
            time.sleep(0.1)
            print("Finished paper"+str(paper_url))
        #End Timer
        stop = timeit.default_timer()
        print("Execution time : "+str(round(stop - start,2))+"s.")           
        
        if(stop-start<65):
            print("Waiting until minute : "+str(60-round(stop-start,2))+"s. left.")
        while(stop-start<65): 
            stop = timeit.default_timer()
        print("Finished Download pdf of "+professor_name+" from page "+str(int(i/10)))
        i+=10

def pdfUrl2pdf(professor_name,url,page=''):
    try:
        r = requests.get(url)
        #Check if are you robot appear or not:
        try: #If filename is in content-disposition
            localName = r.headers['content-disposition']    
            localName = re.findall("filename=(.+)", localName)[0][1:-1]
        except Exception: #Ifn not, find filename from url
            try: 
                localName=  url.split("/")[-1]
                invalid_char = ['?','=']
                for ch in invalid_char:
                    if ch in localName:
                        localName = professor_name+"_"+str(uuid.uuid4().hex.upper()[0:6])+".pdf"
            except Exception: #If still no, then just random the name
                localName = professor_name.replace(" ","_")+"_"+str(uuid.uuid4().hex.upper()[0:6])
        newPdfDirectory = paper_root_directory+"/"+professor_name+"/"+localName
        os.makedirs(os.path.dirname(newPdfDirectory), exist_ok=True)
        with open(newPdfDirectory, "wb") as code:
            code.write(r.content)
            print(str(Exception))
            return True
    except Exception:
        return False

#Create function that get only name of professor. (Excluding the rank)
def get_raw_name(name):
    return name.split("r. ")[1].split(" (")[0]
    

#Now we will get all of professor names from SIIT
siit_df = pd.read_csv('../dataset/SIIT_staff.csv')
SIIT_professor = siit_df[ siit_df['title'].notnull()] #Get only professor/lecturere
SIIT_professor['real_name'] = SIIT_professor['name'].apply(get_raw_name)
ICT_professor = SIIT_professor[SIIT_professor['fac']=='School of Information, Computer, and Communication Technology  (ICT)']
ICT_professor['title'].value_counts()
SIIT_professor['fac'].value_counts()


ICT_professor['real_name'] = ICT_professor['name'].apply(get_raw_name)

#for professor_name in ICT_professor['real_name'].values[15:]:
    #print(professor_name)
    #gscholar2pdfUrl(professor_name)

MSME_professor =SIIT_professor[SIIT_professor['fac']=='School of Manufacturing Systems and Mechanical Engineering (MSME)']

for professor_name in MSME_professor['real_name'].values[10:]:
    print(professor_name)
    gscholar2pdfUrl(professor_name)
