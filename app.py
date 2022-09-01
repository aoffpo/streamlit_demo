from datetime import date
from socket import create_server

import altair as alt
import pandas as pd
# use appropriate connector for your data source
import snowflake.connector as sf

import streamlit as st

sidebar = st.sidebar
st.set_page_config(layout='wide')


def connect_to_snowflake(acct, user, pwd, rl, wh, db):
    ctx = sf.connect(user=user,
                     account=acct,
                     password=pwd,
                     role=rl,
                     warehouse=wh,
                     database=db)
    cs = ctx.cursor()
    st.session_state['snow_conn'] = cs

    st.session_state['is_ready'] = True
    return cs


# you can set local cache instead of using SF's cache
# you can also use pycache/ other caching impl.
# this can prevent using (and paying for) compute in Snowflake
@st.cache(suppress_st_warning=True, show_spinner=False)
def get_data():
    query = 'SELECT * FROM COMFORMED.FINANCIAL_DATA_UNPAID;'
    results = st.session_state['snow_conn'].execute(query)
    results = st.session_state['snow_conn'].fetch_pandas_all()
    return results


# run once won't redisplay on filter changes
@st.cache(suppress_st_warning=True, show_spinner=False)
def render_chart(df):
    summary = alt.Chart(df).mark_bar().encode(
            x='MONTH_ID',
            y='sum(NET_BALANCE):Q'
        )

    st.altair_chart(summary, use_container_width=True)


with sidebar:
    file_path = st.file_uploader('Upload your file or add connection info')

    account = st.text_input('Account')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    role = st.text_input('Role')
    warehouse = st.text_input('Warehouse')
    database = st.text_input('Database')

    connect = st.button('Connect to Snowflake',
                        on_click=connect_to_snowflake,
                        args=[account, username, password, role, warehouse, database])  # nopep8

    if 'is_ready' not in st.session_state:
        st.session_state['is_ready'] = False

    if st.session_state['is_ready'] is True:
        # Data + Behavior - create tabs
        # filters, tables, charts = st.tabs('Filter','Tables','Charts')
        # or columns

        filters, tables, charts = st.columns('Filter', 'Tables', 'Charts')

        data = get_data()

        # for use as filter for viz and df's to filter from cache
        balances = data['NET_BALANCE'].agg('min', 'max')
        # arrange in colums from line 53
        with filters:
            min, max = st.slider('Balance_Range',
                                 min_value=float(balances['min']),
                                 max_value=float(balances['max']),
                                 value=[float(balances['min']), float(balances['max'])])  # nopep8

        with tables:
            data.loc[data['NET_BALANCE']].between(min, max)

        # st.bar_chart(data, 'Balances', x='MONTH_NAME', y='NET_BALANCE')
        # in 1.10, use altair
        # render_chart(data)
        summary = alt.Chart(data.loc[data['NET_BALANCE']
                            .between(min, max)]).mark_bar() \
                     .encode(x='MONTH_ID',
                             y='sum(NET_BALANCE):Q'
                             )

        # st.altair_chart(summary, use_container_width=True)

        average = alt.Chart(data.loc[data['NET_BALANCE']
                            .between(min, max)]).mark_line() \
                     .encode(x='MONTH_ID:N',
                             y='avg(NET_BALANCE):Q'
                             )
        st.altair_chart(summary + average, use_container_width=True)

        # st.write to create chart for each day of the week
        # probably bad visualation type for this data set
        for days in list(data['DAY_NAME'].unique()):
            st.write(days, key='{days}')
            chart = alt.Chart(data.loc[data['DAY_NAME'] == days]).mark_bar().encode(  # nopep8
                x='BALANCE_DATE:T',   # temporal field
                y='sum(NET_BALANCE):Q'  # quantative field
            )
            st.altair_chart(chart, use_container_width=True)

    # bring a file in as data source
    if (file_path is not None):
        if file_path.name.__contains__('json'):
            json = pd.read_json(file_path)
            st.altair_chart(json, use_container_width=True)
        else:
            csv = pd.read_csv(file_path)
            st.altair_chart(csv, use_container_width=True)

    # camera input
    # st.camera_input('Get photo from camera')

    # other application -- create dataset generator using streamlit

    # react components available

    # Use Case:  Interactive data, instead of static dashboards and charts
