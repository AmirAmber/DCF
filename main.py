import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests # api
import yfinance as yf
import datetime
import csv
import sys


#dataframe display settings
pd.set_option('display.max_rows', 600)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#Yahoo Finance API urls
urlstatistics = "https://yh-finance.p.rapidapi.com/stock/v3/get-statistics"
urlfinancials = "https://yh-finance.p.rapidapi.com/stock/v2/get-financials"
urlfreecashflow = "https://yh-finance.p.rapidapi.com/stock/v2/get-cash-flow"

API_Key_List=['f1e24449c0msh918d506fb19bfd3p18eab6jsn6da1404b91fe',
              '384defedebmsh3529d85a6748859p1dfb40jsn7615b5feffd3',
              '57d9ba51femsh7546b1ae9c7982dp1b27b8jsn07d9694a2583',
              'b77a18a041mshd0e03d33bad150ap16886ejsn936318603672',
              '820423be58msh1cc69dd3c2a2ceap16e5bajsn0532e74a2f92',
              '43040c5a01mshb2897e2c115c700p1bd0cajsnd13fa23ee69f',
              '8e62212035msh38caf7c7626bf2bp14fe10jsn2fd3d618ff30',
              '037d11bf9amsh3307c552c5467c3p1867b9jsne16365274914',
              '7c9e8606c9msh5a1a9540ba92b47p118e31jsn9e2a3167ad99']

#SP500 list from wikipedia
SP500_df=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
SP500 = SP500_df['Symbol'].values.tolist()
#-------------------------------------------------------------------------------
TTM_year = datetime.datetime.now().year #2022 THIS YEAR
TTM_1 = TTM_year - 1
TTM_2 = TTM_1 - 1
TTM_3 = TTM_2 - 1
TTM_4 = TTM_3 - 1
TTM_5 = TTM_4 - 1

# years = list(range(datetime.datetime.now().year, datetime.datetime.now().year -6, -1))
# print(years)

