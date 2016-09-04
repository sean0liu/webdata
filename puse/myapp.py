# -*- coding:utf-8 -*- 
import pandas as pd
import numpy as np
import webdata.stock.trading as wt
import webdata.stock.fundamental as wf
import os,sys
try:
    import Quandl
except:
    import quandl as Quandl
import datetime,time
try:
    from io import StringIO
except:
    from pandas.compat import StringIO
token="ALM9oCUNixBCkHwyxJHF"
today = time.strftime("%Y-%m-%d")
start_time="2001-01-01"
end_time=today
bftoday=str(datetime.date.today()-datetime.timedelta(days=1))
import tushare as ts
def annlysis_shares_holdbyfund(code):
    pf='./stockdata/data/share_hold_by_fund.csv'
    df=pd.read_csv(pf,encoding='gbk',low_memory=False,index_col=0)
    df.code=df.code.map(lambda x:str(x).zfill(6))
    dff=df[df.code==code]
    dfff=dff.groupby('date')
    dffff=dfff.sum()
    return dffff

def get_myquandl(ticker):
    fn='./Quandl/'+ticker+'.csv'
    if not os.path.exists(fn):
        pf=os.path.split(fn)[0]
        #print pf
        if not os.path.exists(pf):
            os.mkdir(pf)
        print ('Getting Data for %s'% ticker)
        try:
            df= Quandl.get(ticker, authtoken=token, trim_start=start_time,trim_end=end_time)
            df.to_csv(fn)
            print (df.tail())
            return df
        except Exception as e:
            print (e)#"Getting data is error"
            #pass
            return
    else:
        all_data=pd.read_csv(fn)
        tem=all_data.iloc[-1]['Date']
        if tem != bftoday:
            t=time.strptime(tem,"%Y-%m-%d")
            y,m,d = t[0:3]
            tt=datetime.datetime(y,m,d)
            bd=tt+datetime.timedelta(days=1)
            bday=bd.strftime('%Y-%m-%d')
            all_data1 = pd.DataFrame()
            print ('Updating Data from %s for %s.'% (bday,ticker))
            try:
                df1= Quandl.get(ticker, authtoken=token, trim_start=bday,trim_end=end_time)
                df= all_data1.append(df1)
                if df.empty==False:
                    print (df1.tail())
                    df.to_csv(fn, header=None, mode='a')
                return df
            except Exception as e:
                print (e)#"Getting data is error"
                return

def get_myquandl_hdf5(ticker):
    h5path='./testh5df/Quandl.h5'
    if os.path.exists(h5path):
        h5 = pd.HDFStore(h5path,'a', complevel=4,complib='blosc')
    else:
        h5 = pd.HDFStore(h5path,'w', complevel=4,complib='blosc')
    try:
        dff=h5[ticker]
        tem=str(dff.index[-1])[0:10]
        if tem != bftoday:
            t=time.strptime(tem,"%Y-%m-%d")
            y,m,d = t[0:3]
            tt=datetime.datetime(y,m,d)
            bd=tt+datetime.timedelta(days=1)
            bday=bd.strftime('%Y-%m-%d')
            all_data1 = pd.DataFrame()
            print ('Updating Data from %s for %s.'% (bday,ticker))
            try:
                df1= Quandl.get(ticker, authtoken=token, trim_start=bday,trim_end=end_time)
                df2= all_data1.append(df1)
                if df2.empty==False:
                    df=dff.append(df2)
                    #print df1.tail()
                    h5[ticker]=df
                h5.close()
                return df
            except Exception as e:
                print (e)#"Getting data is error"
                return
    except Exception as e:
        print ('Getting Data for %s'% ticker)
        try:
            df= Quandl.get(ticker, authtoken=token, trim_start=start_time,trim_end=end_time)
            h5[ticker]=df
            print (df.tail())
            h5.close()
            return df
        except Exception as e:
            print (e)#"Getting data is error"
            return
            
