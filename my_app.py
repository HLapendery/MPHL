import streamlit as st
import pandas as pd
from links import *
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import date

today = date.today()
hour = time.strftime("%d/%m/%Y - %H:%M")

@st.cache(show_spinner=False)
def get_teams_names(link):
	with st.spinner("Processing data..."):
		print(hour)
		print(f'Reaching {link}')
		results = pd.read_html(link)
		teams =  []
		for group in results[:-1]:
			for team in group['Squad'].values:
				if team not in teams:
					teams.append(team)
	return sorted(teams)

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_games(link):
	with st.spinner("Processing data..."):
		schedule = pd.read_html(link)[0]
	return schedule

@st.cache
def prepare_data(df):
	games_played = df[df['Score'].notnull()]
	games_played = games_played[['Date', 'Home', 'Score', 'Away']]
	games_played['Home'] = games_played['Home'].apply(lambda x: ' '.join(x.split(' ')[:-1]))
	games_played['Away'] = games_played['Away'].apply(lambda x: ' '.join(x.split(' ')[1:]))
	games_played['Home_Score'] = games_played['Score'].apply(lambda x: x.split('–')[0])
	games_played['Away_Score'] = games_played['Score'].apply(lambda x: x.split('–')[-1])
	df_games = games_played.drop('Score', axis = 1).reset_index()
	games = df_games[['Date', 'Home', 'Home_Score', 'Away_Score', 'Away']]
	return games

st.title('Welcome to our game analysis app')
st.sidebar.title('Choose your game')

country = st.sidebar.selectbox('Country',list(COMP.keys()), format_func= lambda x: x.upper())
league = st.sidebar.selectbox('Competition',list(COMP[country].keys()))
league_teams_link = COMP[country][league]['teams']
league_games_link = COMP[country][league]['games']
teams_names = get_teams_names(league_teams_link)
if country == 'Europe':
	teams_names = sorted(list(map(lambda x: ' '.join(x.split(' ')[1:]), teams_names)))

team = ''
filter = st.sidebar.checkbox('Filter by team?')
if filter:
	team = st.sidebar.selectbox('Team', teams_names, key='teams')

st.write(f'Getting data for {country} - {league} - {team}')

data = get_games(league_games_link)
data_pretty = prepare_data(data)

print(data_pretty)

if filter:
	data_pretty = data_pretty[(data_pretty['Home']==team)|(data_pretty['Away']==team)]

print(data_pretty)
sorting = st.beta_columns(2)
sort_variable = sorting[0].selectbox('Sort by:', list(data_pretty.columns))
sort_order = sorting[1].checkbox('Ascending order')

st.table(data_pretty.sort_values(by=sort_variable, ascending=sort_order))
st.write('Done')
