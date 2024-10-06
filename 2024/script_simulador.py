import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Função para normalizar as previsões
def normalize_predictions(predictions):
    return predictions / predictions.sum(axis=1, keepdims=True)

# Função para normalizar uma linha
def normalize_row(row):
    return row / row.sum()

# Função para sortear votos de forma aleatória, respeitando a distribuição
def sortear_votos_aleatorios(votos_df, porcentagem):
    """Sorteia uma porcentagem dos votos de forma aleatória."""
    votos_sorteados = votos_df.apply(lambda x: np.random.binomial(x, porcentagem))
    return votos_sorteados

# Carregar as tabelas
tabela_votos = pd.read_csv("2024/2020_votos.csv")
# para obter essa tabela, utilize o scrappler.py com o codigo da sua mu (municipio) e o cargo em questao, além de trocar a uf,
# https://resultados.tse.jus.br/oficial/app/index.html#/divulga/votacao-nominal;e=619;cargo=11;uf=rs;mu=88013;zona=1
# portu alegre é mu = 88013
tabela_eleitores = pd.read_csv("2024/2020_eleitores_filiados.csv", delimiter=';')
#https://sig.tse.jus.br/ords/dwapr/r/seai/sig-eleicao-filiados/
#obtenha os dados da sua eleição apartiro do tse no link acima
# Ajustar os nomes das colunas que foram carregadas incorretamente
tabela_eleitores.rename(columns={
    'G�nero': 'Genero',
    'Grau de escolaridade': 'Escolaridade',
    'Faixa et�ria': 'Idade'
}, inplace=True)

# Unir as duas tabelas usando a coluna 'Zona' como identificador
df = pd.merge(tabela_eleitores, tabela_votos, on='Zona', how='inner')

# Inputs: Apenas sexo, escolaridade, idade, partido (ignorando 'local_votacao' e 'zona' para treino)
X_full = df[['Zona', 'Genero', 'Escolaridade', 'Idade', 'Partido']]

# Outputs: Distribuição de votos nos partidos
y_full = df[['Zona', 'psol', 'pp', 'rep', 'pdt', 'pstu', 'pco', 'pcdob', 'pv', 'psdb', 'pros', 'mdb', 'psd']]

# Aplicar a normalização no y_full por zona
y_full_normalized = y_full.groupby('Zona').apply(lambda x: normalize_row(x.drop(columns='Zona').sum())).reset_index()

# Agrupar os eleitores por zona para corresponder ao número de zonas
X_full_grouped = X_full.groupby('Zona').first().reset_index()  # Agrupa por zona, pegando a primeira entrada de cada grupo

# Transformar as variáveis categóricas em variáveis numéricas usando one-hot encoding
X_full_dummies = pd.get_dummies(X_full_grouped.drop(columns='Zona'), drop_first=True)

# Simular a apuração parcial sorteando uma porcentagem aleatória dos votos
porcentagem_apurada = 0.10  # Exemplo: 25% dos votos apurados
y_apurado = sortear_votos_aleatorios(tabela_votos[['psol', 'pp', 'rep', 'pdt', 'pstu', 'pco', 'pcdob', 'pv', 'psdb', 'pros', 'mdb', 'psd']], porcentagem_apurada)

# Zonas com votos sorteados
zonas_apuradas = y_apurado.index[y_apurado.sum(axis=1) > 0]  # Pegamos as zonas que realmente tiveram votos sorteados

# Filtrar as zonas apuradas em X e y
X_train = X_full_dummies.loc[zonas_apuradas]
y_train = y_apurado.loc[zonas_apuradas]

# Verificar a correspondência entre X_train e y_train
print(f"Tamanho de X_train (zonas apuradas): {len(X_train)}")
print(f"Tamanho de y_train (zonas apuradas): {len(y_train)}")

# Normalizar a distribuição dos votos sorteados (apurados) por zona
y_train_normalizado = y_train.apply(normalize_row, axis=1)

# Criar o modelo baseado apenas nas zonas parcialmente apuradas
model = LinearRegression()
model.fit(X_train, y_train_normalizado)

# Prever a distribuição de votos para toda a cidade (incluindo zonas não apuradas)
y_pred = model.predict(X_full_dummies)  # Previsão para toda a cidade

# Normalizar as previsões
y_pred_normalized = normalize_predictions(y_pred)

# Calcular o erro comparando com a tabela completa original (tabela de 2020)
mse_total = mean_squared_error(y_full_normalized.drop(columns='Zona') * 100, y_pred_normalized * 100)

# Exibir os resultados
print(f"Erro Quadrático Médio para a cidade toda com {porcentagem_apurada * 100}% de apuração: {mse_total:.5f}")

# Exibir algumas das previsões e resultados reais para verificação
print("\nPrevisões (normalizadas) para as primeiras 5 zonas:")
print(pd.DataFrame(y_pred_normalized, columns=['psol', 'pp', 'rep', 'pdt', 'pstu', 'pco', 'pcdob', 'pv', 'psdb', 'pros', 'mdb', 'psd']).head())

print("\nResultados reais (normalizados) para as primeiras 5 zonas:")
print(y_full_normalized.head())