def get_history_data_mp(code):
    h5path='./testh5df/stockdata_history.h5'
    if os.path.exists(h5path):
        h5 = pd.HDFStore(h5path,'a', complevel=4,complib='blosc')
    else:
        h5 = pd.HDFStore(h5path,'w', complevel=4,complib='blosc')
    try:
        ddf=h5[code]
        #dftem=datetime.datetime.strftime('%Y-%m-%d',ddf.index[-1])
        dftem=str(ddf.index[-1])[0:10]
        tem=dftem
        if tem != bftoday:
            print ('\nUpdating data from %s for %s:'%(tem,code))
            t=time.strptime(tem,"%Y-%m-%d")
            y,m,d = t[0:3]
            tt=datetime.datetime(y,m,d)
            bd=tt+datetime.timedelta(days=1)
            #if bd.weekday()==5:
            #    bd = bd+datetime.timedelta(days=2)
            #    print 'It is Sat'
            bday=bd.strftime('%Y-%m-%d')
            all_data1 = pd.DataFrame()
            all_data = wt.get_h_data(code,autype=None,start=bday, end=today)
            all_data1 = all_data1.append(all_data)
            if all_data1.empty==False:
                #print all_data1.head(1)
                #all_data1.sort_index(ascending=True,inplace=True)
                df=ddf.append(all_data1)
                h5[code]=df
                return df
    except Exception as e:
        print (e)
        print ('\nDownloading the data %s:'%code)
        df= wt.get_h_data(code,autype=None,start='2000-01-01', end=today)
        #df.sort_index(ascending=True,inplace=True)
        h5[code]=df
        #h5.close()
        return df

def get_data_last3year_mp(code):
    h5path='./testh5df/stockdata_last3year.h5'
    if os.path.exists(h5path):
        h5 = pd.HDFStore(h5path,'a', complevel=4,complib='blosc')
    else:
        h5 = pd.HDFStore(h5path,'w', complevel=4,complib='blosc')
    try:
        dff=h5[code]
        tem=str(dff.index[-1])[0:10]
        if tem < bftoday:
            print ('\nUpdating data from %s for %s:'%(tem,code))
            t=time.strptime(tem,"%Y-%m-%d")
            y,m,d = t[0:3]
            tt=datetime.datetime(y,m,d)
            bd=tt+datetime.timedelta(days=1)
            #if bd.weekday()==5:
            #    bd = bd+datetime.timedelta(days=2)
            #    print 'It is Sat'
            bday=bd.strftime('%Y-%m-%d')
            all_data1 = pd.DataFrame()
            try:
                all_data = wt.get_hist_data(code,start=bday, end=today)
                #print all_data
                all_data1 = all_data1.append(all_data)
                if all_data1.empty==False:
                    #all_data1.sort_index(ascending=True,inplace=True)
                    df=dff.append(all_data1)
                    #print df
                    h5[code]=df
                    return df
            except Exception as e:
                print (e,'No data for %s to upadate'%code)
                return 
    except Exception as e:
        print (e)
        print ('Getting the data for %s: \n'%code)
        df=wt.get_hist_data(code)
        #df.sort_index(ascending=True,inplace=True)
        h5[code]=df
        #h5.close()
        return df


def get_h_hdf5(code):
    """
    获取历史复权数据，分为前复权和后复权数据，接口提供股票上市以来所有历史数据，默认为前复权。如果不设定开始和结束日期，则返回近一年的复权数据，从性能上考虑，推荐设定开始日期和结束日期，而且最好不要超过三年以上，获取全部历史数据，请分年段分步获取，取到数据后，请及时在本地存储。
    """
    h5path='./testh5df/stockdata.h5'
    if os.path.exists(h5path):
        h5 = pd.HDFStore(h5path,'a', complevel=4,complib='blosc')
    else:
        h5 = pd.HDFStore(h5path,'w', complevel=4,complib='blosc')
    if code[0]=='0' or code[0]=='3' or code[0]=='2':
        label='M/sz'+code
    elif code[0]=='6' or code[0]=='9':
        label='M/ss'+code
    
    try:
        dd=h5[label]
        tem=str(dd.index[-1])[0:10]
        if tem!=today:
            if datetime.datetime.today().isoweekday() in [1,2,3,4,5]:
                #print 'Updating the data from%s for %s:'%(tem,code)
                t=time.strptime(tem,'%Y-%m-%d')
                y,m,d=t[0:3]
                tt=datetime.datetime(y,m,d)
                bd=tt+datetime.timedelta(days=1)
                bday=bd.strftime('%Y-%m-%d')
                df1=wt.get_h_data(code,start=bday,end=today)
                #df1=df1.sort_index(ascending=True,inplace=True)
                df=dd.append(df1)
                #df=df.sort_index(ascending=True)
                h5.append(label,df,data_columns=df.columns)
    except:
        df=wt.get_h_data(code)
        #df=df.sort_index(ascending=True)
        h5.append(label,df,data_columns=df.columns)
    #finally:
    #    h5.close()
    df.index=pd.to_datetime(df.index)
    return df

            


