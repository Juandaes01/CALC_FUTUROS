import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import calculos_precios_futuros

HOY= datetime.now() 
# Leer el archivo CSV
df = pd.read_excel('Parametros.xlsx')
Dividendos=  pd.read_excel('Info dividendos.xlsx')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Calculadora Futuros'

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Calculadora de Precios de Futuros de Acciones en Colombia"), className="mb-4")
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Nemotécnico de la Acción"),
            dcc.Dropdown(
                id="nemotecnico",
                options=[{'label': row['nemotecnico'], 'value': row['nemotecnico']} for index, row in df.iterrows()],
                #value=df.iloc[0]['nemotecnico']
            )
        ], width=4),
        dbc.Col([
            dbc.Label("Precio Actual de la Acción (COP)"),
            dbc.Input(id="precio-actual", type="number")
        ], width=4),
        dbc.Col([
            dbc.Label("Tasa de Interés (%)"),
            dbc.Input(id="tasa-interes", type="number")
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id="resultado"), className="mt-4",style={'font-size':'30px'})
    ]),
    dbc.Row([
        dbc.Table(id='table',striped=True, bordered=True,hover=True)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafica-tendencias"), width=12)
    ])
])
 
@app.callback(
    [Output("resultado", "children"),
     Output("table", "children"),
     Output("grafica-tendencias", "figure")],
    [Input("nemotecnico", "value"),
     Input("precio-actual", "value"),
     Input("tasa-interes", "value")]
)
    
