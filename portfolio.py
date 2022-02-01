import yaml
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pickle

pd.set_option("display.max_columns", None)
pd.set_option("expand_frame_repr", True)
pd.options.mode.chained_assignment = None  # default='warn'
pd.set_option("display.precision", 2)

class portfolio_data:
    
    def __init__(self):
        self.portfolio_struct={
            'Share': [],
            'Qty': 0.0,
            'Mean buy price': 0.0,
            'Total Invest.': 0.0,
            'Comms': 0.0,
            'Cur. price': 0.0,
            'Currency': 0.0,
            'Total Currency': 0.0,
            'Total CHF': 0.0,
            'P&L Currency': 0.0,
            'P&L CHF': 0.0,
            'P&L %': 0.0,
            'Type': 0.0,
            'Last 1Y Div.': 0.0,
            'Annual Rev. CHF': 0.0,

        }
        self.currency_ref_struct={
            'Ticker': [],
            'Type': 0.0,

        }
        self.sectors_struct={
            'Ticker':  [],
            'Health care':  0.0,
            'Consumer Stapples':  0.0,
            'Financials':  0.0,
            'Industrials':  0.0,
            'Consumer Discretionary':  0.0,
            'Basic Materials':  0.0,
            'Technology':  0.0,
            'Real Estate':  0.0,
            'Communication':  0.0,
            'Utilities':  0.0,
            'Energy':  0.0,
            'Cash/Derivatives':  0.0,
        }
        self.sectors_struct_noticker={
            'Health care':  [],
            'Consumer Stapples':  0.0,
            'Financials':  0.0,
            'Industrials':  0.0,
            'Consumer Discretionary':  0.0,
            'Basic Materials':  0.0,
            'Technology':  0.0,
            'Real Estate':  0.0,
            'Communication':  0.0,
            'Utilities':  0.0,
            'Energy':  0.0,
            'Cash/Derivatives':  0.0,
        }
        self.market_struct={
            'Ticker':  [],
            'USA':  0.0,
            'EUROPE':  0.0,
            'Pacific':  0.0,
            'Emerging markets':  0.0,
            'Middle East':  0.0,
            'Other':  0.0,
        }
        self.market_struct_noticker={
            'USA':  [],
            'EUROPE':  0.0,
            'Pacific':  0.0,
            'Emerging markets':  0.0,
            'Middle East':  0.0,
            'Other':  0.0,
        }





        self.portfolio_struct_filename='data/portfolio_struct.p'
        self.currency_ref_struct_filename='data/currency_ref_struct.p'
        self.sectors_struct_filename='data/sectors_struct.p'
        self.sectors_struct_noticker_filename='data/sectors_struct_noticker.p'
        self.market_struct_filename='data/market_struct.p'
        self.market_struct_noticker_filename='data/market_struct_noticker.p'


        
    def create(self):
        pickle.dump( self.portfolio_struct, open( self.portfolio_struct_filename, "wb" ) )
        pickle.dump( self.currency_ref_struct, open( self.currency_ref_struct_filename, "wb" ) )
        pickle.dump( self.sectors_struct, open( self.sectors_struct_filename, "wb" ) )
        pickle.dump( self.sectors_struct_noticker, open( self.sectors_struct_noticker_filename, "wb" ) )
        pickle.dump( self.market_struct, open( self.market_struct_filename, "wb" ) )
        pickle.dump( self.market_struct_noticker, open( self.market_struct_noticker_filename, "wb" ) )

    def get_portfolio_struct(self):
        return pickle.load( open( self.portfolio_struct_filename, "rb" ) )

    def get_currency_ref_struct(self):
        return pickle.load( open( self.currency_ref_struct_filename, "rb" ) )

    def get_sectors_struct(self):
        return pickle.load( open( self.sectors_struct_filename, "rb" ) )

    def get_sectors_struct_noticker(self):
        return pickle.load( open( self.sectors_struct_noticker_filename, "rb" ) )

    def get_market_struct(self):
        return pickle.load( open( self.market_struct_filename, "rb" ) )

    def get_market_struct_noticker(self):
        return pickle.load( open( self.market_struct_noticker_filename, "rb" ) )