def get_hist_hdf5(code):
    """
    获取个股历史交易数据（包括均线数据），可以通过参数设置获取日k线、周k线、月k线，以及5分钟、15分钟、30分钟和60分钟k线数据
    """
    h5path='./testh5df/stockdata.h5'
    if os.path.exists(h5path):
        h5 = pd.HDFStore(h5path,'a', complevel=4,complib='blosc')
    else:
        h5 = pd.HDFStore(h5path,'w', complevel=4,complib='blosc')
    if code[0]=='0' or code[0]=='3' or code[0]=='2':
        label='l3y/sz'+code
    elif code[0]=='6' or code[0]=='9':
        label='l3y/ss'+code
    
    try:
        dd=h5[label]
        tem=str(dd.index[-1])[0:10]
        if tem!=today:
            if datetime.datetime.today().isoweekday() in [1,2,3,4,5]:
                #print 'Updating the data from%s for %s:'%(tem,code)
                t=time.strptime(tem,'%Y-%m-%d')
                y,m,d=t[0:3]
                tt=datetime.datetime(y,m,d)
                bd=tt+datetime.timedelta(days=1)
                bday=bd.strftime('%Y-%m-%d')
                df1=wt.get_hist_data(code,start=bday,end=today)
                df=dd.append(df1)
                #df=df.sort_index(ascending=True,inplace=True)
                h5.append(label,df,data_columns=df.columns)
    except:
        df=wt.get_hist_data(code)
        #df=df.sort_index(ascending=True,inplace=True)                
        h5.append(label,df,data_columns=df.columns)
    #finally:
    #    h5.close()
    df.index=pd.to_datetime(df.index)
    return df

def get_open_hist_hdf5(code,h5):
    """
    获取个股历史交易数据（包括均线数据），可以通过参数设置获取日k线、周k线、月k线，以及5分钟、15分钟、30分钟和60分钟k线数据
    """
    if code[0]=='0' or code[0]=='3' or code[0]=='2':
        label='l3y/sz'+code
    elif code[0]=='6' or code[0]=='9':
        label='l3y/ss'+code
    try:
        df=h5[label]
        #print(df)
        tem=str(df.index[-1])[0:10]
        if tem<today:
            if datetime.datetime.today().isoweekday() in [1,2,3,4,5]:
                t=time.strptime(tem,'%Y-%m-%d')
                y,m,d=t[0:3]
                tt=datetime.datetime(y,m,d)
                bd=tt+datetime.timedelta(days=1)
                bday=bd.strftime('%Y-%m-%d')
                df1=wt.get_hist_data(code,start=bday,end=today)
                #print(df1)
                df=df.append(df1)
                df.index=pd.to_datetime(df.index)
                #df=df.sort_index(ascending=True)
                #print(df)
                h5[label]=df
    except:
        df=wt.get_hist_data(code)
        #print (df)
        if df is not None:
            #df.index=pd.to_datetime(df.index)
            #df=df.sort_index(ascending=True)
            h5[label]=df
    finally:
        pass
    return df

def get_open_h_hdf5(code,h5):
    """
    获取个股全部历史交易数据
    """
    if code[0]=='0' or code[0]=='3' or code[0]=='2':
        label='M/sz'+code
    elif code[0]=='6' or code[0]=='9':
        label='M/ss'+code
    try:
        df=h5[label]
        tem=str(df.index[-1])[0:10]
        if tem<today:
            if datetime.datetime.today().isoweekday() in [1,2,3,4,5]:
                t=time.strptime(tem,'%Y-%m-%d')
                y,m,d=t[0:3]
                tt=datetime.datetime(y,m,d)
                bd=tt+datetime.timedelta(days=1)
                bday=bd.strftime('%Y-%m-%d')
                df1=wt.get_h_data(code,start=bday,end=today)
                df=df.append(df1)
                #df.index=pd.to_datetime(df.index)
                #df=df.sort_index(ascending=True)
                #print(df)
                h5[label]=df
    except:
        tem = wf.get_stock_basics()
        date=tem.ix[code]['timeToMarket']
        t=time.strptime(str(date),'%Y%m%d')
        startt=time.strftime('%Y-%m-%d',t)
        df=wt.get_h_data(code,start=startt,end=today)
        if df is not None:
            #df.index=pd.to_datetime(df.index)
            #df=df.sort_index(ascending=True)
            h5[label]=df
    finally:
        pass
    return df