def calcular_futuro(nemotecnico, precio_actual, tasa_interes):
    if nemotecnico is None or precio_actual is None or tasa_interes is None:
        resultado_texto= "Por favor, ingrese todos los valores."
        dividend= pd.DataFrame({'Pagos':[0,0,0,0], 'fecha exdiv': [0,0,0,0], 'Fecha pago':[0,0,0,0]})
        fig=px.line(x=[0,0,0,0], y=[0,0,0,0], labels={'x': 'Fecha', 'y': 'Precio Futuro'}, title='Precios futuros')
        table=dbc.Table.from_dataframe(dividend,striped=True, bordered=True,hover=True,id='table')
        return resultado_texto,table, fig 

    # Obtener los datos del nemotécnico seleccionado
    df['nemotecnico']= df['nemotecnico'].str.strip()
    row = df.query(f"nemotecnico == '{nemotecnico}'").iloc[0]
    nombre_mar = row['Marzo']
    nombre_jun = row['Junio']
    nombre_sep = row['Septiembre']
    nombre_dic = row['Diciembre']
    Dividendos['Nemotecnico']= Dividendos['Nemotecnico'].str.strip()
    Divi=Dividendos.query(f"Nemotecnico == '{nemotecnico}'")
    nominales_dividendos = Divi['Pago de dividendo'].astype(float).tolist()
    Fechas_exdiv = []
    if len(Divi['Fecha Exdividendo']) <= 1:
        if Divi['Fecha Exdividendo'].iloc[0] == '-' or len(Divi['Fecha Exdividendo']) == 0:
            Fechas_exdiv.append('No tiene')
        else:
            Fechas_exdiv.append(f"{Divi['Fecha Exdividendo'].iloc[0]:%Y-%m-%d}")
    else:
        for d in range(len(Divi['Fecha Exdividendo'])):
            if Divi['Fecha Exdividendo'].iloc[d] == '-':
                Fechas_exdiv.append('No tiene')
            else:
                Fechas_exdiv.append(f"{Divi['Fecha Exdividendo'].iloc[d]:%Y-%m-%d}")

    Fechas_pagos = []
    if len(Divi['Fecha Pago']) <= 1:
        if Divi['Fecha Pago'].iloc[0] == '-' or len(Divi['Fecha Pago']) == 0:
            Fechas_pagos.append('No tiene')
        else:
            Fechas_pagos.append(f"{Divi['Fecha Pago'].iloc[0]:%Y-%m-%d}")
    else:
        for d in range(len(Divi['Fecha Pago'])):
            if Divi['Fecha Pago'].iloc[d] == '-':
                Fechas_pagos.append('No tiene')
            else:
                Fechas_pagos.append(f"{Divi['Fecha Pago'].iloc[d]:%Y-%m-%d}")

    dividend= pd.DataFrame({'Pagos':nominales_dividendos, 'fecha exdiv': Fechas_exdiv, 'Fecha pago':Fechas_pagos})
    
    
    futuroH= calculos_precios_futuros.precioFuturo(precio_actual, tasa_interes,str(row['H']), nominales_dividendos,Fechas_exdiv,Fechas_pagos)
    futuroM= calculos_precios_futuros.precioFuturo(precio_actual, tasa_interes,str(row['M']), nominales_dividendos,Fechas_exdiv,Fechas_pagos)
    futuroU= calculos_precios_futuros.precioFuturo(precio_actual, tasa_interes,str(row['U']), nominales_dividendos,Fechas_exdiv,Fechas_pagos)
    futuroZ= calculos_precios_futuros.precioFuturo(precio_actual, tasa_interes,str(row['Z']), nominales_dividendos,Fechas_exdiv,Fechas_pagos)

    # Crear datos para la gráfica de tendencias
    TEMP = [f'{HOY:%Y/%m/%d}',f'{row["H"]:%Y/%m/%d}',f'{row["M"]:%Y/%m/%d}',f'{row["U"]:%Y/%m/%d}',f'{row["Z"]:%Y/%m/%d}']
    TEMP_org=sorted([datetime.strptime(fecha,'%Y/%m/%d')for fecha in TEMP])
    ## Proyecto proyección del precio
    # tiempo=(max([datetime.strftime(fecha,'%Y-%m-%d') for  fecha in TEMP])-HOY).days
    # tiempos = np.linspace(1, tiempo,tiempo) 
    # fig = px.line(x=tiempos, y=precios_futuros, labels={'x': 'Tiempo (dias)', 'y': 'Precio proyectado (COP)'}, title='Proyección Precio Spot')
    
    precios_futuros = [precio_actual,futuroH,futuroM,futuroU,futuroZ]
    contratos_futuros= [nemotecnico,nombre_mar,nombre_jun,nombre_sep,nombre_dic]
    data= pd.DataFrame({'fecha':TEMP, 'precio':precios_futuros,'contrato':contratos_futuros})
    data['fecha']= pd.to_datetime(data['fecha'])
    data = data.sort_values(by='fecha')
    data.reset_index(drop=True,inplace=True)
    
    resultado_texto = html.Div([html.P([f"Dado precio spot de {data['contrato'][0]}: {data['precio'][0]:.2f} el dia {data['fecha'][0]:%Y/%m/%d}"]),
                                html.P([f"El precio futuro del ({data['contrato'][1]}) con vencimiento el {data['fecha'][1]:%Y/%m/%d} es: ", html.B(f"{data['precio'][1]:.2f} COP",style={'color':'darkgreen','font-size':'32px'})]),
                                html.P([f"El precio futuro del ({data['contrato'][2]}) con vencimiento el {data['fecha'][2]:%Y/%m/%d} es: ", html.B(f"{data['precio'][2]:.2f} COP",style={'color':'darkgreen','font-size':'32px'})]),
                                html.P([f"El precio futuro del ({data['contrato'][3]}) con vencimiento el {data['fecha'][3]:%Y/%m/%d} es: ", html.B(f"{data['precio'][3]:.2f} COP",style={'color':'darkgreen','font-size':'32px'})]),
                                html.P([f"El precio futuro del ({data['contrato'][4]}) con vencimiento el {data['fecha'][4]:%Y/%m/%d} es: ", html.B(f"{data['precio'][4]:.2f} COP",style={'color':'darkgreen','font-size':'32px'})]),
                                ])
    fig = px.line(x=data['fecha'], y= data['precio'], labels={'x': 'Fecha', 'y': 'Precio Futuro'}, title='Precios futuros')
    table=dbc.Table.from_dataframe(dividend,striped=True, bordered=True,hover=True,id='table')
    
    return resultado_texto,table, fig

if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port=8289,debug=True)
    
