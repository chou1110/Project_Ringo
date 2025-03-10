import numpy as np
import pandas as pd
import streamlit as st
import math as math
import datetime

from workalendar.asia import Taiwan 

##== Sub Process ==##
def get_workday(date_in):
    month_estimate   = date_in.month
    month_addone     = 12 if (month_estimate+1)%12 == 0 else (month_estimate+1)%12

    if month_addone != 1:
        totaldays        = (date_in.replace(month = month_addone) - date_in).days
        workdays         = np.busday_count(date_in, date_in.replace(month = month_addone))
        holidays         = totaldays - workdays
    else: 
        totaldays        = (date_in.replace(year = date_in.year+1, month = month_addone) - date_in).days
        workdays         = np.busday_count(date_in, date_in.replace(year = date_in.year+1, month = month_addone))
        holidays         = totaldays - workdays
    return workdays, holidays, totaldays


def get_hour_value(month, val_max=5000, val_std=1800): # val_max, val_min default value generate by chat gpt
    
    ls_hour = range(0,24)
    ls_peak = list(range(7, 19))

    dict_ratio_weekday = dict(zip(ls_hour, [1 if h in ls_peak else 0.5 for h in ls_hour]))
    dict_ratio_weekend = dict(zip(ls_hour, [0.5 for h in ls_hour]))

    data = pd.DataFrame()
    data['hour']  = ls_hour
    data['month'] = month
    data['rate_weekday']  = data['hour'].map(dict_ratio_weekday)
    data['rate_weekend']  = data['hour'].map(dict_ratio_weekend)
    
    data['mean_weekday'] = val_max * data['rate_weekday']
    data['std_weekday']  = val_std * data['rate_weekday']
    data['mean_weekend'] = val_max * data['rate_weekend']
    data['std_weekend']  = val_std * data['rate_weekend']
    
    data['value_weekday'] = np.random.normal(data['mean_weekday'], data['std_weekday'])*0.9 // 100 * 100
    data['value_weekend'] = np.random.normal(data['mean_weekend'], data['std_weekend'])*0.9 // 100 * 100
    data['value_weekday'] = data['value_weekday'].clip(lower=0)
    data['value_weekend'] = data['value_weekend'].clip(lower=0)

    data = data[['month', 'hour', 'value_weekday', 'value_weekend']]
    
    return data


def get_month_value(df_strategy, estimate_date):
    workdays, holidays, totaldays = get_workday(estimate_date)
    strategy_weekday = df_strategy['value_weekday'].sum() * workdays
    strategy_holiday = df_strategy['value_weekend'].sum() * holidays
    return round((strategy_weekday+strategy_holiday)/1000), totaldays 


def get_tracking(df_hour):
    cal_tw = Taiwan()  # Use a country-specific calendar
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    start = today - datetime.timedelta(30)
    ls_datehour = pd.date_range(start, today, freq='H')
    ls_datehour_today = pd.date_range(today, tomorrow, freq='H')
    data = pd.DataFrame()
    data['date_hour'] = ls_datehour
    data['date'] = data['date_hour'].dt.date
    data['hour'] = data['date_hour'].dt.hour
    data['month'] = pd.to_datetime(data['date']).dt.to_period('M').dt.to_timestamp()
    data['isholiday'] = data['date'].apply(cal_tw.is_holiday)
    data.loc[data['isholiday'],'date_type'] = 'holiday'
    data.loc[~data['isholiday'],'date_type'] = 'weekday'
    
    data_weekday = data.query("not isholiday")
    data_holiday = data.query("isholiday")
    data_weekday = data_weekday.merge(df_hour[['hour', 'value_weekday']]).rename(columns={'value_weekday':'strategy'})
    data_holiday = data_holiday.merge(df_hour[['hour', 'value_weekend']]).rename(columns={'value_weekend':'strategy'})
    
    data = pd.concat([data_weekday, data_holiday])
    data['buffer'] = data['strategy']*0.25
    data['action'] = np.random.normal(data['strategy'], data['buffer']/5*3)
    data['action'] = data['action'].clip(lower=0)
    data['under']  = data['action'] > (data['strategy'] + data['buffer']) 
    data['over']   = data['action'] < (data['strategy'] - data['buffer']) 

    data_today = pd.DataFrame()
    data_today['date_hour'] = ls_datehour_today
    data_today['date'] = data_today['date_hour'].dt.date
    data_today['hour'] = data_today['date_hour'].dt.hour
    data_today['month'] = pd.to_datetime(data_today['date']).dt.to_period('M').dt.to_timestamp()
    data_today['isholiday'] = data_today['date'].apply(cal_tw.is_holiday)
    data_today.loc[data_today['isholiday'],'date_type'] = 'holiday'
    data_today.loc[~data_today['isholiday'],'date_type'] = 'weekday'
    
    data_today_weekday = data_today.query("not isholiday")
    data_today_holiday = data_today.query("isholiday")
    data_today_weekday = data_today_weekday.merge(df_hour[['hour', 'value_weekday']]).rename(columns={'value_weekday':'strategy'})
    data_today_holiday = data_today_holiday.merge(df_hour[['hour', 'value_weekend']]).rename(columns={'value_weekend':'strategy'})

    data_today = pd.concat([data_today_weekday, data_today_holiday])
    data_today['buffer'] = data_today['strategy']*0.25

    data = pd.concat([data, data_today])
    data = data.sort_values('date_hour').reset_index(drop=True)
    return data 


