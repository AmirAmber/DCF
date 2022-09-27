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
API_Key_List = ['f1e24449c0msh918d506fb19bfd3p18eab6jsn6da1404b91fe',
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


class Financial_Dicts_For_Ticker:

    def __init__(self,ticker,api_key):
        self.ticker = ticker
        self.api_key = api_key
        self.headers = {
            'x-rapidapi-host': "yh-finance.p.rapidapi.com",
            'x-rapidapi-key': api_key
        }
        self.querystring = {"symbol": self.ticker}
        self.urlstatistics = urlstatistics_yahoo
        self.urlfinancials = urlfinancials_yahoo
        self.urlfreecashflow = urlfreecashflow_yahoo
        self.url_list = [self.urlstatistics, self.urlfinancials, self.urlfreecashflow]
        self.requeststatistics = requests.request("GET", self.url_list[0], headers=self.headers, params=self.querystring)
        self.requestfinancials = requests.request("GET", self.url_list[1], headers=self.headers, params=self.querystring)
        self.requestfreecashflow = requests.request("GET", self.url_list[2], headers=self.headers, params=self.querystring)
        self.request_list = [self.requeststatistics,self.requestfinancials,self.requestfreecashflow]
        statistics_dict = self.request_list[0].json()#ממיר מריקווסט ל דיק
        financials_dict = self.request_list[1].json()
        cashflows_dict = self.request_list[2].json()
        self.statistics_dict = statistics_dict
        self.financials_dict = financials_dict
        self.cashflows_dict = cashflows_dict
        self.list_of_dicts = [self.statistics_dict, self.financials_dict, self.cashflows_dict]









