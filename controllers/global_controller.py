from flask import render_template, request, redirect, url_for, session
from models.global_model import get_years, get_hrswatchd_graph, get_avgviewers_graph, get_records

class GlobalController:
    def __init__(self):
        self.graph_type = None
        
    def index(self, mysql):
        years = get_years(mysql)
        
        graph_type = session.get('graph_type', 'Heures Vues')
        switch_checked = graph_type != 'Heures Vues'
        if graph_type == 'Heures Vues':
            graph_url = get_hrswatchd_graph(mysql)
            switch_label = "Voir moyenne de viewers"
        else:
            graph_url = get_avgviewers_graph(mysql)
            switch_label = "Voir nombre d'heures vues"

        records = get_records(mysql)
        return render_template('global.html', years=years, graph_url=graph_url, switch_checked=switch_checked, switch_label=switch_label, records=records)
    
    def toggle_graph(self):
        graph_type = session.get('graph_type', 'Heures Vues')
        if graph_type == 'Heures Vues':
            session['graph_type'] = 'Moyenne des Viewers'
        else:
            session['graph_type'] = 'Heures Vues'
        return redirect(url_for('global_vue'))