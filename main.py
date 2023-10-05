from controllers.global_controller import GlobalController
import pandas as pd
from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
import json
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
import datetime
import pandas as pd
from raceplotly.plots import barplot
import plotly.graph_objects as go
import plotly
from random import sample
import random

app = Flask(__name__)
app.secret_key = 'mIlTkQ6kFlKVJ1ANl3vR7jSioF6PVhTv'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitch'

mysql = MySQL(app)
matplotlib.use('Agg')

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/global', methods=['GET'])
def global_vue():
    global_controller = GlobalController()
    return global_controller.index(mysql)

@app.route('/toggle_graph', methods=['POST'])
def toggle_graph():
    global_controller = GlobalController()
    return global_controller.toggle_graph()

@app.template_filter('format')
def format_number(value):
    return '{:,}'.format(value)

@app.route('/jeu')
def allGames():
    cursor = mysql.connection.cursor()
    
    query = "SELECT game, sum(hours_watched) as sumHours FROM `game_data` group by game ORDER BY `sumHours` DESC"
    cursor.execute(query)
    
    data_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    
    cursor.close()
    
    data_dict = data_df.to_dict(orient='records')
    
    return render_template('listJeu.html', table=data_dict)
    
@app.route('/jeu/<jeu>', methods=['GET', 'POST'])
def jeu_vue(jeu):
    cursor = mysql.connection.cursor()

    selected_year = request.form.get('year')
    chart_image_annee_default = None

    if selected_year is None:
        selected_year = '2023'
        chart_image_annee_default = generate_default_chart(jeu, selected_year)

    data_json2 = None 
    dataFrameAnnee = pd.DataFrame()

    if request.method == 'POST':
        selected_year = request.form.get('year')
        if selected_year:
            query = "SELECT * FROM game_data WHERE game=%s AND year=%s"
            cursor.execute(query, (jeu, selected_year))
            dataFrameAnnee = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            month_mapping = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Jun',
                            7: 'Jul', 8: 'Aou', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            dataFrameAnnee['month'] = dataFrameAnnee['month'].replace(month_mapping)

            months_order = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']
            dataFrameAnnee['month'] = pd.Categorical(dataFrameAnnee['month'], categories=months_order, ordered=True)

            data_json2 = json.dumps(dataFrameAnnee.to_dict(orient='records'))

    query = "SELECT DISTINCT year FROM game_data WHERE game=%s" 
    cursor.execute(query, (jeu,)) 
    years = [row[0] for row in cursor.fetchall()]

    query = "SELECT * FROM game_data WHERE game=%s"
    cursor.execute(query, (jeu,))
    data_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    query = "SELECT game, MAX(peak_viewers) as peak_viewer, year FROM game_data WHERE game =%s GROUP BY year ORDER BY year ASC;"
    cursor.execute(query, (jeu,))
    data_df_peak_viewer = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    data_json3 = json.dumps(data_df_peak_viewer.to_dict(orient='records'))
    table_data = json.loads(data_json3)

    query ="SELECT game, sum(hours_streamed) as hours_streamed FROM `game_data` where game =%s ORDER BY `game_data`.`game` DESC"
    cursor.execute(query, (jeu,))
    hour_streamed = cursor.fetchall()

    query ="SELECT game, sum(hours_watched), year FROM `game_data` where game =%s group by year ORDER BY `game_data`.`game` DESC"
    cursor.execute(query, (jeu,))
    hours_watched = cursor.fetchall()
    
    cursor.close()

    myDatetime = datetime.datetime.now()
    current_year = myDatetime.year

    avg_viewers_by_year = data_df.groupby('year')['avg_viewers'].mean()
    avg_viewers_by_year.plot(kind='bar')
    ax = avg_viewers_by_year.plot(kind='bar') 

    ax.grid(True, linestyle='-', linewidth=0.5, color='lightgrey') 
    ax.set_axisbelow(True)
    
    plt.xlabel('Année') 
    plt.xticks(rotation=0)
    plt.ylabel('Nombre moyen de spectateurs')
    plt.title('Nombre moyen de spectateurs par année')

    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format='png')
    image_buffer.seek(0)

    chart_image = base64.b64encode(image_buffer.read()).decode('utf-8')

    chart_image_annee = None
    if not dataFrameAnnee.empty:
        avg_viewers_by_month = dataFrameAnnee.groupby('month')['avg_viewers'].mean().sort_index()
        ax = avg_viewers_by_month.plot(kind='bar')

        plt.xlabel('Mois')
        plt.xticks(rotation=0)
        ax.grid(True, linestyle='-', linewidth=0.5, color='lightgrey') 
        ax.set_axisbelow(True)

        plt.ylabel('Nombre moyen de spectateurs')
        plt.title("Nombre moyen de spectateurs par mois pour l'année " + selected_year)

        image_buffer = io.BytesIO()
        plt.savefig(image_buffer, format='png')
        image_buffer.seek(0)
        chart_image_annee = base64.b64encode(image_buffer.read()).decode('utf-8')
        plt.clf()

    return render_template('jeu.html', hours_watched = hours_watched, hours_streamed= hour_streamed, table = table_data, viewers_month_chart = chart_image_annee, chart_image_by_year=chart_image, years=years, dataAnnee = data_json2, annee = selected_year, current_year = current_year, jeu = jeu, chart_image_annee_default = chart_image_annee_default)
  
