import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
import streamlit as st
 
with st.sidebar: 
    # Titulo
    st.write("# Opciones")
    # slider
    div = st.slider('Radio:', 1, 5, 3)
    st.write("Radio=", div)    

dataFrame = pd.read_csv("UNI_CORR_500_01.txt",delimiter="\t",skiprows=3)
dataFrame = dataFrame[["# PersID","Frame","X","Y"]]
filas = dataFrame.shape[0]
radio = div

def calcularDistancia (punto1,punto2):
    return ((punto1[0]-punto2[0])**2 + (punto1[1]-punto2[1])**2)**0.5

listaSK = []
for indice in range(filas):
    
    frame = int(dataFrame.loc[indice,["Frame"]])
    peaton = int(dataFrame.loc[indice,["# PersID"]])
    subDataFrame = dataFrame[dataFrame["Frame"]==frame]
    subDataFrame = subDataFrame.reset_index(drop=True)
    coordenadas = subDataFrame[["X","Y"]].values
    arbol = KDTree(coordenadas)

    peatonIndice = subDataFrame.index[subDataFrame["# PersID"] == peaton].tolist()
    peatonIndice = peatonIndice[0]
    queryPoint = coordenadas[peatonIndice]
    
    vecinosIndices = arbol.query_ball_point(queryPoint,radio) #búsqueda de vecinos
    vecinosIndices = [indices for indices in vecinosIndices if indices != peatonIndice]
    
    distanciaTotal = 0
    for vecinos in vecinosIndices:
        coordenadasVecinos = coordenadas[vecinos]
        distanciaTotal += calcularDistancia(queryPoint,coordenadasVecinos)
        
    if len(vecinosIndices)>0:  
        SK = distanciaTotal/len(vecinosIndices)
        listaSK.append(SK)
    else:
        listaSK.append(0)
        
dataFrame["SK"] = listaSK

tiempo = 1/25
dataFrame["Distancia"] = (dataFrame["X"].diff(periods=-1)**2 + dataFrame["Y"].diff(periods=-1)**2)**0.5 
dataFrame["Velocidad"] = dataFrame["Distancia"]/tiempo

filtro = dataFrame[dataFrame["Velocidad"]<10]
velocidadPromedio = filtro["Velocidad"].mean()
dataFrame.loc[dataFrame['Velocidad'] > 10, 'Velocidad'] = velocidadPromedio

filtro2 = dataFrame[dataFrame["SK"]>0]
SKPromedio = filtro2["SK"].mean()
dataFrame.loc[dataFrame['SK'] == 0, 'SK'] = SKPromedio

ultimo = dataFrame.index[-1] 
columna1 = "Distancia"
columna2 = "Velocidad"
dataFrame.loc[ultimo, columna1] = velocidadPromedio*tiempo
dataFrame.loc[ultimo, columna2] = velocidadPromedio

fig,ax = plt.subplots()
ax.scatter(dataFrame["SK"],dataFrame["Velocidad"],c="red")
ax.set_xlabel("Valor calculado de SK")
ax.set_ylabel("Velocidad del peatón (mts/seg)")
ax.set_title("Velocidad vs SK", loc = "center")
st.pyplot(fig)