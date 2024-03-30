import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

st.set_page_config(
    page_title="NSE-STOCK OPTION ANALYSIS",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("NSE - STOCK OPTION ANALYSIS")
st.divider()

st.sidebar.title("NSE - STOCK OPTION ANALYSIS")
st.sidebar.subheader('Upload F&O bhavcopy Files', divider='grey')
uploaded_file_fo = st.sidebar.file_uploader('Upload F&O bhavcopy Files', type=['csv'])

st.sidebar.subheader('Upload Equity bhavcopy Files', divider='grey')
uploaded_file_eq = st.sidebar.file_uploader('Upload Equity bhavcopy Files', type=['csv'])

filtered_eq_df = None
filtered_fo_df = None

if uploaded_file_fo is not None:
    df_fo = pd.read_csv(uploaded_file_fo)
    df_fo['EXPIRY_DT'] = pd.to_datetime(df_fo['EXPIRY_DT'], format='%d-%b-%Y')
    filtered_fo_df = df_fo[(df_fo['INSTRUMENT'] == 'FUTSTK') & (df_fo['EXPIRY_DT'] == pd.to_datetime('2024-03-28'))]

if uploaded_file_eq is not None:
    df_eq = pd.read_csv(uploaded_file_eq)
    filtered_eq_df = df_eq[df_eq['SERIES'] == 'EQ']

if filtered_eq_df is not None and filtered_fo_df is not None:
    main_df = pd.merge(filtered_eq_df, filtered_fo_df, on='SYMBOL', how='left')
    df = main_df.dropna(subset=['CHG_IN_OI']).copy()
    df['price_change'] = df['CLOSE_x'].sub(df['PREVCLOSE'], fill_value=0)

    conditions = [
        df['price_change'] < 0,
        df['price_change'] >= 0
    ]

    choices = [
        'Negative',
        'Positive'
    ]

    df['change'] = np.select(conditions, choices)

    conditions = [
        df['CHG_IN_OI'] < 0,
        df['CHG_IN_OI'] >= 0
    ]

    choices = [
        'Negative',
        'Positive'
    ]

    df['change_oi'] = np.select(conditions, choices)

    conditions = [
        (df['change'] == 'Positive') & (df['change_oi'] == 'Positive'),
        (df['change'] == 'Negative') & (df['change_oi'] == 'Negative'),
        (df['change'] == 'Positive') & (df['change_oi'] == 'Negative'),
        (df['change'] == 'Negative') & (df['change_oi'] == 'Positive'),
    ]

    choices = [
        'Long Buildup',
        'Long Unwinding',
        'Short Covering',
        'Short Buildup'
    ]

    df['interpret_01'] = np.select(conditions, choices)

    conditions = [
        df['interpret_01'] == 'Long Buildup',
        df['interpret_01'] == 'Long Unwinding',
        df['interpret_01'] == 'Short Covering',
        df['interpret_01'] == 'Short Buildup'
    ]

    choices = [
        'BUYING',
        'Buyer Exit',
        'Seller Exit',
        'SELLING'
    ]

    df['interpret_02'] = np.select(conditions, choices)

    conditions = [
        df['interpret_02'] == 'BUYING',
        df['interpret_02'] == 'Buyer Exit',
        df['interpret_02'] == 'Seller Exit',
        df['interpret_02'] == 'SELLING'
    ]

    choices = [
        'Bullish',
        'Moderate Bearish',
        'Moderate Bullish',
        'Bearish'
    ]

    df['interpret_03'] = np.select(conditions, choices)

    columns_to_remove = ['SERIES', 'OPEN_x', 'HIGH_x', 'LOW_x', 'LAST', 'TOTTRDQTY',
                         'TOTTRDVAL', 'TIMESTAMP_x', 'TOTALTRADES', 'ISIN', 'Unnamed: 13', 'INSTRUMENT', 'EXPIRY_DT',
                         'STRIKE_PR', 'OPTION_TYP', 'OPEN_y', 'HIGH_y', 'LOW_y', 'CLOSE_y', 'SETTLE_PR', 'CONTRACTS',
                         'VAL_INLAKH', 'TIMESTAMP_y', 'Unnamed: 15']

    df = df.drop(columns_to_remove, axis=1)


    def format_change_price(val):
        if val < 0:
            return 'background-color: #ffbfbf'
        elif val >= 0:
            return 'background-color: #86e888'
        else:
            return ''


    def format_change(val):
        if val == 'Positive':
            return 'background-color: #86e888'
        elif val == 'Negative':
            return 'background-color: #ffbfbf'
        else:
            return ''

    def format_change_oi(val):
        if val == 'Positive':
            return 'background-color: #86e888'
        elif val == 'Negative':
            return 'background-color: #ffbfbf'
        else:
            return ''


    def interpret_01(val):
        if val == 'Short Covering':
            return 'background-color: #bfffbf'
        elif val == 'Long Buildup':
            return 'background-color: #008000'
        elif val == 'Long Unwinding':
            return 'background-color: #ffbfbf'
        elif val == 'Short Buildup':
            return 'background-color: #b30000'
        else:
            return ''

    def interpret_02(val):
        if val == 'Seller Exit':
            return 'background-color: #86e888'
        elif val == 'Buyer Exit':
            return 'background-color: #ffbfbf'
        else:
            return ''

    def interpret_03(val):
        if val == 'Moderate Bullish':
            return 'background-color: #bfffbf'
        elif val == 'Bullish':
            return 'background-color: #008000'
        elif val == 'Moderate Bearish':
            return 'background-color: #ffbfbf'
        elif val == 'Bearish':
            return 'background-color: #b30000'
        else:
            return ''

    styled_df = df.style.applymap(format_change_price, subset=['price_change'])\
        .applymap(format_change, subset=['change'])\
        .applymap(format_change_oi, subset=['change_oi'])\
        .applymap(interpret_01, subset=['interpret_01'])\
        .applymap(interpret_02, subset=['interpret_02'])\
        .applymap(interpret_03, subset=['interpret_03'])

    df = st.dataframe(styled_df, hide_index=True, width=1200, height=900, use_container_width=False,)

    # st.write(styled_df, unsafe_allow_html=True)


    # st.dataframe(df, use_container_width=False,  width=1800, hide_index=True)