def generate_default_chart(jeu, selected_year):
    cursor = mysql.connection.cursor()

    query = "SELECT * FROM game_data WHERE game=%s AND year=%s"
    cursor.execute(query, (jeu, selected_year))
    dataFrameAnnee = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    month_mapping = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Jun',
                    7: 'Jul', 8: 'Aou', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    dataFrameAnnee['month'] = dataFrameAnnee['month'].replace(month_mapping)

    months_order = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']
    dataFrameAnnee['month'] = pd.Categorical(dataFrameAnnee['month'], categories=months_order, ordered=True)

    # Générer le graphique pour l'année sélectionnée
    avg_viewers_by_month = dataFrameAnnee.groupby('month')['avg_viewers'].mean().sort_index()
    ax = avg_viewers_by_month.plot(kind='bar')

    plt.xlabel('Mois')
    plt.xticks(rotation=0)
    ax.grid(True, linestyle='-', linewidth=0.5, color='lightgrey') 
    ax.set_axisbelow(True)

    plt.ylabel('Nombre moyen de spectateurs')
    plt.title("Nombre moyen de spectateurs par mois pour l'année " + selected_year)

    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format='png')
    image_buffer.seek(0)
    chart_image_annee = base64.b64encode(image_buffer.read()).decode('utf-8')
    plt.clf()

    cursor.close()

    return chart_image_annee

@app.route('/timeline/', methods=['GET'])
def timeline():
    chartYear = timeline_year()
    chartMonth = timeline_month()

    return render_template('timeline.html', chartYear=chartYear, chartMonth=chartMonth)

