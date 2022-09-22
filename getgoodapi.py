import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests # api
import yfinance as yf
import datetime
import csv
import sys

#list of keys
API_Key_List=['f1e24449c0msh918d506fb19bfd3p18eab6jsn6da1404b91fe',
                  '384defedebmsh3529d85a6748859p1dfb40jsn7615b5feffd3',
                  '57d9ba51femsh7546b1ae9c7982dp1b27b8jsn07d9694a2583',
                  'b77a18a041mshd0e03d33bad150ap16886ejsn936318603672',
                  '820423be58msh1cc69dd3c2a2ceap16e5bajsn0532e74a2f92',
                  '43040c5a01mshb2897e2c115c700p1bd0cajsnd13fa23ee69f',
                  '8e62212035msh38caf7c7626bf2bp14fe10jsn2fd3d618ff30',
                  '037d11bf9amsh3307c552c5467c3p1867b9jsne16365274914',
                  '7c9e8606c9msh5a1a9540ba92b47p118e31jsn9e2a3167ad99']

#dataframe display settings
pd.set_option('display.max_rows', 600)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
# SP500 list from wikipedia
SP500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
SP500 = SP500_df['Symbol'].values.tolist()

# Yahoo Finance API urls
urlstatistics_yahoo = "https://yh-finance.p.rapidapi.com/stock/v3/get-statistics"
urlfinancials_yahoo = "https://yh-finance.p.rapidapi.com/stock/v2/get-financials"
urlfreecashflow_yahoo = "https://yh-finance.p.rapidapi.com/stock/v2/get-cash-flow"

class Urlfromyahoo:
    def __init__(self, urlstatistics , urlfinancials , urlfreecashflow):
        self.urlstatistics = urlstatistics
        self.urlfinancials = urlfinancials
        self.urlfreecashflow = urlfreecashflow
    def pickurlstatistics(self):
        return self.urlstatistics
    def pickurlfinancials(self):
        return self.urlfinancials
    def pickurlfreecashflow(self):
        return self.urlfreecashflow


class Keyfromyahoo:

    def __init__(self,api_key_list):
        self.api_key_list = API_Key_List
    def list_of_api_keys(self):
        list_of_api_keys = self.api_key_list
        return list_of_api_keys

    def pick_specific_key(self,key_number):
        specific_key = self.api_key_list[key_number]
        return specific_key

class List_of_tickers:

    def __init__(self,list_of_symbols_df,list_of_symbols):
        self.list_of_symbols_df = list_of_symbols_df
        self.list_of_symbols = list_of_symbols

    def returns_list_of_tickers(self):
        list_of_tickers = self.list_of_symbols
        return list_of_tickers
    def returns_specific_ticker(self,ticker_number):
        specific_ticker = self.list_of_symbols[ticker_number]
        return specific_ticker

class Headers(Urlfromyahoo,Keyfromyahoo,List_of_tickers):
    def __init__(self,key_list,key_number=0):
        Keyfromyahoo.__init__(self,API_Key_List)
        List_of_tickers.__init__(self,SP500_df,SP500_df)
        Urlfromyahoo.__init__(self,urlstatistics_yahoo,urlfinancials_yahoo,urlfreecashflow_yahoo)

        self.key_list = API_Key_List
        self.key_number = key_number

    def dict_headers(self):
        return  self.headers == {
            'x-rapidapi-host': "yh-finance.p.rapidapi.com",
            'x-rapidapi-key': self.pick_specific_key(self.key_number)
        }

class All_the_requests():

    def requests(self):
        requeststatistics = requests.request("GET",self.pickurlstatistics(),headers=self.dict_headers(),params=self.dict_querystring())

requeststatistics = requests.request("GET", urlstatistics, headers=headers, params=querystring)
requestfinancials = requests.request("GET", urlfinancials, headers=headers, params=querystring)
requestfreecashflow = requests.request("GET", urlfreecashflow, headers=headers, params=querystring)

