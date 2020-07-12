import csv
import plotly.graph_objects as go

h=[]  # Hi
m = []  # Miss
r = []  # Requests

with open('output.csv') as f:
	d = csv.reader(f,delimiter=',')
	for i in d:
		h.append(i[0])
		m.append(i[1])
		r.append(i[-1])

fig = go.Figure() 
fig.add_trace(go.Scatter(x=r,y=h,mode='lines',name='HITS'))
fig.add_trace(go.Scatter(x=r,y=m,mode='lines',name='MISS')) 
fig.update_layout(title='Hit and Miss without coordinators',xaxis_title='Requests', )
fig.show()