class Company:
    def __init__(self,Ticker,API_Key):
        Error_Dict = {}
        self.Ticker = Ticker.upper()
        querystring = {"symbol":self.Ticker}

        #Yahoo Finance API configuration
        headers = {
            'x-rapidapi-host': "yh-finance.p.rapidapi.com",
            'x-rapidapi-key':API_Key_List[API_Key]

        }

        response1 = requests.request("GET", urlstatistics, headers=headers, params=querystring)
        response2 = requests.request("GET", urlfinancials, headers=headers, params=querystring)
        response3 = requests.request("GET", urlfreecashflow, headers=headers, params=querystring)

        try:
            Error_Dict['Ticker'] = self.Ticker
            statisticsv3 = response1.json()#ממיר מריקווסט ל דיק
            financialsv2 = response2.json()
            cashflowsv2 = response3.json()

            self.statisticsv3 = statisticsv3
            self.financialsv2=financialsv2
            self.cashflowsv2=cashflowsv2


            #Basic parameters from API
            try:
                self.Market_Cap = statisticsv3.get('price').get('marketCap').get('raw')
            except Exception as e:
                None
            try: #get current price
                self.Current_Price=round(statisticsv3.get('financialData').get('currentPrice').get('raw'))
                Error_Dict['Current Price']=""
            except: # נותן כל סוג של תקלה
                self.Current_Price=""
            try:
                self.Dividend=round(100*(statisticsv3.get('summaryDetail').get('dividendYield').get("raw",0)),2)
                Error_Dict['Dividend'] = ""
                if self.Dividend < 0:
                    self.Dividend = 0
                    Error_Dict['Dividend'] = 1
            except Exception as e:
                self.Dividend = ""
                Error_Dict['Dividend'] = e
            try: #get implied shares outstanding
                Implied_Shares_Outstanding=statisticsv3.get('defaultKeyStatistics').get('impliedSharesOutstanding').get('raw')
            except Exception as e:
                Implied_Shares_Outstanding=0 #מרקט קאפ חלקי פרייס
            try: #get shares outstanding
                Shares_Outstanding=statisticsv3.get('defaultKeyStatistics').get('sharesOutstanding').get('raw')
            except Exception as e:
                Shares_Outstanding=0 # מרקט קאפ חלקי פרייס
            self.Shares_Outstanding = max(Implied_Shares_Outstanding, Shares_Outstanding)
            if self.Shares_Outstanding < 0:
                Error_Dict['Dividend'] = "Negative Number"
            Error_Dict['Shares Outstanding']=""
            if self.Shares_Outstanding == 0 : #if shares outstanding isn't valid
                try:
                    self.Shares_Outstanding =self.Market_Cap / self.Current_Price
                    Error_Dict['Shares Outstanding'] = 1
                except Exception as e:
                    self.Shares_Outstanding =""
                    Error_Dict['Shares Outstanding'] = e
            if self.Current_Price=="":
                try: #if Current Price isn't valid
                    self.Current_Price=self.Market_Cap/self.Shares_Outstanding
                    Error_Dict['Current Price'] = 1
                except Exception as e:
                    Error_Dict['Current Price'] = e
            if self.Current_Price < 0:
                Error_Dict['Current_Price'] = "Negative Number"

            if self.Shares_Outstanding < 0:
                Error_Dict['Shares Outstanding'] = "Negative Number"

            try:
                self.Sector=PATH
            except Exception as e:
                self.Sector=""
                Error_Dict['Sector'] = e
            try:
                try:
                    self.Current_Assets=financialsv2.get('balanceSheetHistoryQuarterly').get('balanceSheetStatements')[0].get('totalCurrentAssets').get('raw')
                    Error_Dict['Current Assets']=""
                except:
                    self.Current_Assets = statisticsv3.get('financialData').get('totalCash').get('raw')
                    Error_Dict['Current Assets'] = 1
                if self.Current_Assets < 0:
                    Error_Dict['Current_Price'] = "Negative Number"
                    self.Current_Assets = 0 #לא בטוח האם כדאי ככה   ???????
            except Exception as e:
                self.Current_Assets=""
                Error_Dict['Current Assets'] = e
            try:
                try:
                    self.Liabilities =financialsv2.get('balanceSheetHistoryQuarterly').get('balanceSheetStatements')[0].get('totalLiab').get('raw')
                    Error_Dict['Liabilities']=""
                except:
                    self.Liabilities = statisticsv3.get('financialData').get('totalDebt').get('raw')
                    Error_Dict['Liabilities'] = 1
                if self.Liabilities < 0:
                    Error_Dict['Liabilities'] = "Negative Number"
                    self.Liabilities =0  #לא בטוח האם כדאי ככה   ???????
            except Exception as e:
                self.Liabilities=""
                Error_Dict['Liabilities'] = e

            # Revenue from API
            try:
                self.TTM_Revenue=financialsv2.get("timeSeries").get('trailingTotalRevenue')[0].get('reportedValue').get('raw')
                Error_Dict['TTM Revenue']=""
                if self.TTM_Revenue == None:
                    Error_Dict['TTM Revenue'] = "Data Unavailable"
                if self.TTM_Revenue < 0:
                    Error_Dict['TTM_Revenue'] = "Negative Number"
                    self.TTM_Revenue = "" #לא בטוח האם כדאי ככה   ???????
            except Exception as e:
                self.TTM_Revenue=""
                Error_Dict['TTM Revenue'] = e
            try:
                Revenue_dict = {}
                self.earnings = financialsv2.get('earnings').get('financialsChart').get('yearly')
                for index in range(len(self.earnings)):
                    year = str(self.earnings[index].get('date'))+" Revenue"
                    Revenue = self.earnings[index].get('revenue').get('raw')
                    Revenue_dict[year] = Revenue
                self._2022Revenue = Revenue_dict.get( str(TTM_year) + " Revenue")
                Error_Dict[str(TTM_year)+" Revenue"] = ""
                if self._2022Revenue == None:
                    Error_Dict[str(TTM_year)+" Revenue"] = "Data Unavailable"
                if self._2022Revenue < 0:
                    Error_Dict[str(TTM_year)+" Revenue"] = "Negative Number"
                    self._2022Revenue = ""  #    ???????

                self._2021Revenue = Revenue_dict.get(str(TTM_1)+" Revenue")
                Error_Dict[str(TTM_1)+" Revenue"] = ""
                if self._2021Revenue == None:
                    Error_Dict[str(TTM_1)+" Revenue"] = "Data Unavailable"
                if self._2021Revenue < 0:
                    Error_Dict[str(TTM_1)+" Revenue"] = "Negative Number"
                    self._2021Revenue = ""  #    ???????

                self._2020Revenue = Revenue_dict.get(str(TTM_2)+" Revenue")
                Error_Dict[str(TTM_2)+" Revenue"] =""
                if self._2020Revenue == None:
                    Error_Dict[str(TTM_2)+" Revenue"] = "Data Unavailable"
                if self._2020Revenue < 0:
                    Error_Dict[str(TTM_2)+" Revenue"] = "Negative Number"
                    self._2020Revenue = ""  #    ???????

                self._2019Revenue = Revenue_dict.get(str(TTM_3)+" Revenue")
                Error_Dict[str(TTM_3)+" Revenue"] = ""
                if self._2019Revenue == None:
                    Error_Dict[str(TTM_3)+" Revenue"] = "Data Unavailable"
                if self._2019Revenue < 0:
                    Error_Dict[str(TTM_3)+" Revenue"] = "Negative Number"
                    self._2019Revenue = ""  #    ???????

                self._2018Revenue = Revenue_dict.get(str(TTM_4)+" Revenue")
                Error_Dict[str(TTM_4)+" Revenue"] = ""
                if self._2018Revenue == None:
                    Error_Dict[str(TTM_4)+" Revenue"] = "Data Unavailable"
                if self._2018Revenue < 0:
                    Error_Dict[str(TTM_4)+" Revenue"] = "Negative Number"
                    self._2018Revenue = ""  #    ???????

                self._2017Revenue = Revenue_dict.get(str(TTM_5)+" Revenue")
                Error_Dict[str(TTM_5)+" Revenue"] =""
                if self._2017Revenue == None:
                    Error_Dict[str(TTM_5)+" Revenue"] = "Data Unavailable"
                if self._2017Revenue < 0:
                    Error_Dict[str(TTM_5) + " Revenue"] = "Negative Number"
                    self._2017Revenue = ""  # ???????


            except Exception as e:
                self._2022Revenue=self._2021Revenue=self._2020Revenue=self._2019Revenue=self._2018Revenue=self._2017Revenue=""
                Error_Dict[str(TTM_year)+" Revenue"] = Error_Dict[str(TTM_1)+" Revenue"]=Error_Dict[str(TTM_2)+" Revenue"] =Error_Dict[str(TTM_3)+" Revenue"] =Error_Dict[str(TTM_4)+" Revenue"] = Error_Dict[str(TTM_5)+" Revenue"] =e

            try:
                self.Next_Year_Revenue = PATH
                Error_Dict['TTM+1 Revenue']=""
            except Exception as e:
                self.Next_Year_Revenue=""
                Error_Dict['TTM+1 Revenue'] = e

            # Net income from API
            try:
                self.TTM_Net_Income=financialsv2.get("timeSeries").get('trailingNetIncome')[0].get('reportedValue').get('raw')
                Error_Dict['TTM Net Income'] = ""
                if self.TTM_Net_Income == None:
                    Error_Dict['TTM Net Income'] = "Data Unavailable"
            except Exception as e:
                self.TTM_Net_Income = ""
                Error_Dict['TTM Net Income'] = e

            try:
                Net_Income_dict = {}
                for index in range(len(self.earnings)):
                    year = str(self.earnings[index].get('date'))+" Net Income"
                    Net_Income = self.earnings[index].get('earnings').get('raw')
                    Net_Income_dict[year] = Net_Income

                self._2022Net_Income = Net_Income_dict.get(str(TTM_year)+" Net Income")
                Error_Dict[str(TTM_year)+" Net Income"] = ""
                if self._2022Net_Income == None:
                    Error_Dict[str(TTM_year)+" Net Income"] = "Data Unavailable"

                self._2021Net_Income = Net_Income_dict.get(str(TTM_1)+" Net Income")
                Error_Dict[str(TTM_1)+" Net Income"] = ""
                if self._2021Net_Income == None:
                    Error_Dict[str(TTM_1)+" Net Income"] = "Data Unavailable"

                self._2020Net_Income = Net_Income_dict.get(str(TTM_2)+" Net Income")
                Error_Dict[str(TTM_2)+" Net Income"] = ""
                if self._2020Net_Income == None:
                    Error_Dict[str(TTM_2)+" Net Income"] = "Data Unavailable"

                self._2019Net_Income = Net_Income_dict.get(str(TTM_3)+" Net Income")
                Error_Dict[str(TTM_3)+" Net Income"] = ""
                if self._2019Net_Income == None:
                    Error_Dict[str(TTM_3)+" Net Income"] = "Data Unavailable"

                self._2018Net_Income = Net_Income_dict.get(str(TTM_4)+" Net Income")
                Error_Dict[str(TTM_4)+" Net Income"] = ""
                if self._2018Net_Income == None:
                    Error_Dict[str(TTM_4)+" Net Income"] = "Data Unavailable"

                self._2017Net_Income = Net_Income_dict.get(str(TTM_5)+" Net Income")
                Error_Dict[str(TTM_5)+" Net Income"] = ""
                if self._2017Net_Income == None:
                    Error_Dict[str(TTM_5)+" Net Income"] = "Data Unavailable"

            except Exception as e:
                self._2022Net_Income=self._2021Net_Income=self._2020Net_Income=self._2019Net_Income=self._2018Net_Income=self._2017Net_Income=""
                Error_Dict[str(TTM_year)+" Net Income"] = Error_Dict[str(TTM_1)+" Net Income"] = Error_Dict[str(TTM_2)+" Net Income"] = Error_Dict[
                str(TTM_3)+" Net Income"] = Error_Dict[str(TTM_4)+" Net Income"] = Error_Dict[str(TTM_5)+" Net Income"] = e

            try:
                self.Next_Year_Net_Income=PATH
                Error_Dict['TTM+1 Net Income'] = ""
            except Exception as e:
                self.Next_Year_Net_Income=""
                Error_Dict['TTM+1 Net Income'] = e
            # Free Cash Flow from API
            try:
                Trailing_Operating_Cash_Flow = (cashflowsv2.get("timeSeries").get('trailingOperatingCashFlow'))[0].get('reportedValue').get('raw')
            except Exception as e:
                Trailing_Operating_Cash_Flow=0
            try:
                Trailing_Capex = abs((cashflowsv2.get("timeSeries").get('trailingCapitalExpenditure'))[0].get('reportedValue').get('raw'))
            except Exception as e:
                Trailing_Capex=0
            self.TTM_Free_Cash_Flow=(Trailing_Operating_Cash_Flow - Trailing_Capex)
            Error_Dict['TTM Free Cash Flow'] = ""
            if self.TTM_Free_Cash_Flow == Trailing_Operating_Cash_Flow or self.TTM_Free_Cash_Flow == - Trailing_Capex:
                Error_Dict['TTM Free Cash Flow'] = 1
            if self.TTM_Free_Cash_Flow==0:
                self.TTM_Free_Cash_Flow=""
                Error_Dict['TTM Free Cash Flow']="Data Unavailable"
            try:
                Free_Cash_Flow_dict = {}
                Cash_Flow_Statements = cashflowsv2.get('cashflowStatementHistory').get('cashflowStatements')
                for index in range(len(Cash_Flow_Statements)):
                    year = str(((Cash_Flow_Statements[-(index + 1)]).get('endDate').get('fmt'))[0:4])+" Free Cash Flow"
                    Cash_Flow_From_Operations = (Cash_Flow_Statements[-(index + 1)]).get('totalCashFromOperatingActivities').get('raw')
                    Capex = abs((Cash_Flow_Statements[-(index + 1)]).get('capitalExpenditures').get('raw'))
                    Free_Cash_Flow_dict[year] = Cash_Flow_From_Operations - Capex
                    Error_Dict[year] = ""
                    if Free_Cash_Flow_dict[year] == Cash_Flow_From_Operations or Free_Cash_Flow_dict[year] == - Capex:
                        Error_Dict[year] = 1
                    if Free_Cash_Flow_dict[year]==0:
                        Error_Dict[year] ="Data Unavailable"

                self._2022Free_Cash_Flow = Free_Cash_Flow_dict.get(str(TTM_year)+" Free Cash Flow")
                if self._2022Free_Cash_Flow==None:
                    Error_Dict[str(TTM_year)+" Free Cash Flow"]="Data Unavailable"

                self._2021Free_Cash_Flow = Free_Cash_Flow_dict.get(str(TTM_1)+" Free Cash Flow")
                if self._2021Free_Cash_Flow==None:
                    Error_Dict[str(TTM_1)+" Free Cash Flow"]="Data Unavailable"

                self._2020Free_Cash_Flow = Free_Cash_Flow_dict.get(str(TTM_2)+" Free Cash Flow")
                if self._2020Free_Cash_Flow==None:
                    Error_Dict[str(TTM_2)+" Free Cash Flow"]="Data Unavailable"

                self._2019Free_Cash_Flow = Free_Cash_Flow_dict.get(str(TTM_3)+" Free Cash Flow")
                if self._2019Free_Cash_Flow==None:
                    Error_Dict[str(TTM_3)+" Free Cash Flow"]="Data Unavailable"

                self._2018Free_Cash_Flow = Free_Cash_Flow_dict.get(str(TTM_4)+" Free Cash Flow")
                if self._2018Free_Cash_Flow==None:
                    Error_Dict[str(TTM_4)+" Free Cash Flow"]="Data Unavailable"

                self._2017Free_Cash_Flow = Free_Cash_Flow_dict.get(str(TTM_5)+" Free Cash Flow")
                if self._2017Free_Cash_Flow==None:
                    Error_Dict[str(TTM_5)+" Free Cash Flow"]="Data Unavailable"

            except Exception as e:
                self._2022Free_Cash_Flow=self._2021Free_Cash_Flow=self._2020Free_Cash_Flow=self._2019Free_Cash_Flow=self._2018Free_Cash_Flow=self._2017Free_Cash_Flow=""
                Error_Dict[str(TTM_year)+" Free Cash Flow"] = Error_Dict[str(TTM_1)+" Free Cash Flow"]=Error_Dict[str(TTM_2)+" Free Cash Flow"] =Error_Dict[str(TTM_3)+" Free Cash Flow"] = Error_Dict[str(TTM_4)+" Free Cash Flow"] = Error_Dict[str(TTM_5)+" Free Cash Flow"] = e

            try:
                self.Next_Year_Free_Cash_Flow = PATH
                Error_Dict['TTM+1 Free Cash Flow'] = ""
            except Exception as e:
                self.Next_Year_Free_Cash_Flow= ""
                Error_Dict['TTM+1 Free Cash Flow'] = e

        except Exception as e:
            Error_Dict['Ticker'] = self.Ticker # str of company
            Error_Dict['Valid Ticker'] = e # error

        try:
            self.Next_Earnings_Date= self.statisticsv3.get('calendarEvents').get('earnings').get('earningsDate')[0].get('fmt')# אפשר לעשות 1 כנתון גיבוי
            Error_Dict['Next Earnings Date'] = ""
        except Exception as e:
            self.Next_Earnings_Date=""
            Error_Dict['Next Earnings Date'] = e

        finally:
            self.Date = datetime.date.today()
            Error_Dict['Date'] = self.Date
            self.Error_Dict = Error_Dict