def open_hdf5():
    h5path='./testh5df/stockdata.h5'
    if os.path.exists(h5path):
        h5 = pd.HDFStore(h5path,'a', complevel=4,complib='blosc')
    else:
        h5 = pd.HDFStore(h5path,'w', complevel=4,complib='blosc')
    return h5

def get_h_csv(code,index=False,autype='qfq'):
    """
    获取历史复权数据，分为前复权和后复权数据，接口提供股票上市以来所有历史数据，
    默认为前复权。如果不设定开始和结束日期，则返回近一年的复权数据，从性能上考虑，
    推荐设定开始日期和结束日期，而且最好不要超过三年以上，获取全部历史数据，
    请分年段分步获取，取到数据后，请及时在本地存储。
    index:False(提取非指数的数据;True(提取指数的数据)
    autype：主要是提取复权类型，None 表示不复权；qfq 前复权；hfq 后复权
    """
    if index:
        if code[0]=='0':
            tick='SS_'+code
        else:
            tick='SZ_'+code
        fn='./stockdata/data/history/'+tick+'.csv'
        if not os.path.exists(fn):
            df=wt.get_h_data(code,index=True,start='2000-01-01',end=today)
            df.to_csv(fn)
        else:
            df=pd.read_csv(fn,index_col='date')
            tem=str(df.index[-1])[0:10]
            #dftem=dftem.set_index('date')
            if tem < bftoday:
                print ('\nUpdating data from %s for %s:'%(tem,code))
                t=time.strptime(tem,"%Y-%m-%d")
                y,m,d = t[0:3]
                tt=datetime.datetime(y,m,d)
                bd=tt+datetime.timedelta(days=1)
                if bd.weekday()==5:
                    bd = bd+datetime.timedelta(days=2)
                bday=bd.strftime('%Y-%m-%d')
                all_data = ts.get_h_data(code,index=True,start=bday, end=today)
                if all_data is not None:
                    all_data.to_csv(fn, header=None, mode='a')
                    df=df.append(all_data)
    else:
        h5path='./stockdata/data/history/'+code+'.csv'
        if not os.path.exists(h5path):
            tem = wf.get_stock_basics()
            date=tem.ix[code]['timeToMarket']
            t=time.strptime(str(date),'%Y%m%d')
            startt=time.strftime('%Y-%m-%d',t)
            df=wt.get_h_data(code,autype=autype,start=startt,end=today)
            df.to_csv(h5path)
        else:
            df=pd.read_csv(h5path,index_col='date')
            tem=str(df.index[-1])[0:10]
            if tem<today:
                if datetime.datetime.today().isoweekday() in [1,2,3,4,5]:
                    t=time.strptime(tem,'%Y-%m-%d')
                    y,m,d=t[0:3]
                    tt=datetime.datetime(y,m,d)
                    bd=tt+datetime.timedelta(days=1)
                    bday=bd.strftime('%Y-%m-%d')
                    df1=wt.get_h_data(code,autype=autype,start=bday,end=today)
                    if df1 is not None:
                        df=df.append(df1)
                        df1.to_csv(h5path,mode='a',header=None)
    return df

def get_hist_csv(code):
    
    """
    获取个股历史交易数据（包括均线数据），可以通过参数设置获取
    日k线、周k线、月k线，以及5分钟、15分钟、30分钟和60分钟k线数据
    """
    h5path='./stockdata/data/last3year/'+code+'.csv'
    if not os.path.exists(h5path):
        df=wt.get_hist_data(code)
        if df is not None:
            #df.index=pd.to_datetime(df.index)
            #df=df.sort_index(ascending=True)
            df.to_csv(h5path)
    else:
        df=pd.read_csv(h5path,index_col='date')
        tem=str(df.index[-1])[0:10]
        if tem!=today:
            if datetime.datetime.today().isoweekday() in [1,2,3,4,5]:
                t=time.strptime(tem,'%Y-%m-%d')
                y,m,d=t[0:3]
                tt=datetime.datetime(y,m,d)
                bd=tt+datetime.timedelta(days=1)
                bday=bd.strftime('%Y-%m-%d')
                df1=wt.get_hist_data(code,start=str(bday),end=str(today))
                if df1 is not None:
                    #df1.index=pd.to_datetime(df.index)
                    #df1=df1.sort_index(ascending=True)
                    df=df.append(df1)
                    df1.to_csv(h5path,mode='a',header=None)
    return df