def get_tracking_stats(df_tracking, theDate):
    
    thisMonth = theDate.replace(day=1)
    lastMonth = thisMonth - pd.DateOffset(months=1)

    df_tracking_today = df_tracking[pd.to_datetime(df_tracking['month']) == pd.to_datetime(thisMonth)]
    df_tracking_last  = df_tracking[pd.to_datetime(df_tracking['month']) == pd.to_datetime(lastMonth)]

    # Over and Under Stats
    tracking_stats    = df_tracking_today.groupby('hour')[['over', 'under']].sum().reset_index()
    
    # Part Over
    if tracking_stats['over'].max() == 0:
        hour_over  = -1
        count_over = 0
    else:
        max_over   = tracking_stats[tracking_stats['over'] == tracking_stats['over'].max()]
        hour_over  = max_over.iloc[0]['hour']
        count_over = max_over.iloc[0]['over']
    
    hour_count_over = [hour_over, count_over]

    # Part Underdf_tracking
    if tracking_stats['under'].max() == 0:
        hour_underbid  = -1
        count_underbid = 0
    else:
        max_undrbid  = tracking_stats[tracking_stats['under'] == tracking_stats['under'].max()]
        hour_underbid  = max_undrbid.iloc[0]['hour']
        count_underbid = max_undrbid.iloc[0]['under']
    
    hour_count_under = [hour_underbid, count_underbid]
    
    # Part Close
    count_hours = df_tracking_today[~df_tracking_today['action'].isna()].shape[0]
    count_miss  = df_tracking_today['under'].sum() + df_tracking_today['over'].sum()
    close_rate  = (count_hours-count_miss) / count_hours

    count_hours_last = df_tracking_last[~df_tracking_last['action'].isna()].shape[0]
    count_miss_last  = df_tracking_last['under'].sum() + df_tracking_last['over'].sum()
    close_rate_last  = (count_hours_last-count_miss_last) / count_hours_last

    close_rates = [close_rate, close_rate_last]
    
    return hour_count_over, hour_count_under, close_rates, tracking_stats

@st.cache_data(ttl=28800)
def get_month_trend(date_in):
    dict_ratio = [0.9239,0.8152,0.8696,0.8913,0.9022,0.9239,0.9783,1.0,0.9457,0.9239,0.9022,0.7935]
    dict_ratio = dict(zip(range(1,13), dict_ratio))

    def get_month_start(date_in, n_month=0):
        ret = date_in.replace(day=1)
        for _ in range(n_month):
            ret = ret + datetime.timedelta(32)
            ret = ret.replace(day=1)
        return ret

    def generate_data_1(ls_date, dict_ratio, val_max=5000, val_std=1800):
        data = pd.DataFrame()
        data['date']  = ls_date
        data['month'] = data['date'].dt.month
        data['rate']  = data['month'].map(dict_ratio)
        
        data['val_mean'] = val_max * data['rate']
        data['val_std']  = val_std * data['rate']
        
        data['avg_value'] = np.random.normal(data['val_mean'], data['val_std'])
        data['avg_value'] = data['avg_value'].clip(lower=0)
        data = data[['date', 'avg_value']]
        return data

    start = datetime.date(2024,1,1)
    today = get_month_start(date_in)
    end2  = get_month_start(date_in, 3)

    ls_date1 = pd.date_range(start, today, freq='MS')
    ls_date2 = pd.date_range(today, end2, freq='MS')

    df_trend    = generate_data_1(ls_date1, dict_ratio)
    df_estimate = generate_data_1(ls_date2[1:], dict_ratio)
    df_estimate = pd.concat([df_trend[-1:], df_estimate]).reset_index(drop=True)
    
    return df_trend, df_estimate