#returns all company parameters
    def __repr__(self):
        return self.Ticker

#saves company to csv
    def Save_Company(self):
        #with open(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\companies_CSV.txt', 'a') as companies_CSV:
        with open(r'C:\Users\amira\OneDrive\Desktop\dfs\companies1_CSV.txt', 'a') as companies_CSV:
            writer = csv.writer(companies_CSV)
            if self.Error_Dict.get('Valid Ticker')==None:
                csv_data = [self.Ticker, self.Current_Price, self.Dividend, self.Shares_Outstanding, self.Sector,
                        self.Current_Assets, self.Liabilities, self.TTM_Revenue, self._2022Revenue, self._2021Revenue,
                        self._2020Revenue, self._2019Revenue, self._2018Revenue, self._2017Revenue,
                        self.Next_Year_Revenue, self.TTM_Net_Income, self._2022Net_Income, self._2021Net_Income,
                        self._2020Net_Income, self._2019Net_Income, self._2018Net_Income, self._2017Net_Income,
                        self.Next_Year_Net_Income, self.TTM_Free_Cash_Flow, self._2022Free_Cash_Flow,
                        self._2021Free_Cash_Flow, self._2020Free_Cash_Flow, self._2019Free_Cash_Flow,
                        self._2018Free_Cash_Flow, self._2017Free_Cash_Flow, self.Next_Year_Free_Cash_Flow,
                        self.Next_Earnings_Date, self.Date]
                writer.writerow(csv_data)
            companies_CSV.close()
        #with open(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\Errors_CSV.txt', 'a') as Errors_CSV:
        with open(r'C:\Users\amira\OneDrive\Desktop\dfs\Error_log1.txt', 'a') as Errors_CSV:
            writer = csv.writer(Errors_CSV)
            Order_List=['Ticker','Current Price','Dividend','Shares Outstanding','Sector','Current Assets','Liabilities','TTM Revenue','2022 Revenue','2021 Revenue','2020 Revenue','2019 Revenue','2018 Revenue','2017 Revenue','TTM+1 Revenue','TTM Net Income','2022 Net Income','2021 Net Income','2020 Net Income','2019 Net Income','2018 Net Income','2017 Net Income','TTM+1 Net Income','TTM Free Cash Flow','2022 Free Cash Flow','2021 Free Cash Flow','2020 Free Cash Flow','2019 Free Cash Flow','2018 Free Cash Flow','2017 Free Cash Flow','TTM+1 Free Cash Flow','Valid Ticker','Next Earnings Date','Date']
            csv_data = []
            for key in Order_List:
                csv_data.append(self.Error_Dict.get(key))
            writer.writerow(csv_data)
            Errors_CSV.close()
        #error_df=pd.DataFrame(data=(self.Error_Dict).items()).T
        #print(error_df)
        #error_df.to_csv(r'C:\Users\amira\OneDrive\Desktop\dfs\errorlog_CSV.txt',mode='a',index=False,header=False)
        #error_df.to_csv(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\Errors_CSV.txt',mode='a',index=False,header=True)
        #error_df.to_excel(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\Errors_CSV.xlsx',index=False,header=False,startrow = r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\Errors_CSV.xlsx'.max_row)