def print_return_next_n_day(dd):
    #print
    print ('历史上这只股票%s出现买入信号的次数为%d，这股票在：'%(code,dd.shape[0]))
    #print
    for n in [1, 2, 3, 5, 10, 20]:
        print ("金叉之后的%d个交易日内，" % n,)
        print ("平均涨幅为%.2f%%，" % (dd['CP_next_'+str(n)+'_days'].mean()*100),)
        print ("最高涨幅为%.2f%%，" % (dd['CP_next_'+str(n)+'_days'].max()*100),)
        print ("最大跌涨幅为%.2f%%，" % (dd['CP_next_'+str(n)+'_days'].min()*100),)
        print ("其中上涨的概率是%.2f%%。" % \
            (dd[dd['CP_next_'+str(n)+'_days'] > 0].shape[0]/float(dd.shape[0]) * 100))
        #    print all_stock[all_stock['接下来'+str(n)+'个交易日涨跌幅'] > 0].shape[0],all_stock.shape[0]
    return

def return_for_period(stock_data):
    stock_data['p_change_period'] = (stock_data['p_change']) * stock_data['position']
    year_rtn = stock_data.set_index('date')[['p_change', 'p_change_period']].\
               resample('A', how=lambda x: (x/100+1.0).prod() - 1.0) * 100
    return stock_data

def Make_decision(stock_data):
    if (stock_data.iloc[-1]['position']==1)&(stock_data.iloc[-2]['position']==1):
        print ('持有这只股票Holding %s.'%code)
    elif (stock_data.iloc[-1]['position']==1)&(stock_data.iloc[-2]['position']==0):
        print ('开始买进这只股票Buy %s.'%code)
    elif (stock_data.iloc[-1]['position']==0)&(stock_data.iloc[-2]['position']==1):
        print ('开始卖出这只股票Sell %s.'%code)
    else:
        print ('保持空仓Keeping Short Position %s.'%code)
    #print '================================================================='
    return

def print_return_next_n_day(dd):
    #print
    print ('历史上这只股票%s出现买入信号的次数为%d，这股票在：'%(code,dd.shape[0]))
    #print
    for n in [1, 2, 3, 5, 10, 20]:
        print ("金叉之后的%d个交易日内，" % n,)
        print ("平均涨幅为%.2f%%，" % (dd['CP_next_'+str(n)+'_days'].mean()*100),)
        print ("最高涨幅为%.2f%%，" % (dd['CP_next_'+str(n)+'_days'].max()*100),)
        print ("最大跌涨幅为%.2f%%，" % (dd['CP_next_'+str(n)+'_days'].min()*100),)
        print ("其中上涨的概率是%.2f%%。" % \
            (dd[dd['CP_next_'+str(n)+'_days'] > 0].shape[0]/float(dd.shape[0]) * 100))
        #    print all_stock[all_stock['接下来'+str(n)+'个交易日涨跌幅'] > 0].shape[0],all_stock.shape[0]
        #print
    return

def return_for_period(stock_data):
    # ==========计算每年指数的收益以及海龟交易法则的收益
    stock_data['p_change_period'] = (stock_data['p_change']) * stock_data['position']
    year_rtn = stock_data.set_index('date')[['p_change', 'p_change_period']].\
               resample('A', how=lambda x: (x/100+1.0).prod() - 1.0) * 100
    return stock_data

def Make_decision(stock_data):
    if (stock_data.iloc[-1]['position']==1)&(stock_data.iloc[-2]['position']==1):
        print ('持有这只股票Holding %s.'%code)
    elif (stock_data.iloc[-1]['position']==1)&(stock_data.iloc[-2]['position']==0):
        print ('开始买进这只股票Buy %s.'%code)
    elif (stock_data.iloc[-1]['position']==0)&(stock_data.iloc[-2]['position']==1):
        print ('开始卖出这只股票Sell %s.'%code)
    else:
        print ('保持空仓Keeping Short Position %s.'%code)
    #print '================================================================='
    return


