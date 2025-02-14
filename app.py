import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from functions import *

st.set_page_config(
    page_title="Portail Cinergie",
    page_icon=":fire:",
    layout="wide"
)


st.title("Portail Cinergie")
st.markdown("##### Le but de ce dashboard est de visualiser les données de production et de consommation des cogénérations et des échangeurs de chaleur, ainsi que de repérer les anomalies de fonctionnement du réseau de chaleur.")
cogen_file = st.sidebar.file_uploader('Importez le fichier csv des cogénérations', 'csv', key = 'cogen_file')
heat_exchanger_file = st.sidebar.file_uploader('Importez le fichier csv des échangeurs de chaelur', 'csv', key = 'heat_exchanger_file')

if cogen_file is not None and heat_exchanger_file is not None:
    df_cogen = pd.read_csv(cogen_file, sep = ';')
    df_heat_exchanger = pd.read_csv(heat_exchanger_file, sep = ';')

    set_timestamp(df_cogen)
    set_timestamp(df_heat_exchanger)

    df_heat_exchanger['dT_RU'] = df_heat_exchanger['Tc_RU'] - df_heat_exchanger['Tf_RU']
    df_cogen['Total_Gen_P'] = df_cogen['JEN1_P'] + df_cogen['JEN2_P'] + df_cogen['LIEB_P']

    # st.dataframe(df_cogen)
    # st.dataframe(df_heat_exchanger)
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("Températures réseau urbain")
        num_Tc_RU = len(df_heat_exchanger[df_heat_exchanger['Tc_RU'] > 74])
        num_total = len(df_heat_exchanger['Tc_RU'])
        st.markdown(f"La température de départ est supérieure ou égale à 74°C **{np.round((num_Tc_RU /num_total)*100,0)}% du temps**")
        show_RU_temps(df_heat_exchanger)

    with c2:
        st.subheader("Comparaison températures réseau urbain - échangeurs")
        st.markdown("")
        compare_temp_RU(df_heat_exchanger)
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("Pompes côté réseau urbain")
        show_RU_pumps(df_heat_exchanger, type = 'RU')
    with c2:
        st.subheader("Pompes côté échangeurs ")
        show_RU_pumps(df_heat_exchanger, type = 'HX')
    st.subheader("Production des cogénérations")
    show_production(df_cogen)   
    st.subheader("Consommation des échangeurs")
    show_consumption(df_cogen)
    st.subheader("Consommation relative des échangeurs")
    show_relative_production(df_cogen)
    st.subheader("Comparaison consommation réseau / digesteur & sécheur")
    compare_production(df_cogen)