#saves each company in a list to a csv
def Save_List(list):
    API_Key=0
    Run_Time_List=[7.55]
    for company in list:
        try:
            Start_Time=datetime.datetime.now()
            Average_Run_Time=sum(Run_Time_List)/len(Run_Time_List)
            total_seconds=Average_Run_Time*len(list[list.index(company):]) #total time to finish
            minutes=total_seconds//60
            seconds=round(total_seconds%60)
            print(str(round(100*(list.index(company) / len(list)),2)),"% done, about ",minutes," minutes:",seconds,"seconds left" )
            if company.isalnum() == False:
                company = name_fixer(company)
            try:
                comp = Company('{}'.format(company),API_Key)
                while comp.cashflowsv2=={'message': 'You have exceeded the MONTHLY quota for Requests on your current plan, BASIC. Upgrade your plan at https://rapidapi.com/apidojo/api/yh-finance'} and API_Key<=len(API_Key_List):
                    API_Key+=1
                    try:
                        comp = Company('{}'.format(company), API_Key)
                    except:
                        continue
                comp.Save_Company()
                End_Time=datetime.datetime.now()
                Run_Time_List.append((End_Time-Start_Time).total_seconds())
            except:
                continue
        except:
            continue
    print('Total Run Time: ',sum(Run_Time_List[1:]),'Estimated Run Time: ',Run_Time_List[0]*len(Run_Time_List[1:]))

