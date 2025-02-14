import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np

def set_timestamp(df):
    df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['UTC Time'])
    df.set_index('timestamp', inplace=True)
    df.drop(columns=['Date', 'UTC Time','Record'], inplace=True)


def show_RU_temps(df):
    # Create line plot for Tc_ru and Tf_ru temperatures
    fig = px.line(df, x=df.index, y=['Tc_RU', 'Tf_RU'],    line_shape = 'spline'
    )

    # Update line colors
    fig.update_traces(line_color='orange', selector=dict(name='Tc_RU'))
    fig.update_traces(line_color='blue', selector=dict(name='Tf_RU'))

    # Add conditional coloring for Tc_ru > 74
    fig.add_scatter(
        x=df[df['Tc_RU'] >= 74].index,
        y=df[df['Tc_RU'] >= 74]['Tc_RU'],
        mode='markers',
        line_color='red',
        name='Tc_ru > 74°C',
        showlegend=False,
        line_shape = 'spline'
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        template='simple_white',
        xaxis_rangeslider_visible=True
    )
    num_upper_74 = len(df[df['Tc_RU'] > 74])
    num_total = len(df['Tc_RU'])

    fig_2 = px.line(df, x=df.index, y=['dT_RU'], line_shape = 'spline')
    fig_2.update_layout(
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        template='simple_white',
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Delta T  réseau urbain")
    st.plotly_chart(fig_2, use_container_width=True)
def show_RU_pumps(df,type = 'RU'):
    # Calculate pump percentages
    if type == 'RU':
        name_1 = 'Hz1_RU'
        name_2 = 'Hz2_RU'
    elif type == 'HX':
        name_1 = 'Hz_HX1_CIN'
        name_2 = 'Hz_HX2_CIN'
    
    df[f'{name_1}_pct'] = df[name_1] / 50 * 100
    df[f'{name_2}_pct'] = df[name_2] / 50 * 100
    
    fig = px.line(df, x=df.index, y=[f'{name_1}_pct', f'{name_2}_pct'], line_shape='spline')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Pump (%)',
        template='simple_white',
        yaxis=dict(range=[0, 110]))
    
    # Update legend names
    fig.data[0].name = 'Pump 1'
    fig.data[1].name = 'Pump 2'
    
    # Add threshold line at 95%
    fig.add_scatter(x=[df.index[0], df.index[-1]], y=[95, 95], mode='lines', line=dict(dash='dash', color='grey'), name='95% Threshold')
    
    st.plotly_chart(fig, use_container_width=True)

def compare_temp_RU(df):
    fig = px.line(df, x=df.index, y=['Tc_RU', 'Tc_HX1_RU','Tc_HX2_RU','Tf_RU','Tf_HX1_CIN','Tf_HX2_CIN'], line_shape = 'spline')
    
    # Update line colors and styles for Tc temperatures
    fig.data[0].line.color = 'red'  # Tc_RU
    fig.data[1].line.color = 'red'  # Tc_HX1_RU 
    fig.data[1].line.dash = 'dash'
    fig.data[2].line.color = 'red'  # Tc_HX2_RU
    fig.data[2].line.dash = 'dot'
    fig.data[3].line.color = 'blue'  # Tf_RU        
    fig.data[4].line.color = 'blue'  # Tf_HX1_CIN
    fig.data[4].line.dash = 'dash'
    fig.data[5].line.color = 'blue'  # Tf_HX2_CIN
    fig.data[5].line.dash = 'dot'

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        template='simple_white')
    st.plotly_chart(fig, use_container_width=True)

def show_production(df):
    fig = px.area(df, x=df.index, y=['JEN1_P', 'JEN2_P', 'LIEB_P'], line_shape = 'spline')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Power',
        template='simple_white')
    fig.update_traces(selector=dict(type='scatter'), line=dict(width=0))

    st.plotly_chart(fig, use_container_width=True)

def show_consumption(df):
    # Create stacked area plot for heat exchanger and other power values
    area_cols = ['HX1_P', 'HX2_P', 'Sech_P', 'Dig_P']

    # Create stacked area plot for heat exchangers
    fig = px.area(df, x=df.index, y=area_cols,
                labels={'value': 'Power', 'variable': 'System'},
                height=600,line_shape = 'spline')
    fig.update_traces(selector=dict(type='scatter'), line=dict(width=0))

    # Add total generator power as a line on top
    fig.add_scatter(x=df.index, y=df['Total_Gen_P'], 
                    name='Total Generator Power',
                    mode='lines',
                    line=dict(width=2, color = 'grey'), line_shape = 'spline')

    fig.update_layout(
        xaxis_title="Timestamp", 
        yaxis_title="Power",
        showlegend=True,
        template='simple_white'
    )
    st.plotly_chart(fig, use_container_width=True)


def show_relative_production(df):
    area_cols = ['HX1_P', 'HX2_P', 'Sech_P', 'Dig_P']
    total_gen_power = df['Total_Gen_P']
    df_pct = df.copy()
    for col in area_cols:
        df_pct[col] = df_pct[col] / total_gen_power * 100

    # Calculate loss column as difference from 100%
    df_pct['Loss'] = 100 - df_pct[area_cols].sum(axis=1)

    # Add loss column to plot columns
    plot_cols = area_cols + ['Loss']

    fig = px.area(df_pct, x=df_pct.index, y=plot_cols,
                labels={'value': '% of Generator Power', 'variable': 'System'},
                height=600, line_shape = 'spline')

    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Percent of Total Generator Power", 
        showlegend=True,
        template='simple_white'
    )
    fig.update_traces(line=dict(width=0))
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

def compare_production(df):
    df['Consommation réseau'] = df['HX1_P'] + df['HX2_P']
    df['Consommation sécheur + digesteur'] = df['Sech_P'] + df['Dig_P']
    fig = px.line(df, x=df.index, y=['Consommation réseau', 'Consommation sécheur + digesteur'], line_shape = 'spline')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Power',
        template='simple_white',
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig, use_container_width=True)