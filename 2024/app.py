from flask import Flask, render_template, redirect, url_for
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import subprocess

app = Flask(__name__)

# Função para normalizar as previsões
def normalize_predictions(predictions):
    return predictions / predictions.sum(axis=1, keepdims=True)

# Função para normalizar uma linha
def normalize_row(row):
    return row / row.sum()

@app.route('/')
def previsao_votos():
    # Carregar as tabelas de votos (dados incompletos) e eleitores
    tabela_votos = pd.read_csv("2024/2024_votos.csv")
    tabela_eleitores = pd.read_csv("2024/2020_eleitores_filiados.csv", delimiter=';')

    # Ajustar os nomes das colunas que foram carregadas incorretamente
    tabela_eleitores.rename(columns={
        'G�nero': 'Genero',
        'Grau de escolaridade': 'Escolaridade',
        'Faixa et�ria': 'Idade'
    }, inplace=True)

    # Extrair o nome dos partidos e a coluna 'Zona' dinamicamente da tabela de votos
    colunas_votos = tabela_votos.columns
    partidos = colunas_votos.drop('Zona')  # Exclui a coluna 'Zona', deixando apenas os partidos

    # Unir as duas tabelas usando a coluna 'Zona' como identificador
    df = pd.merge(tabela_eleitores, tabela_votos, on='Zona', how='inner')

    # Inputs: Apenas sexo, escolaridade, idade, partido
    X_full = df[['Zona', 'Genero', 'Escolaridade', 'Idade', 'Partido']]

    # Outputs: Distribuição de votos nos partidos (com base nos dados reais apurados)
    y_full = df[['Zona'] + list(partidos)]

    # Normalizar os dados de votos apurados por zona
    y_full_normalized = y_full.groupby('Zona').apply(lambda x: normalize_row(x.drop(columns='Zona').sum())).reset_index()

    # Agrupar os eleitores por zona para corresponder ao número de zonas
    X_full_grouped = X_full.groupby('Zona').first().reset_index()  # Agrupa por zona, pegando a primeira entrada de cada grupo

    # Transformar as variáveis categóricas em variáveis numéricas usando one-hot encoding
    X_full_dummies = pd.get_dummies(X_full_grouped.drop(columns='Zona'), drop_first=True)

    # Filtrar as zonas com votos apurados (incompletos)
    zonas_apuradas = y_full_normalized.index[y_full_normalized.drop(columns='Zona').sum(axis=1) > 0]

    # Filtrar os dados das zonas apuradas em X e y
    X_train = X_full_dummies.loc[zonas_apuradas]
    y_train = y_full_normalized.loc[zonas_apuradas].drop(columns='Zona')

    # Treinar o modelo de regressão linear com base nos dados disponíveis
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Prever a distribuição de votos para todas as zonas, incluindo aquelas que não têm todos os votos apurados
    y_pred = model.predict(X_full_dummies)  # Previsão para toda a cidade

    # Normalizar as previsões
    y_pred_normalized = normalize_predictions(y_pred)

    # Calcular a porcentagem de votos previstos por partido para toda a cidade
    porcentagem_votos_previstos = (y_pred_normalized.mean(axis=0) * 100).round(2)

    # Determinar o partido vencedor
    partido_vencedor = partidos[np.argmax(porcentagem_votos_previstos)]

    # Analisar a tendência de grupos específicos (homens, mulheres, jovens, etc.)
    coeficientes = pd.DataFrame(model.coef_, columns=X_full_dummies.columns)

    tendencias = []
    for grupo in X_full_dummies.columns:
        tendencia_partido = coeficientes.loc[:, grupo].idxmax()  # Partido mais favorecido por este grupo
        coef_maior = coeficientes.loc[:, grupo].max()  # Coeficiente máximo para o partido mais favorecido
        coef_menor = coeficientes.loc[:, grupo].min()  # Coeficiente mínimo (partido menos favorecido)
        
        if coef_maior > 0:
            tendencias.append(f"Ser {grupo} aumenta as chances de votar principalmente no partido {partidos[tendencia_partido]} em {(coef_maior* 100).round(2)}%.")
        if coef_menor < 0:
            partido_menos_fav = coeficientes.loc[:, grupo].idxmin()
            tendencias.append(f"Ser {grupo} diminui as chances de votar no partido {partidos[partido_menos_fav]} em {(coef_menor* 100).round(2)}%.")

    # Renderizar o template com as previsões e tendências
    return render_template('resultado.html', partidos=partidos, porcentagem_votos_previstos=porcentagem_votos_previstos,
                           partido_vencedor=partido_vencedor, tendencias=tendencias, zip=zip)

@app.route('/recarregar')
def recarregar_dados():
    # Executar o script scrappler.py para atualizar os dados
    subprocess.run(["python", "2024/scrappler.py"], check=True)
    # Após a execução do script, redirecionar de volta à página principal
    return redirect(url_for('previsao_votos'))

if __name__ == '__main__':
    app.run(debug=True)