#fixes broken ticker symbols
def name_fixer(Company_Ticker):
    if '>' in Company_Ticker or '<' in Company_Ticker:
        for letter in range(len(Company_Ticker)):
            if '>' == Company_Ticker[letter] or '<' == Company_Ticker[letter]:
                Company_Ticker = Company_Ticker[:letter]
    if '.' in Company_Ticker:
        lst = Company_Ticker.split('.') #apl.a ---> [apl , a]
        lst.insert(1,'-') # ----->[apl , - , a]
        Company_Ticker = lst[0]+lst[1]+lst[2]
    return Company_Ticker

#convert dataframe objects to floats
def convert_to_float(df):
    df1=df.iloc[:,1:-2] # [rows, columns]
    for col in df1.columns:
        df[col]=df[col].astype(float)
    return df

def Calculate_Financial_Averages(df):
    df['Average Revenue'] = df.loc[:, 'TTM Revenue':str(TTM_5)+" "+'Revenue'].mean(axis=1, numeric_only=True)
    df['Average Revenue 3 Years'] = df.loc[:, 'TTM Revenue':str(TTM_2)+" "+'Revenue'].mean(axis=1, numeric_only=True)
    df['Median Revenue'] = df.loc[:, 'TTM Revenue':str(TTM_5)+" "+'Revenue'].median(axis=1, numeric_only=True)

    df['Average Net Income Margin'] = df.loc[:, 'TTM Net Income':str(TTM_5)+" "+'Net Income'].mean(axis=1, numeric_only=True)
    df['Average Net Income Margin 3 Years'] = df.loc[:, 'TTM Net Income':str(TTM_2)+" "+'Net Income'].mean(axis=1, numeric_only=True)
    df['Median Net Income Margin'] = df.loc[:, 'TTM Net Income':str(TTM_5)+" "+'Net Income'].median(axis=1, numeric_only=True)

    df['Average Free Cash Flow'] = df.loc[:, 'TTM Free Cash Flow':str(TTM_5)+" "+'Free Cash Flow'].mean(axis=1, numeric_only=True)
    df['Average Free Cash Flow 3 Years'] = df.loc[:, 'TTM Free Cash Flow':str(TTM_2)+" "+'Free Cash Flow'].mean(axis=1, numeric_only=True)
    df['Median Free Cash Flow'] = df.loc[:, 'TTM Free Cash Flow':str(TTM_5)+" "+'Free Cash Flow'].median(axis=1, numeric_only=True)
    return df

