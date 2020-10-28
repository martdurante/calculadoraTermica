import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from collections import OrderedDict
import datetime
from urllib.request import Request, urlopen
import pandas as pd
from calendar import monthrange

def tempAcum (ESTACION,FECHA,ACUM,TBASE):
	date = datetime.datetime(int(FECHA.split('-')[0]),int(FECHA.split('-')[1]),int(FECHA.split('-')[2]))
	iteracion=1
	temperatura = pd.DataFrame(columns=['dia','mes','anio','max','min','tProm','tAcum'])
	sigue = True
	while sigue:
		mesLetra=date.strftime('%B')
		dia=int(date.strftime('%d'))
		mes=int(date.strftime('%m'))
		anio=int(date.strftime('%Y'))
		dias_en_mes=monthrange(anio, mes)[1]
		url = 'https://www.accuweather.com/es/uy/'+ESTACION+'/'+mesLetra+'-weather/'+ESTACION.split('/')[1]+'?year='+str(anio)
		req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
		response = urlopen(req, timeout=20).read()
		fecha = []
		maxi = []
		mini = []
		for i in list(range(1, 36)):
			fe = str(response).split('date">\\n\\t\\t\\t\\t\\t\\t')[i][0:3]
			ma = str(response).split('high  ">\\n\\t\\t\\t\\t\\t\\t')[i][0:3]
			mi = str(response).split('low">\\n\\t\\t\\t\\t\\t\\t')[i][0:3]
			fecha.append(int(''.join([n for n in fe if n.isdigit()])))
			maxi.append(float(''.join([n for n in ma if n.isdigit()])))
			mini.append(float(''.join([n for n in mi if n.isdigit()])))
		iniMes = fecha.index(1)
		finMes = max([i for i,x in enumerate(fecha) if x==dias_en_mes])
		addDiaIni = dia-1 if iteracion == 1 else 0
		temp=pd.DataFrame({'dia':fecha[iniMes+addDiaIni:finMes+1],'mes':mes,'anio':anio ,'max':maxi[iniMes+addDiaIni:finMes+1], 'min':mini[iniMes+addDiaIni:finMes+1]})
		temp['tProm'] = (temp['max']+temp['min'])/2-TBASE
		temp.tProm = temp.tProm.mask(temp.tProm.lt(0),0)
		temp['tAcum'] = temp['tProm'].cumsum()
		temperatura = pd.concat([temperatura,temp])
		temperatura['tAcum'] = temperatura['tProm'].cumsum()
		#temp
		iteracion +=1
		date = date+datetime.timedelta(days=dias_en_mes)
		if max(temperatura['tAcum'])>ACUM:
			sigue = False
	temperatura = temperatura[temperatura.tAcum<=min(temperatura[temperatura.tAcum>ACUM]['tAcum'])]
	tu = temperatura.iloc[::-1].reset_index()
	return 'El '+str(tu['anio'][0])+'-'+str(tu['mes'][0])+'-'+str(tu['dia'][0])+' se alcanzaran '+str(tu['tAcum'][0])+'ºCd ('+str(tu.shape[0])+' dias de acumulacion)'

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.I("Calculadora Termica"),
        html.Br(),
        dcc.Input(id="input1", type="text", placeholder="", value='tacuarembo/350800', debounce=True),
        dcc.Input(id="input2", type="text", placeholder="", value='2020-10-10', debounce=True),
        dcc.Input(id="input3", type="text", placeholder="", value='450', debounce=True),
        dcc.Input(id="input4", type="text", placeholder="", value='0', debounce=True),
        html.Div(id="Ofecha"),
        html.Div(id="Otacum")
    ]
)


@app.callback(
    Output("Ofecha", "children"),
    Output("Otacum", "children"),
    [Input("input1", "value"), Input("input2", "value"), Input("input3", "value"), Input("input4", "value")],
)
def update_output(input1, input2, input3, input4):
	return u'Estacion = {}, Fecha = {}, Cd a acumular = {}, Temp. Base = {}'.format(input1, input2, input3, input4), tempAcum(input1,input2,int(input3),int(input4))
	#return u'temperatura= tempAcum ({},{},400,0)'.format(input1, input2), tempAcum(input1,input2,400,0).iloc[::-1].reset_index()['tAcum'][0]


if __name__ == "__main__":
    app.run_server(debug=True)
