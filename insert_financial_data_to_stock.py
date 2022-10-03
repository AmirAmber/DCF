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


class Financial_Parameters_For_Ticker:
# given a ticker , the class will attach 3 params to the ticker
    def __init__(self,ticker,api_key):
        self.ticker = ticker
        self.api_key = api_key
        self.querystring = {"symbol": self.ticker}
        self.headers = {
            'x-rapidapi-host': "yh-finance.p.rapidapi.com",
            'x-rapidapi-key': api_key
        }
        self.urlstatistics = urlstatistics_yahoo
        self.urlfinancials = urlfinancials_yahoo
        self.urlfreecashflow = urlfreecashflow_yahoo


    def request_statistics(self, statistics_url):

        requeststatistics = requests.request("GET", self.urlstatistics, headers=self.headers, params=self.querystring)
        return requeststatistics

    def request_financials(self, financials_url):

        requestfinancials = requests.request("GET", self.urlfinancials, headers=self.headers, params=self.querystring)
        return requestfinancials

    def request_free_cashflow(self, freecashflow_url):

        requestfreecashflow = requests.request("GET", self.urlfreecashflow, headers=self.headers, params=self.querystring)
        return requestfreecashflow

    def requests_to_dicts(self):

        statistics_dict = self.request_statistics(self.urlstatistics).json()
        financials_dict = self.request_financials(self.urlfinancials).json()
        freecashflows_dict = self.request_free_cashflow(self.urlfreecashflow).json()
        parameteres_dict_list = [statistics_dict, financials_dict, freecashflows_dict]
        return parameteres_dict_list


class Extract_Statistics_Data(Financial_Parameters_For_Ticker):
    # when given statistics_dict extract all needed data
    def __init__(self):
        