def Calculate_Financial_Margins(df):
    #net income to revenue
    df['TTM Net Income Margin'] = df['TTM Net Income'] / df['TTM Revenue']
    df['TTM-1 Net Income Margin'] = df[str(TTM_1)+" "+'Net Income'] / df[str(TTM_1)+" "+'Revenue']
    df['TTM-2 Net Income Margin'] = df[str(TTM_2)+" "+'Net Income'] / df[str(TTM_2)+" "+'Revenue']
    df['TTM-3 Net Income Margin'] = df[str(TTM_3)+" "+'Net Income'] / df[str(TTM_3)+" "+'Revenue']
    df['TTM-4 Net Income Margin'] = df[str(TTM_4)+" "+'Net Income'] / df[str(TTM_4)+" "+'Revenue']
    df['TTM-5 Net Income Margin'] = df[str(TTM_5)+" "+'Net Income'] / df[str(TTM_5)+" "+'Revenue']
    df['Average Net Income Margin'] = df.loc[:, 'TTM Net Income Margin':'TTM-5 Net Income Margin'].mean(axis=1, numeric_only=True)
    df['Average Net Income Margin 3 Years'] = df.loc[:, 'TTM Net Income Margin':'TTM-2 Net Income Margin'].mean(axis=1, numeric_only=True)
    df['Median Net Income Margin'] = df.loc[:, 'TTM Net Income Margin':'TTM-5 Net Income Margin'].median(axis=1, numeric_only=True)
    #free cash flow to revenue
    df['TTM Free Cash Flow Margin'] = df['TTM Free Cash Flow'] / df['TTM Revenue']
    df['TTM-1 Free Cash Flow Margin'] = df[str(TTM_1)+" "+'Free Cash Flow'] / df[str(TTM_1)+" "+'Revenue']
    df['TTM-2 Free Cash Flow Margin'] = df[str(TTM_2)+" "+'Free Cash Flow'] / df[str(TTM_2)+" "+'Revenue']
    df['TTM-3 Free Cash Flow Margin'] = df[str(TTM_3)+" "+'Free Cash Flow'] / df[str(TTM_3)+" "+'Revenue']
    df['TTM-4 Free Cash Flow Margin'] = df[str(TTM_4)+" "+'Free Cash Flow'] / df[str(TTM_4)+" "+'Revenue']
    df['TTM-5 Free Cash Flow Margin'] = df[str(TTM_5)+" "+'Free Cash Flow'] / df[str(TTM_5)+" "+'Revenue']
    df['Average Free Cash Flow Margin'] = df.loc[:, 'TTM Free Cash Flow Margin':'TTM-5 Free Cash Flow Margin'].mean(axis=1, numeric_only=True)
    df['Average Free Cash Flow Margin 3 Years'] = df.loc[:, 'TTM Free Cash Flow Margin':'TTM-2 Free Cash Flow Margin'].mean(axis=1, numeric_only=True)
    df['Median Free Cash Flow Margin'] = df.loc[:, 'TTM Free Cash Flow Margin':'TTM-5 Free Cash Flow Margin'].median(axis=1, numeric_only=True)
    #free cash flow to net income
    df['TTm Free Cash Flow To Net Income'] =df['TTM Free Cash Flow'] / df['TTM Net Income']
    df['TTm-1 Free Cash Flow To Net Income'] = df[str(TTM_1)+" "+'Free Cash Flow'] / df[str(TTM_1)+" "+'Net Income']
    df['TTm-2 Free Cash Flow To Net Income'] = df[str(TTM_2)+" "+'Free Cash Flow'] / df[str(TTM_2)+" "+'Net Income']
    df['TTm-3 Free Cash Flow To Net Income'] = df[str(TTM_3)+" "+'Free Cash Flow'] / df[str(TTM_3)+" "+'Net Income']
    df['TTm-4 Free Cash Flow To Net Income'] = df[str(TTM_4)+" "+'Free Cash Flow'] / df[str(TTM_4)+" "+'Net Income']
    df['TTm-5 Free Cash Flow To Net Income'] = df[str(TTM_5)+" "+'Free Cash Flow'] / df[str(TTM_5)+" "+'Net Income']
    df['Average Free Cash Flow To Net Income'] = df.loc[:, 'TTm Free Cash Flow To Net Income':'TTm-5 Free Cash Flow To Net Income'].mean(axis=1, numeric_only=True)
    df['Average Free Cash Flow To Net Income 3 Years'] = df.loc[:, 'TTm Free Cash Flow To Net Income': 'TTm-2 Free Cash Flow To Net Income'].mean(axis=1, numeric_only=True)
    df['Median Free Cash Flow To Net Income'] = df.loc[:, 'TTm Free Cash Flow To Net Income':'TTm-5 Free Cash Flow To Net Income'].median(axis=1, numeric_only=True)
    return df