class portfolio:
    
    def __init__(self, tickers_filename, chf_usd_rate):
        
        self.pf_data=portfolio_data()
        self.pf_data.create()

        self.portfolio = pd.DataFrame(self.pf_data.get_portfolio_struct())
        self.currency_ref = pd.DataFrame(self.pf_data.get_currency_ref_struct())
        self.annual_rev_chf=0.



        self.total_invest_chf=0.00

        if chf_usd_rate>0:
            self.chf_usd_rate=chf_usd_rate
        else:
            self.get_chf_usd_rate()
        print('1 CHF = %.4f USD' %self.chf_usd_rate)

        self.read_tickers_file(tickers_filename)

    def get_chf_usd_rate(self):
        chf_usd = yf.Ticker("CHFUSD=X")
        hist = chf_usd.history(period="1d")
        self.chf_usd_rate=hist['Close'][-1]
        return 

    def get_ticker_1y_dividend(self,ticker):
        """
        read last year data for ticker
        returns the sum of dividends
        """
        tmp = yf.Ticker(ticker).history(period='1Y')
        try:
            return tmp['Dividends'].sum()
        except:
            return 0

    
    def get_ticker_current_rate(self,ticker):
        x = yf.Ticker(ticker)
        hist = x.history(period="2d")
        return hist['Close'][-1]


    def get_ticker_support(self,ticker_ref, ticker):
        result=ticker_ref.loc[ticker_ref['Ticker'] == ticker]
        if len(result)>0:
            index=result.index[0]
            support=ticker_ref['Support'][index]
        else:
            index=-1
            support='?'
        return support


    def get_ticker_type(self,ticker_ref, ticker):
        result=ticker_ref.loc[ticker_ref['Ticker'] == ticker]
        if len(result)>0:
            index=result.index[0]
            the_type=ticker_ref['Type'][index]
        else:
            index=-1
            the_type='?'
        return the_type

    def read_tickers_file(self,tickers_filename):
        try:
            with open(tickers_filename) as file:
                self.tickers = yaml.load(file, Loader=yaml.FullLoader)
                #print(self.tickers)
        except:
            print('Error: unable to read %s.' %tickers_filename)
            
        #print('----')

        for k in self.tickers:
            #print(k)
            self.currency_ref=self.currency_ref.append( {
                'Ticker': k,
                #'Support':self.tickers[k]['Support'],
                'Type':self.tickers[k]['Type'],

            }, ignore_index=True)
        #print('----')
        #print(self.currency_ref)
        return

    
    def read_transactions_file(self,transactions_filename):
        try:
            with open(transactions_filename) as file:
                self.transactions = yaml.load(file, Loader=yaml.FullLoader)

        except:
            print('Error: unable to read %s.' %tickers_filename)

    def process_transactions(self,transactions_filename, display=False):
        
        self.read_transactions_file(transactions_filename)

        for k in self.transactions:
            t=self.transactions[k]
            date=t['Date']
            #print(t)

            if t['Action']=='INJECT_CURRENCY':
                currency=t['Currency']
                qty=t['Qty']
                result=self.portfolio.loc[self.portfolio['Share'] == currency]
                if len(result)>0:
                    index=result.index[0]
                else:
                    #print('Adding',currency,'to portfolio')
                    self.portfolio = self.portfolio.append({
                        'Share':currency,
                        'Qty':0.0,
                        'Mean buy price':1,
                        'Total Invest.':0,
                        'Cur. price':1,
                        'Currency':0.0,
                        'Total Currency':0.0,
                        'Total CHF':0.0,
                        'P&L Currency':0.0,
                        'P&L CHF':0.0,
                        'P&L %': 0.0,
                        #'Support':self.get_ticker_support(self.currency_ref,currency),
                        'Type':self.get_ticker_type(self.currency_ref,currency),
                        'Last 1Y Div.': 0.0,
                        'Annual Rev. CHF': 0.0,



                    }, ignore_index=True)
                    result=self.portfolio.loc[self.portfolio['Share'] == currency]
                    index=result.index[0]
                self.portfolio['Qty'][index]+=qty
                self.portfolio['Currency'][index]=currency
                self.total_invest_chf+=qty
                if display:
                        print("%s %-16s %+8.2f %s" %(date,t['Action'],qty,currency))


            elif t['Action']=='BUY_CURRENCY':
                to_currency=t['Currency']
                from_currency=t['With']
                qty=t['Qty']
                rate=t['Rate']

                result=self.portfolio.loc[self.portfolio['Share'] == to_currency]
                if len(result)>0:
                    index_to=result.index[0]
                else:
                    #print('Adding',to_currency,'to portfolio')
                    self.portfolio = self.portfolio.append({
                        'Share':to_currency,
                        'Qty':0.0,
                        'Mean buy price':1,
                        'Total Invest.':0,
                        'Cur. price':1,
                        'Currency':0.0,
                        'Total Currency':0.0,
                        'Total CHF':0.0,
                        'P&L Currency':0.0,
                        'P&L CHF':0.0,
                        'P&L %': 0.0,
                        #'Support':self.get_ticker_support(self.currency_ref,currency),
                        'Type':self.get_ticker_type(self.currency_ref,currency),
                        'Last 1Y Div.': 0.0,
                        'Annual Rev. CHF': 0.0,



                    }, ignore_index=True)
                    result=self.portfolio.loc[self.portfolio['Share'] == to_currency]
                    index_to=result.index[0]

                result=self.portfolio.loc[self.portfolio['Share'] == from_currency]
                if len(result)>0:
                    index_from=result.index[0]
                else:
                    print('ERROR, currency',from_currency,'not found.')

                self.portfolio['Qty'][index_to]+=qty*rate
                self.portfolio['Qty'][index_from]-=qty+t['Comm']
                self.portfolio['Currency'][index_to]=to_currency
                if display:
                        print("%s %-16s %+8.2f %3s => %+8.2f %3s" %(date,t['Action'],qty,from_currency,qty*rate,to_currency))

            elif t['Action']=='BUY_SHARE':
                ticker=t['Ticker']
                currency=t['Currency']
                qty=t['Qty']
                rate=t['Rate']



                result=self.portfolio.loc[self.portfolio['Share'] == ticker]
                if len(result)>0:
                    index_to=result.index[0]
                else:
                    #print('Adding',ticker,'to portfolio')
                    self.portfolio = self.portfolio.append({
                        'Share':ticker,
                        'Qty':0.0,
                        'Mean buy price':0.0,
                        'Total Invest.':0,
                        'Comms': 0.0,
                        'Cur. price':0.0,
                        'Currency':0.0,
                        'Total Currency':0.0,
                        'Total CHF':0.0,
                        'P&L Currency':0.0,
                        'P&L CHF':0.0,
                        'P&L %': 0.0,
                        #'Support':self.get_ticker_support(self.currency_ref,ticker),
                        'Type':self.get_ticker_type(self.currency_ref,ticker),
                        'Last 1Y Div.': 0.0,
                        'Annual Rev. CHF': 0.0,


                    }, ignore_index=True)
                    result=self.portfolio.loc[self.portfolio['Share'] == ticker]
                    index_to=result.index[0]

                result=self.portfolio.loc[self.portfolio['Share'] == currency]
                if len(result)>0:
                    index_from=result.index[0]
                else:
                    print('ERROR, currency',currency,'not found.')

                if display:
                        print("%s %-16s %8.2f %-10s at %8.2f %s  (+comm=%.2f)" %(date,t['Action'],qty,ticker,rate,currency,t['Comm']))
                    
                    
                # first buy of this ticker
                if self.portfolio['Qty'][index_to]==0:
                    self.portfolio['Qty'][index_to]=qty
                    self.portfolio['Mean buy price'][index_to]=(qty*rate+t['Comm'])/qty
                    self.portfolio['Total Invest.'][index_to]=self.portfolio['Mean buy price'][index_to]*self.portfolio['Qty'][index_to]
                    self.portfolio['Comms'][index_to]=t['Comm']


                # add more
                else:
                    current_qty=self.portfolio['Qty'][index_to]
                    current_value=self.portfolio['Qty'][index_to]*self.portfolio['Mean buy price'][index_to]#+self.portfolio['Comms'][index_to]
                    new_qty=current_qty+qty
                    new_value=current_value+qty*rate+t['Comm']
                    new_rate=new_value/new_qty
                    self.portfolio['Qty'][index_to]=new_qty
                    self.portfolio['Mean buy price'][index_to]=new_rate
                    self.portfolio['Total Invest.'][index_to]=self.portfolio['Mean buy price'][index_to]*self.portfolio['Qty'][index_to]
                    self.portfolio['Comms'][index_to]+=t['Comm']



                total=qty*rate+t['Comm']
                #print('Total cost: ',total)
                self.portfolio['Qty'][index_from]-=total


                current_rate=self.get_ticker_current_rate(ticker)
                self.portfolio['Cur. price'][index_to]=current_rate

                self.portfolio['Currency'][index_to]=currency

        
        for index in range(len(self.portfolio)):
            self.portfolio['Total CHF'][index]=self.portfolio['Qty'][index]*self.portfolio['Cur. price'][index]
            self.portfolio['Total Currency'][index]=self.portfolio['Total CHF'][index]
            self.portfolio['P&L %'][index]=0
            if self.portfolio['Total Invest.'][index]>0:
                self.portfolio['P&L %'][index]=100*(self.portfolio['Total Currency'][index]-self.portfolio['Total Invest.'][index])/self.portfolio['Total Invest.'][index]



            self.portfolio['P&L CHF'][index]=self.portfolio['Qty'][index]*(self.portfolio['Cur. price'][index]-self.portfolio['Mean buy price'][index])
            self.portfolio['P&L Currency'][index]=self.portfolio['P&L CHF'][index]
            
            if self.portfolio['Currency'][index]=='USD':
                self.portfolio['Total CHF'][index]/=self.chf_usd_rate
                self.portfolio['P&L CHF'][index]/=self.chf_usd_rate

            if self.portfolio['Type'][index]!='Cash':
                self.portfolio['Last 1Y Div.'][index]=self.get_ticker_1y_dividend(self.portfolio['Share'][index])
                annual_rev_for_share=self.portfolio['Last 1Y Div.'][index]*self.portfolio['Qty'][index]
                if self.portfolio['Currency'][index]=='USD':
                    self.annual_rev_chf+=annual_rev_for_share/self.chf_usd_rate
                else:
                    self.annual_rev_chf+=annual_rev_for_share

                self.portfolio['Annual Rev. CHF'][index]=annual_rev_for_share




        self.ratio=100*self.portfolio['P&L CHF'].sum()/self.total_invest_chf


        print('\n')
        print('Total injected:   %+9.2f CHF' %self.total_invest_chf)
        print('Current value:    %+9.2f CHF' %self.portfolio['Total CHF'].sum())
        print('P&L:              %+9.2f CHF (%.1f%%)' %(self.portfolio['P&L CHF'].sum(),self.ratio))
        print('Est. annual rev.: %+9.2f CHF' %self.annual_rev_chf)



    def compute_sectors_ratio(self):


        self.sectors = pd.DataFrame(self.pf_data.get_sectors_struct())
        self.sectors_details = pd.DataFrame(self.pf_data.get_sectors_struct())
        self.sectors_ratio = pd.DataFrame(self.pf_data.get_sectors_struct_noticker())



        # create a table with sectors ratio for each ticker => sectors
        for t in (self.tickers):
            if self.tickers[t]['Support']!='Currency':
                
                info=self.tickers[t]['Sectors']
                if 0:
                    tmp_o=self.pf_data.get_sectors_struct()
                    tmp_o['Ticker']=t
                    tmp_o['Health care']=info['Health care'],
                    tmp_o['Consumer Stapples']=info['Consumer Stapples'],
                    tmp_o['Financials']=info['Financials'],
                    tmp_o['Industrials']=info['Industrials'],
                    tmp_o['Consumer Discretionary']=info['Consumer Discretionary'],
                    tmp_o['Basic Materials']=info['Basic Materials'],
                    tmp_o['Technology']=info['Technology'],
                    tmp_o['Real Estate']=info['Real Estate'],
                    tmp_o['Communication']=info['Communication'],
                    tmp_o['Utilities']=info['Utilities'],
                    tmp_o['Energy']=info['Energy'],
                    tmp_o['Cash/Derivatives']=info['Cash/Derivatives'],
                    self.sectors = self.sectors.append(tmp_o, ignore_index=True)

                else:
                    self.sectors = self.sectors.append({
                        'Ticker': t,
                        'Health care': info['Health care'],
                        'Consumer Stapples': info['Consumer Stapples'],
                        'Financials': info['Financials'],
                        'Industrials': info['Industrials'],
                        'Consumer Discretionary': info['Consumer Discretionary'],
                        'Basic Materials': info['Basic Materials'],
                        'Technology': info['Technology'],
                        'Real Estate': info['Real Estate'],
                        'Communication': info['Communication'],
                        'Utilities': info['Utilities'],
                        'Energy': info['Energy'],
                        'Cash/Derivatives': info['Cash/Derivatives'],

                    }, ignore_index=True)


        #sectors

        # compute the value per sectors for all ticker => sectors_details
        for i in range(len(self.portfolio)):
            #print(p.portfolio.loc[i, "Share"], p.portfolio.loc[i, "Total CHF"])

            ticker=self.portfolio.loc[i, "Share"]
            total_chf=self.portfolio.loc[i, "Total CHF"]
            if self.tickers[ticker]['Support']!='Currency':

                result=self.sectors.loc[self.sectors['Ticker'] == ticker]

                tmp=self.pf_data.get_sectors_struct()
                #print(tmp)
                for k in self.sectors_details.columns:
                    if k=='Ticker':
                        tmp[k]=ticker
                    else:
                        #print(k,result[k].to_numpy())
                        if result[k].to_numpy()[0]!=None and False==np.isnan(result[k].to_numpy()[0]):
                            tmp[k]=result[k].to_numpy()[0]*total_chf/100.
                        else:
                            tmp[k]=0

                self.sectors_details = self.sectors_details.append(tmp, ignore_index=True)



        # compute the ratio per sectors for all sectors => sectors_ratio

        tmp=self.pf_data.get_sectors_struct_noticker()

        for k in self.sectors_ratio.columns:
            total=self.sectors_details[k].sum()/self.total_invest_chf*100
            #print(k,total)
            tmp[k]=total

        self.sectors_ratio = self.sectors_ratio.append(tmp, ignore_index=True)


        return self.sectors_ratio   
    
    
    def compute_market_ratio(self):


        self.market = pd.DataFrame(self.pf_data.get_market_struct())
        self.market_details = pd.DataFrame(self.pf_data.get_market_struct())
        self.market_ratio = pd.DataFrame(self.pf_data.get_market_struct_noticker())

        for t in (self.tickers):
            if self.tickers[t]['Support']!='Currency':

                info=self.tickers[t]['Markets']

                tmp=self.pf_data.get_market_struct()
                tmp['Ticker']=t
                tmp['USA']=info['USA']
                tmp['EUROPE']=info['EUROPE']
                tmp['Pacific']=info['Pacific']
                tmp['Emerging markets']=info['Emerging markets']
                tmp['Middle East']=info['Middle East']
                tmp['Other']=info['Other']

                self.market = self.market.append(tmp, ignore_index=True)


        #self.market
        


        for i in range(len(self.portfolio)):
            #print(p.portfolio.loc[i, "Share"], p.portfolio.loc[i, "Total CHF"])

            ticker=self.portfolio.loc[i, "Share"]
            total_chf=self.portfolio.loc[i, "Total CHF"]
            if self.tickers[ticker]['Support']!='Currency':


                result=self.market.loc[self.market['Ticker'] == ticker]
                tmp=self.pf_data.get_market_struct()

                for k in self.market_details.columns:
                    if k=='Ticker':
                        tmp[k]=ticker
                    else:
                        #print(k,result[k].to_numpy())
                        if result[k].to_numpy()[0]!=None and False==np.isnan(result[k].to_numpy()[0]):
                            tmp[k]=result[k].to_numpy()[0]*total_chf/100.
                        else:
                            tmp[k]=0

                self.market_details = self.market_details.append(tmp, ignore_index=True)



        tmp=self.pf_data.get_market_struct_noticker()

        for k in self.market_ratio.columns:
            total=self.market_details[k].sum()/self.total_invest_chf*100
            tmp[k]=total

        self.market_ratio = self.market_ratio.append(tmp, ignore_index=True)

        return self.market_ratio