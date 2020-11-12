import streamlit as st
import pandas as pd
from links import *
import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
import time

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

@st.cache(suppress_st_warning=True) 
def prepare_data(df):
	games_played = df[df['Score'].notnull()]
	games_played = games_played[['Date', 'Home', 'Score', 'Away']]
	games_played['Home_Score'] = games_played['Score'].apply(lambda x: x.split('–')[0])
	games_played['Away_Score'] = games_played['Score'].apply(lambda x: x.split('–')[-1])
	df_games = games_played.drop('Score', axis = 1).reset_index()
	games = df_games[['Date', 'Home', 'Home_Score', 'Away_Score', 'Away']]
	return games

@st.cache(suppress_st_warning=True) 
def get_match_report(link, game):
	home, away = game.split(' - ')
	st.write(f"{home} vs {away}")
	page = requests.get(link)
	st.write(f"Searching for data..")
	html = BeautifulSoup(page.content, "html.parser", parse_only=SoupStrainer('td', {'data-stat':'match_report'}))
	print(f"len:{len(html)}")
	for game in html:
		print(game.get('href'))
	st.write(f"Still searching for data..")
	all_td = 'all_td' #html.find_all('a', {'href':re.compile('/matches/')})
	#game_link = html.find_all('a', {'href':re.compile(f"/{home}")})
	return all_td


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
filter_team = st.sidebar.checkbox('Filter by team?')

if filter_team:
	team = st.sidebar.selectbox('Team', teams_names, key='teams')

st.markdown(f'Getting data for **{country} - {league} - {team}**')

data = get_games(league_games_link)
data_pretty = prepare_data(data)

if filter_team:
	data_pretty = data_pretty[(data_pretty['Home']==team)|(data_pretty['Away']==team)]

st.dataframe(data_pretty)

c1, c2 = st.sidebar.beta_columns(2)
most_recent = c1.checkbox('Most recent first')
alpha_order = c2.checkbox('Alphabetics order')

data_pretty = data_pretty.sort_values(by='Date', ascending=most_recent)

available_games = [f"{x['Home']} - {x['Away']}" for _, x in data_pretty.iterrows()]
if alpha_order:
	available_games.sort()

game = st.sidebar.selectbox('Game', available_games)

st.markdown(f'Selected game  : **{game}**')

get_data = st.sidebar.button('Generate game report')

if get_data:
	link_to_game = get_match_report(league_games_link, game)
	print(link_to_game)
	st.write(link_to_game)
st.write('Done')