def Calculate_Growth_Rates(df):
    #Revenue Growth rate
    df['TTM Revenue Growth Rate'] = df['TTM Revenue'] / df[str(TTM_1)+" "+ 'Revenue']
    df['TTM-1 Revenue Growth Rate'] = df[str(TTM_1)+" "+'Revenue'] / df[str(TTM_2)+" "+'Revenue']
    df['TTM-2 Revenue Growth Rate'] = df[str(TTM_2)+" "+'Revenue'] / df[str(TTM_3)+" "+'Revenue']
    df['TTM-3 Revenue Growth Rate'] = df[str(TTM_3)+" "+'Revenue'] / df[str(TTM_4)+" "+'Revenue']
    df['TTM-4 Revenue Growth Rate'] = df[str(TTM_4)+" "+'Revenue'] / df[str(TTM_5)+" "+'Revenue']
    df['Average Revenue Growth Rate'] = df.loc[:, 'TTM Revenue Growth Rate':'TTM-4 Revenue Growth Rate'].mean(axis=1, numeric_only=True)
    df['Average Revenue Growth Rate 3 Years'] = df.loc[:, 'TTM Revenue Growth Rate':'TTM-2 Revenue Growth Rate'].mean(axis=1, numeric_only=True)
    df['Median Revenue Growth Rate'] = df.loc[:, 'TTM Revenue Growth Rate':'TTM-4 Revenue Growth Rate'].median(axis=1, numeric_only=True)
    #Net Income Growth rate
    df['TTM Net Income Growth Rate'] = df['TTM Net Income'] / df[str(TTM_1)+" "+'Net Income']
    df['TTM-1 Net Income Growth Rate'] = df[str(TTM_1)+" "+'Net Income'] / df[str(TTM_2)+" "+'Net Income']
    df['TTM-2 Net Income Growth Rate'] = df[str(TTM_2)+" "+'Net Income'] / df[str(TTM_3)+" "+'Net Income']
    df['TTM-3 Net Income Growth Rate'] = df[str(TTM_3)+" "+'Net Income'] / df[str(TTM_4)+" "+'Net Income']
    df['TTM-4 Net Income Growth Rate'] = df[str(TTM_4)+" "+'Net Income'] / df[str(TTM_5)+" "+'Net Income']
    df['Average Net Income Growth Rate'] = df.loc[:, 'TTM Net Income Growth Rate':'TTM-4 Net Income Growth Rate'].mean(axis=1, numeric_only=True)
    df['Average Net Income Growth Rate 3 Years'] = df.loc[:, 'TTM Net Income Growth Rate':'TTM-2 Net Income Growth Rate'].mean(axis=1, numeric_only=True)
    df['Median Net Income Growth Rate'] = df.loc[:, 'TTM Net Income Growth Rate':'TTM-4 Net Income Growth Rate'].median(axis=1, numeric_only=True)
    #Free Cash Flow Growth rate
    df['TTM Free Cash Flow Growth Rate'] = df['TTM Free Cash Flow'] / df[str(TTM_1)+" "+'Free Cash Flow']
    df['TTM-1 Free Cash Flow Growth Rate'] = df[str(TTM_1)+" "+'Free Cash Flow'] / df[str(TTM_2)+" "+'Free Cash Flow']
    df['TTM-2 Free Cash Flow Growth Rate'] = df[str(TTM_2)+" "+'Free Cash Flow'] / df[str(TTM_3)+" "+'Free Cash Flow']
    df['TTM-3 Free Cash Flow Growth Rate'] = df[str(TTM_3)+" "+'Free Cash Flow'] / df[str(TTM_4)+" "+'Free Cash Flow']
    df['TTM-4 Free Cash Flow Growth Rate'] = df[str(TTM_4)+" "+'Free Cash Flow'] / df[str(TTM_5)+" "+'Free Cash Flow']
    df['Average Free Cash Flow Growth Rate'] = df.loc[:, 'TTM Free Cash Flow Growth Rate':'TTM-4 Free Cash Flow Growth Rate'].mean(axis=1, numeric_only=True)
    df['Average Free Cash Flow Growth Rate 3 Years'] = df.loc[:, 'TTM Free Cash Flow Growth Rate':'TTM-2 Free Cash Flow Growth Rate'].mean(axis=1, numeric_only=True)
    df['Median Free Cash Flow Growth Rate'] = df.loc[:, 'TTM Free Cash Flow Growth Rate':'TTM-4 Free Cash Flow Growth Rate'].median(axis=1, numeric_only=True)
    return df