def timeline_year():
    cursor = mysql.connection.cursor()

    query = """
    SELECT
        year,
        game,
        game_data.rank game_rank,
        SUM(hours_watched) AS hours_watched,
        SUM(hours_streamed) AS hours_streamed,
        MAX(peak_viewers) AS peak_viewers
    FROM
        game_data
    WHERE
        game_data.rank <= 10
    GROUP BY
        year, game
    ORDER BY
        year ASC, game_data.rank ASC;
    """

    cursor.execute(query)
    top_games = cursor.fetchall()

    data_df = pd.DataFrame(top_games, columns=[desc[0] for desc in cursor.description])
    
    my_raceplot = barplot(data_df, item_column="game", value_column="peak_viewers", time_column="year")
    my_raceplot.plot(title = 'Top 10 best game from 2015 to 2023', item_label = 'Top 10 jeux', value_label = 'Peek de viewers', frame_duration = 800)

    fig = {
        "data": [],
        "layout": {},
        "frames": []
    }
    
    unique_games = data_df['game'].unique()
    game_colors = {game: 'rgb({}, {}, {})'.format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for game in unique_games}
    data_df['color'] = data_df['game'].map(game_colors)

    frame1 = data_df[data_df['year'] == data_df['year'].min()]

    top_entries = 10
    frame1 = frame1.iloc[:top_entries, :]
    frame1 = frame1.sort_values('hours_watched', ascending = True).iloc[:top_entries, :]
    fig['data'] = go.Bar(
        x = frame1['hours_watched'],
        y = frame1['game'],
        marker_color = frame1['color'],
        hoverinfo = 'all',
        textposition = 'outside',
        # texttemplate = '%{y}',
        texttemplate = '%{y}<br>%{x:.4s}',
        orientation = 'h',
        textfont = {'size': 20}
    )

    fig['layout'] = go.Layout(
        font = {'size' : 14},
        plot_bgcolor = 'white',
        xaxis = {
            'showline': True,
            'visible': True,
            'range': (0, data_df['hours_watched'].max() + data_df['hours_watched'].max()/10),
            'title_text': 'Heures visionnées' # title of the x axis,
        },
        yaxis = {
            'showline': False, 
            'visible': True, # to show the title
            'showticklabels': False, # to avoid displaying the names
            'title_text': 'Top 10 des jeux'
        }, # title of the y axis
        bargap = 0.15, # number btwn 0 and 1, sets gap between adjacent bars (as plot fraction)
        title = 'Jeux les plus regardés par année', # sets title for default plot
        height = 650
    )

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Année :",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 1500, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    fig["layout"]["updatemenus"] = [
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 2500, "redraw": False}, "fromcurrent": True, "transition": {"duration": 1500, "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}], "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left", 
        "pad": {"r": 10, "t": 87},
        "showactive": True, 
        "type": "buttons",
        "x": 0.1,
        "y": 0
    }
    ]

    for year in range(data_df['year'].min(), data_df['year'].max()+1):
        snap_data = data_df[data_df['year'] == year]
        snap_data = snap_data.iloc[:top_entries,:]
        snap_data = snap_data.sort_values('hours_watched', ascending=True).iloc[:top_entries,:]

        frame = go.Frame(
            data=[
                go.Bar(
                    x=snap_data['hours_watched'],
                    y=snap_data['game'],
                    marker_color=snap_data['color'],
                    hoverinfo='all',
                    textposition='outside',
                    # texttemplate= '%{y}',
                    texttemplate= '%{y}<br>%{x:.4s}',
                    orientation = 'h'
                )
            ],
            layout=go.Layout(
                font={'size': 14},
                plot_bgcolor = 'white',
                xaxis={
                    'showline': True,
                    'visible': True,
                    'range': (0, data_df['hours_watched'].max() + data_df['hours_watched'].max()/10),
                },
                yaxis={
                    'showline': False,
                    'visible': False
                },
                bargap= 0.15,
                title= 'Top 10 Crops across time'
            ),
            name = year
        )
        fig['frames'].append(frame)

        slider_step = {"args": [
            [year],
            {"frame": {"duration": 300, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 300}}
        ],
        "label": year,
        "method": "animate"}
        sliders_dict["steps"].append(slider_step)

        fig['layout']['sliders'] = [sliders_dict]

    figSchema = go.Figure(fig)
    figChart64 = json.dumps(figSchema, cls=plotly.utils.PlotlyJSONEncoder)

    # return render_template('timeline.html', fig=figChart64)
    return figChart64

