"""
Dashboard en temps réel pour le monitoring réseau
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime, timedelta


class NetworkDashboard:
    """Dashboard pour la visualisation des données réseau"""
    
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Configurer la mise en page du dashboard"""
        self.app.layout = html.Div([
            html.H1("Tableau de Bord d Automatisation Réseau", 
                   style={'textAlign': 'center', 'color': '#2c3e50'}),
            
            dcc.Tabs([
                # Tab 1: Vue d'ensemble
                dcc.Tab(label='Vue d ensemble', children=[
                    html.Div([
                        dcc.Graph(id='device-status-chart'),
                        dcc.Interval(
                            id='interval-component',
                            interval=60*1000,  # 1 minute
                            n_intervals=0
                        )
                    ])
                ]),
                
                # Tab 2: Performance des interfaces
                dcc.Tab(label='Interfaces', children=[
                    html.Div([
                        dcc.Dropdown(id='device-selector', placeholder='Selectionnez un equipement'),
                        dcc.Graph(id='interface-traffic-chart')
                    ])
                ]),
                
                # Tab 3: Rapports
                dcc.Tab(label='Rapports', children=[
                    html.Div([
                        html.H3("Rapports Generes"),
                        html.Ul(id='reports-list')
                    ])
                ])
            ])
        ])
    
    def setup_callbacks(self):
        """Configurer les callbacks pour l'interactivité"""
        @self.app.callback(
            Output('device-status-chart', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_device_status(n):
            # Données simulées - à remplacer par des données réelles
            devices = ['Router1', 'Switch1', 'Firewall1', 'Router2']
            status = ['UP', 'UP', 'DOWN', 'UP']
            
            fig = px.bar(
                x=devices, 
                y=[1 if s == 'UP' else 0 for s in status],
                color=status,
                title="Statut des Equipements",
                labels={'x': 'Equipements', 'y': 'Statut'}
            )
            return fig
        
        @self.app.callback(
            Output('reports-list', 'children'),
            Input('interval-component', 'n_intervals')
        )
        def update_reports_list(n):
            reports_dir = 'reports'
            if not os.path.exists(reports_dir):
                return [html.Li("Aucun rapport disponible")]
            
            reports = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
            report_items = []
            
            for report in reports[-5:]:  # 5 derniers rapports
                report_path = os.path.join(reports_dir, report)
                report_time = datetime.fromtimestamp(os.path.getctime(report_path))
                report_items.append(
                    html.Li([
                        html.A(report, href=f"/assets/{report}"),
                        f" - Genere le {report_time.strftime('%Y-%m-%d %H:%M')}"
                    ])
                )
            
            return report_items
    
    def run(self, debug=True, port=8050):
        """Lancer le dashboard"""
        self.app.run_server(debug=debug, port=port)


if __name__ == "__main__":
    dashboard = NetworkDashboard()
    dashboard.run()