def load_df_from_csv(name):
    if name=='amir':
        df=pd.read_csv(r'C:\Users\amira\OneDrive\Desktop\dfs\companies1_CSV.txt')
    elif name=='roy':
        df=pd.read_csv(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\companies_CSV.txt')
    else:
        return "Wrong Name"

    df=convert_to_float(df)
    df = Calculate_Financial_Averages(df)
    df = Calculate_Financial_Margins(df)
    df = Calculate_Growth_Rates(df)
    return df

def Recursive_DCF(Initial_Free_Cash_Flow,Growth_Rate,Years,Current_Assets,Liabilities,Shares_Outstanding,Current_Price,Dividend,Expected_Return=0):
    if Expected_Return>75:
        return Expected_Return
    #growth period calculation
    n=Years+1
    a1=Initial_Free_Cash_Flow
    q1=Growth_Rate/(1+(Expected_Return/100))+0.000000000000001
    Growth_Value=a1*(q1**(n)-1)/(q1-1)-a1  # sum Sn
    #terminal value calculation
    an=a1*(q1**(n-1))
    terminal_growth_rate=1.025
    q2=terminal_growth_rate/(1+(Expected_Return/100))+0.000000000000001
    Terminal_Value=(an/(1-q2))-an
    #adjustment for assets,liabilities and share count
    Value_Per_Share=(Growth_Value+Terminal_Value+Current_Assets-Liabilities)/Shares_Outstanding
    #Recursive call
    if Value_Per_Share > Current_Price :
        Expected_Return+=0.1
        return Recursive_DCF(Initial_Free_Cash_Flow,Growth_Rate,Years,Current_Assets,Liabilities,Shares_Outstanding,Current_Price,Dividend,Expected_Return)
    else:
        return round((Expected_Return+Dividend*0.75),2)

def Calculate_DCF(df):
    df['DCF Revenue 5 Years'] = df.apply(lambda row: Recursive_DCF(Initial_Free_Cash_Flow=row['Average Free Cash Flow Margin']*row['Average Revenue'],Growth_Rate=row['Average Revenue Growth Rate'],Years=6,Current_Assets=row['Current Assets'],Liabilities=row['Liabilities'],Shares_Outstanding=row['Shares Outstanding'],Current_Price=row['Current Price'],Dividend=row['Dividend'],Expected_Return=5), axis=1)
    df['DCF Revenue 3 Years'] = df.apply(lambda row: Recursive_DCF(Initial_Free_Cash_Flow=row['Average Free Cash Flow Margin']*row['Average Revenue 3 Years'],Growth_Rate=row['Average Revenue Growth Rate 3 Years'],Years=6,Current_Assets=row['Current Assets'],Liabilities=row['Liabilities'],Shares_Outstanding=row['Shares Outstanding'],Current_Price=row['Current Price'],Dividend=row['Dividend'],Expected_Return=5), axis=1)
    df['DCF Net Income 5 Years'] = df.apply(lambda row: Recursive_DCF(Initial_Free_Cash_Flow=row['Average Free Cash Flow To Net Income']*row['Average Net Income Margin']*row['Average Revenue'],Growth_Rate=row['Average Revenue Growth Rate'],Years=6,Current_Assets=row['Current Assets'],Liabilities=row['Liabilities'],Shares_Outstanding=row['Shares Outstanding'],Current_Price=row['Current Price'],Dividend=row['Dividend'],Expected_Return=5), axis=1)
    df['DCF Net Income 3 Years'] = df.apply(lambda row: Recursive_DCF(Initial_Free_Cash_Flow=row['Average Free Cash Flow To Net Income']*row['Average Net Income Margin']*row['Average Revenue 3 Years'],Growth_Rate=row['Average Revenue Growth Rate'],Years=6,Current_Assets=row['Current Assets'],Liabilities=row['Liabilities'],Shares_Outstanding=row['Shares Outstanding'],Current_Price=row['Current Price'],Dividend=row['Dividend'],Expected_Return=5), axis=1)
    df['DCF Free Cash Flow 5 years'] = df.apply(lambda row: Recursive_DCF(Initial_Free_Cash_Flow=row['Average Free Cash Flow'],Growth_Rate=row['Average Revenue Growth Rate'],Years=6,Current_Assets=row['Current Assets'],Liabilities=row['Liabilities'],Shares_Outstanding=row['Shares Outstanding'],Current_Price=row['Current Price'],Dividend=row['Dividend'],Expected_Return=5), axis=1)
    df['DCF Free Cash Flow 3 years'] = df.apply(lambda row:Recursive_DCF(Initial_Free_Cash_Flow=row['Average Free Cash Flow 3 Years'],Growth_Rate=row['Average Revenue Growth Rate'],Years=6,Current_Assets=row['Current Assets'],Liabilities=row['Liabilities'],Shares_Outstanding=row['Shares Outstanding'],Current_Price=row['Current Price'],Dividend=row['Dividend'],Expected_Return=5), axis=1)
    df['Average Expected Return']=round(df.loc[:, 'DCF Revenue 5 Years':'DCF Free Cash Flow 3 years'].mean(axis=1, numeric_only=True),2)
    df['Median Expected Return']=round(df.loc[:, 'DCF Revenue 5 Years':'DCF Free Cash Flow 3 years'].median(axis=1, numeric_only=True),2)
    return df

#sys.setrecursionlimit(1000)
#Save_List(SP500)

#df=load_df_from_csv('roy')
df=load_df_from_csv('amir')
df=Calculate_DCF(df)
#df.to_excel(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\sp500today.xlsx')

#print(Save_List(SP500[102:]))
#df = pd.read_csv(r'C:\Users\amira\OneDrive\Desktop\dfs\Error_log1.txt')
#df2=pd.read_csv(r'C:\Users\amira\OneDrive\Desktop\dfs\companies1_CSV.txt')

#df=pd.read_csv(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\Errors_CSV.txt')
#df.to_excel(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\Errors_CSV.xlsx')
#print(df)
#df2=pd.read_csv(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\companies_CSV.txt')
#print(df2)
#print("rev5: "+str(df['DCF Revenue 5 Years'].sum())+" rev 3: "+str(df['DCF Revenue 3 Years'].sum())+" ni5: "+str(df['DCF Net Income 5 Years'].sum())+" ni3: "+str(df['DCF Net Income 3 Years'].sum())+" fcf 5: "+str(df['DCF Free Cash Flow 5 years'].sum())+" fcf 3: "+str(df['DCF Free Cash Flow 3 years'].sum()))
#print(df['Median Expected Return'].median())
#df1=df['Median Expected Return'].sort_values()
#df1=(df[df['Median Expected Return']>13])
#df1=df1[df1['Median Expected Return']<25]
#df2=pd.DataFrame(data=None)
#df2['Ticker']=df1['Ticker']
#df2['Expected Return']=df1['Median Expected Return']
#df2=df2.sort_values(by=['Expected Return'],ignore_index=True)
#print(df2)
#df2.plot(x='Ticker', y='Expected Return',kind="bar")
#plt.show()

#df=pd.read_csv(r'C:\Users\amira\OneDrive\Desktop\dfs\companies_CSV.txt') תקייה אמיר
#df=pd.read_excel(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\sp500df.xlsx',index_col=[0])
#print(df)
#df.to_csv(r'C:\Users\Roy Leibovici\Desktop\Finance\DCF2022\sp500df.txt')