def timeline_month():
    cursor = mysql.connection.cursor()

    query = """
    SELECT
        CONCAT(month, '-', year) as month_year,
        game,
        ROW_NUMBER() OVER (PARTITION BY year, month ORDER BY hours_watched DESC) AS game_rank,
        hours_watched,
        hours_streamed,
        peak_viewers
    FROM
        game_data
    WHERE
        game_data.rank <= 10
    ORDER BY
        year ASC,
        month ASC,
        game_data.rank ASC;
    """

    cursor.execute(query)
    top_games = cursor.fetchall()
    month_list = {1:'Janvier', 2:'Février', 3:'Mars', 4:'Avril', 5:'Mai', 6:'Juin', 7:'Juillet', 8:'Août', 9:'Septembre', 10:'Octobre', 11:'Novembre', 12:'Décembre'}

    data_df = pd.DataFrame(top_games, columns=[desc[0] for desc in cursor.description])
    
    my_raceplot = barplot(data_df, item_column="game", value_column="peak_viewers", time_column="month_year")
    my_raceplot.plot(title = 'Top 10 best game from 2015 to 2023', item_label = 'Top 10 jeux', value_label = 'Peek de viewers', frame_duration = 800)

    fig = {
        "data": [],
        "layout": {},
        "frames": []
    }
    
    unique_games = data_df['game'].unique()
    game_colors = {game: 'rgb({}, {}, {})'.format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for game in unique_games}
    data_df['color'] = data_df['game'].map(game_colors)

    frame1 = data_df[data_df['month_year'] == data_df['month_year'].min()]

    top_entries = 10
    frame1 = frame1.iloc[:top_entries, :]
    frame1 = frame1.sort_values('game_rank', ascending = False).iloc[:top_entries, :]

    fig['data'] = go.Bar(
        x = frame1['hours_watched'],
        y = frame1['game'],
        marker_color = frame1['color'],
        hoverinfo = 'all',
        textposition = 'outside',
        texttemplate = '%{y}<br>%{x:.4s}',
        orientation = 'h',
        textfont = {'size': 20}
    )

    fig['layout'] = go.Layout(
        font = {'size' : 14},
        plot_bgcolor = 'white',
        xaxis = {
            'showline': True,
            'visible': True,
            'range': (0, data_df['hours_watched'].max()),
            'title_text': 'Heures visionnées' # title of the x axis,
        },
        yaxis = {
            'showline': False, 
            'visible': True, # to show the title
            'showticklabels': False, # to avoid displaying the names
            'title_text': 'Top 10 des jeux'
        }, # title of the y axis
        bargap = 0.15, # number btwn 0 and 1, sets gap between adjacent bars (as plot fraction)
        title = 'Jeux les plus regardés par mois', # sets title for default plot
        height = 650
    )

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        # "currentvalue": {
        #     "font": {"size": 20},
        #     "prefix": "Mois : ",
        #     "visible": True,
        #     "xanchor": "right"
        # },
        "transition": {"duration": 1500, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    fig["layout"]["updatemenus"] = [
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 2500, "redraw": False}, "fromcurrent": True, "transition": {"duration": 1500, "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}], "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left", 
        "pad": {"r": 10, "t": 87},
        "showactive": True, 
        "type": "buttons",
        "x": 0.1,
        "y": 0
    }
    ]

    previousYear = 0
    for month_year in data_df['month_year'].unique():
        snap_data = data_df[data_df['month_year'] == month_year]
        snap_data = snap_data.iloc[:top_entries,:]
        snap_data = snap_data.sort_values('game_rank', ascending=False).iloc[:top_entries,:]

        month, year = month_year.split('-')
        month = int(month)
        year = int(year)

        frame = go.Frame(
            data=[
                go.Bar(
                    x=snap_data['hours_watched'],
                    y=snap_data['game'],
                    marker_color=snap_data['color'],
                    hoverinfo='all',
                    textposition='outside',
                    texttemplate='%{y}<br>%{x:.4s}',
                    orientation='h'
                )
            ],
            layout=go.Layout(
                font={'size': 14},
                plot_bgcolor='white',
                xaxis={
                    'showline': True,
                    'visible': True,
                    'range': (0, data_df['hours_watched'].max()),
                },
                yaxis={
                    'showline': False,
                    'visible': False
                },
                bargap=0.15,
                title='Top 10 Crops across time'
            ),
            name=month_year
        )
        fig['frames'].append(frame)

        if year != previousYear:
            label = year
            previousYear = year
        else:
            label = ''

        slider_step = {
            "args": [
                [month_year],
                {
                    "frame": {"duration": 300, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 300},
                },
            ],
            "label": label,
            "method": "animate",
            'value': "Test",
        }
        sliders_dict["steps"].append(slider_step)

        fig['layout']['sliders'] = [sliders_dict]


    figSchema = go.Figure(fig)
    figChart64 = json.dumps(figSchema, cls=plotly.utils.PlotlyJSONEncoder)

    # return render_template('timeline.html', fig=figChart64)
    return figChart64

if __name__ == '__main__':
    app.run(debug=True)
 