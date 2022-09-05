# streamlit_app.py

import streamlit as st
import psycopg2
import pandas as pd
import numpy as np
from sshtunnel import SSHTunnelForwarder

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
#    return psycopg2.connect(**st.secrets["postgres"])

#    keepalive_kwargs = {
#        "keepalives": 1,
#        "keepalives_idle": 60,
#        "keepalives_interval": 10,
#        "keepalives_count": 5
#    }

    ssh_tunnel = SSHTunnelForwarder(
        (st.secrets["ssh"].ssh_server, 22),
        ssh_username=st.secrets["ssh"].ssh_user,
        ssh_private_key=st.secrets["ssh"].ssh_pkey,
        remote_bind_address=(st.secrets["ssh"].ssh_bind, 5432)
    )

    ssh_tunnel.start()
    port = ssh_tunnel.local_bind_port
    return psycopg2.connect(**st.secrets["momt-prod"], port=port)

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("SELECT NOW();")

# Print results.
for row in rows:
    st.write(f"{row[0]}, :{row[1]}:, :{row[2]}:, :{row[3]}:, :{row[4]}:, :{row[5]}:, :{row[6]}:, :{row[7]}:")

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)