def analysis_kdjv1(code):
    filename='./stockdata/data/last3year/'+code+'.csv'
    stock_dataT = pd.read_csv(filename, parse_dates=['date'],encoding='gbk')
    stock_data=stock_dataT.loc[:,('date', 'high', 'low', 'close', 'p_change')].copy()
    # 计算KDJ指标
    stock_data['low_list'] = pd.Series.rolling(stock_data['low'],window=9,center=False).min()
    stock_data['low_list'].fillna(value=stock_data['low'].expanding(min_periods=1).min())
    stock_data['high_list']=pd.Series.rolling(stock_data['high'],window=9,center=False).max()
    stock_data['high_list'].fillna(value=stock_data['high'].expanding(min_periods=1).max())
    stock_data['rsv'] = (stock_data['close'] - stock_data['low_list']) / (stock_data['high_list'] - stock_data['low_list']) * 100
    stock_data['KDJ_K'] = pd.Series.ewm(stock_data['rsv'],ignore_na=False,min_periods=0,adjust=True,com=2).mean()
    stock_data['KDJ_D'] = pd.Series.ewm(stock_data['KDJ_K'],ignore_na=False,min_periods=0,adjust=True,com=2).mean()
    stock_data['KDJ_J'] = 3 * stock_data['KDJ_K'] - 2 * stock_data['KDJ_D']
    # 计算KDJ指标金叉、死叉情况
    ###通常就敏感性而言，J值最强，K值次之，D值最慢，而就安全性而言，J值最差，K值次之，D值最稳
    ##金叉用1表示，死叉用0表示
    buyi=stock_data[(stock_data['KDJ_K'] > stock_data['KDJ_D'])&(stock_data['KDJ_K'].shift(-1) < stock_data['KDJ_D'].shift(-1))].index
    stock_data.loc[buyi,'Signal'] = 0
    selli=stock_data[(stock_data['KDJ_K'] < stock_data['KDJ_D'])&(stock_data['KDJ_K'].shift(-1) > stock_data['KDJ_D'].shift(-1))].index
    stock_data.loc[selli,'Signal'] = 1
    ##测试反向操作的效果，即买进信号则卖出，卖出信号则买进。
    stock_data['position']=stock_data['Signal'].shift(1)
    stock_data['position'].fillna(method='ffill', inplace=True)
    #当仓位为1时，已当天的开盘价买入股票，当仓位为0时，以收盘价卖出该股份。计算从数据期内的收益
    stock_data['Cash_index'] = ((stock_data['p_change']/100) * stock_data['position'] + 1.0).cumprod()
    #initial_idx = stock_data.iloc[0]['close'] / (1 + (stock_data.iloc[0]['p_change']/100))
    initial_idx = 1
    stock_data['Cash_index'] *= initial_idx
    print ('The KDJ Forwards methon Signal:')
    Make_decision(stock_data)
    # 通过复权价格计算接下来几个交易日的收益率
    for n in [1, 2, 3, 5, 10, 20]:
        stock_data['CP_next_'+str(n)+'_days'] =(stock_data['close'].shift(-1*n) / stock_data['close'] - 1.0)
    dd=stock_data[stock_data['Signal']==1]
    #print_return_next_n_day(dd)
    codedir='./output/A/'+code+os.sep
    if not os.path.exists(codedir):
        os.mkdir(codedir)
    # ===计算每年指数的收益
    stock_data['p_change_period'] = (stock_data['p_change']) * stock_data['position']
    year_rtn = stock_data.set_index('date')[['p_change', 'p_change_period']].resample('A').apply(lambda x: ((x/100+1.0).prod() - 1.0) * 100)
    year_rtn.to_csv(codedir+'kdjv1_year.csv', encoding='gbk')
    #按月计算收益
    stock_data['p_change_period_for_Month'] = (stock_data['p_change']) * stock_data['position']
    month_rtn = stock_data.set_index('date')[['p_change', 'p_change_period_for_Month']].resample('M').apply(lambda x: ((x/100+1.0).prod() - 1.0) * 100)
    month_rtn.to_csv(codedir+'kdjv1_month.csv', encoding='gbk')
    stock_data.to_csv(codedir+'kdjv1.csv',encoding='gbk',index=False)
    stock_data.tail(20).to_csv(codedir+'kdjv1_Signal.csv',encoding='gbk',index=False)
    return

