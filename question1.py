import pandas as pd
import dash
from dash import Dash, dcc, html
import plotly.express as px

# Import data
characters = pd.read_csv('data/characters.grivg.csv')
games = pd.read_csv('data/games.grivg.csv')
sexualization = pd.read_csv('data/sexualization.grivg.csv')
vgd = pd.read_csv('data/video_game_developers_worldwide2014_2021.csv')

# Format columns
games.columns = games.columns.str.lower().str.replace(" ", "_")
characters.columns = characters.columns.str.lower().str.replace(" ", "_")
sexualization.columns = sexualization.columns.str.lower().str.replace(" ", "_")
vgd.columns = vgd.columns.str.lower().str.replace(" ", "_")

# Merge dataframes
temp_games = games.rename(columns={'game_id': 'game'})
merged_data = pd.merge(characters, temp_games, on='game')
merged_data = pd.merge(merged_data, sexualization, on='id')
merged_data['release'] = pd.to_datetime(merged_data['release'], format='%b-%y')
merged_data['year'] = merged_data['release'].dt.year

# Number of female and male leads over time
female_leads = merged_data[(merged_data['gender'] == 'Female') & (merged_data['relevance'] == 'PA')]
female_leads_count = female_leads.groupby('year').size().reset_index(name='female_lead_count')

male_leads = merged_data[(merged_data['gender'] == 'Male') & (merged_data['relevance'] == 'PA')]
male_leads_count = male_leads.groupby('year').size().reset_index(name='male_lead_count')

lead_counts = pd.merge(female_leads_count, male_leads_count, on='year', how='outer').fillna(0)
lead_counts['female_lead_count'] = lead_counts['female_lead_count'].astype(int)
lead_counts['male_lead_count'] = lead_counts['male_lead_count'].astype(int)

# Create a complete range of years
min_year = lead_counts['year'].min()
max_year = lead_counts['year'].max()
all_years = pd.DataFrame({'year': range(min_year, max_year + 1)})
lead_counts = all_years.merge(lead_counts, on='year', how='left').fillna(0)

# Custom leads
custom_leads = merged_data[(merged_data['gender'] == 'Custom') & (merged_data['relevance'] == 'PA')]
custom_leads_count = custom_leads.groupby('year').size().reset_index(name='custom_lead_count')
lead_counts = pd.merge(lead_counts, custom_leads_count, on='year', how='outer').fillna(0)
lead_counts['custom_lead_count'] = lead_counts['custom_lead_count'].astype(int)

# Create the plot
fig = px.line(lead_counts, x='year', y=['female_lead_count', 'male_lead_count', 'custom_lead_count'], 
              labels={'year': 'Year', 'value': 'Count'}, 
              title='Number of Female, Male, and Custom Leads Over Time', 
              color_discrete_map={'female_lead_count': 'red', 'male_lead_count': 'blue', 'custom_lead_count': 'green'})

fig.update_layout(
    xaxis_title='Year',
    yaxis_title='Count',
    xaxis=dict(tickmode='linear', dtick=1),
    yaxis=dict(range=[0, max(lead_counts['female_lead_count'].max(), lead_counts['male_lead_count'].max(), lead_counts['custom_lead_count'].max()) + 1]),
    template='plotly_dark'
)

# Initialize Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Video Game Character Analysis"),
    dcc.Graph(figure=fig)
])

# Run the app
if __name__ == '__main__':
    app.run_server()