def tutlemethon(code):
    filename='./stockdata/data/last3year/'+code+'.csv'
    #    if len(code)==6:
    index_data = pd.read_csv(filename, parse_dates=['date'])
    # 保留这几个需要的字段：'date', 'high', 'low', 'close', 'change'
    index_data = index_data[['date','open', 'high', 'low', 'close', 'p_change']]
    # 对数据按照【date】交易日期从小到大排序
    #index_data.sort('date', inplace=True)
    # ==========计算海龟交易法则的买卖点
    # 设定海龟交易法则的两个参数，当收盘价大于最近N1天的最高价时买入，当收盘价低于最近N2天的最低价时卖出
    # 这两个参数可以自行调整大小，但是一般N1 > N2
    N1 = 20
    N2 = 10
    # 通过rolling_max方法计算最近N1个交易日的最高价
    index_data['High_Close_Price_N1_Day'] =  pd.Series.rolling(index_data['high'],window=N1,center=False).max()
    # 对于上市不足N1天的数据，取上市至今的最高价
    index_data['High_Close_Price_N1_Day'].fillna(value=index_data['high'].expanding(min_periods=1).max())
    # 通过相似的方法计算最近N2个交易日的最低价
    index_data['Low_Close_Price_N2_Day'] =  pd.Series.rolling(index_data['low'],window=N2,center=False).min()
    # 对于上市不足N2天的数据，取上市至今的最低价
    index_data['Low_Close_Price_N2_Day'].fillna(value=index_data['low'].expanding(min_periods=1).min())
    # 当当天的【close】> 昨天的【最近N1个交易日的最高点】时，将【收盘发出的信号】设定为1
    buy_index = index_data[index_data['close'] > index_data['High_Close_Price_N1_Day'].shift(1)].index
    index_data.loc[buy_index, 'Signal'] = 1
    # 当当天的【close】< 昨天的【最近N2个交易日的最低点】时，将【收盘发出的信号】设定为0
    sell_index = index_data[index_data['close'] < index_data['Low_Close_Price_N2_Day'].shift(1)].index
    index_data.loc[sell_index, 'Signal'] = 0
    # 计算每天的仓位，当天持有上证指数时，仓位为1，当天不持有上证指数时，仓位为0
    index_data['position'] = index_data['Signal'].shift(1)
    index_data['position'].fillna(method='ffill', inplace=True)
    # 取1992年之后的数据，排出较早的数据
    #index_data = index_data[index_data['date'] >= pd.to_datetime('19930101')]
    #当仓位为1时，已当天的开盘价买入股票，当仓位为0时，以收盘价卖出该股份。计算从数据期内的收益
    index_data['Cash_index'] = ((index_data['p_change']/100) * index_data['position'] + 1.0).cumprod()
    #initial_idx = index_data.iloc[0]['close'] / (1 + (index_data.iloc[0]['p_change']/100))
    initial_idx = 1
    index_data['Cash_index'] *= initial_idx
    print ('The turtle methon Signal:')
    Make_decision(index_data)
    # 通过复权价格计算接下来几个交易日的收益率
    for n in [1, 2, 3, 5, 10, 20]:
        index_data['CP_next_'+str(n)+'_days'] = index_data['close'].shift(-1*n) / index_data['close'] - 1.0
    dd=index_data[index_data['position']==1]
    # 输出数据到指定文件
    #codedir='./output/A/'+code+os.sep
    if not os.path.exists(codedir):
        os.mkdir(codedir)   
    index_data[['date', 'high', 'low', 'close', 'p_change', 'High_Close_Price_N1_Day','Low_Close_Price_N2_Day', 'position', 'Cash_index']].to_csv(codedir+'turtle.csv', index=False, encoding='gbk')
        
    # ==========计算每年指数的收益以及海龟交易法则的收益
    index_data['p_change_turtle'] = (index_data['p_change']) * index_data['position']
    #year_rtn = index_data.set_index('date')[['p_change', 'p_change_turtle']].resample('A', how=lambda x: (x/100+1.0).prod() - 1.0) * 100
    year_rtn = index_data.set_index('date')[['p_change', 'p_change_turtle']].resample('A').apply(lambda x: ((x/100+1.0).prod() - 1.0) * 100)
    year_rtn.to_csv(codedir+'tuetle_year.csv', encoding='gbk')
    index_data.tail(20).to_csv(codedir+'turtle_Signal.csv', index=False, encoding='gbk')
    return
