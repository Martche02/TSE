# Instalar pacotes necessários, se ainda não estiverem instalados
# install.packages("dplyr")
# install.packages("glmnet")

library(dplyr)
library(glmnet)

# Função para normalizar as previsões
normalize_predictions <- function(predictions) {
  return(sweep(predictions, 1, rowSums(predictions), FUN = "/"))
}

# Função para normalizar uma linha
normalize_row <- function(row) {
  return(row / sum(row))
}

# Função para sortear votos de forma aleatória, respeitando a distribuição
sortear_votos_aleatorios <- function(votos_df, porcentagem) {
  votos_sorteados <- apply(votos_df, 2, function(x) rbinom(length(x), x, porcentagem))
  return(as.data.frame(votos_sorteados))
}

# Carregar os dados
tabela_votos <- read.csv("2024/2020_votos.csv")
tabela_eleitores <- read.csv("2024/2020_eleitores_filiados.csv", sep = ";")

# Ajustar nomes das colunas que foram carregadas incorretamente
names(tabela_eleitores)[names(tabela_eleitores) == "G�nero"] <- "Genero"
names(tabela_eleitores)[names(tabela_eleitores) == "Grau de escolaridade"] <- "Escolaridade"
names(tabela_eleitores)[names(tabela_eleitores) == "Faixa et�ria"] <- "Idade"

# Unir as duas tabelas usando a coluna 'Zona' como identificador
df <- merge(tabela_eleitores, tabela_votos, by = "Zona")

# Inputs: Apenas sexo, escolaridade, idade, partido (ignorando 'local_votacao' e 'zona' para treino)
X_full <- df %>% select(Zona, Genero, Escolaridade, Idade, Partido)

# Outputs: Distribuição de votos nos partidos
y_full <- df %>% select(Zona, psol, pp, rep, pdt, pstu, pco, pcdob, pv, psdb, pros, mdb, psd)

# Normalizar as distribuições de votos por zona
y_full_normalized <- y_full %>%
  group_by(Zona) %>%
  summarise(across(psol:psd, sum)) %>%
  mutate(across(psol:psd, normalize_row))

# Agrupar os eleitores por zona para corresponder ao número de zonas
X_full_grouped <- X_full %>%
  group_by(Zona) %>%
  summarise(across(everything(), first)) %>%
  ungroup()

# One-hot encoding para variáveis categóricas
X_full_dummies <- model.matrix(~ Genero + Escolaridade + Idade + Partido - 1, data = X_full_grouped)

# Simular a apuração parcial sorteando uma porcentagem aleatória dos votos
porcentagem_apurada <- 0.25  # Exemplo: 25% dos votos apurados
y_apurado <- sortear_votos_aleatorios(tabela_votos %>% select(psol, pp, rep, pdt, pstu, pco, pcdob, pv, psdb, pros, mdb, psd), porcentagem_apurada)

# Zonas com votos sorteados
zonas_apuradas <- which(rowSums(y_apurado) > 0)  # Pegamos as zonas que realmente tiveram votos sorteados

# Filtrar as zonas apuradas em X e y
X_train <- X_full_dummies[zonas_apuradas,]
y_train <- as.matrix(y_apurado[zonas_apuradas,])

# Verificar a correspondência entre X_train e y_train
cat("Tamanho de X_train (zonas apuradas):", nrow(X_train), "\n")
cat("Tamanho de y_train (zonas apuradas):", nrow(y_train), "\n")

# Normalizar a distribuição dos votos sorteados (apurados) por zona
y_train_normalizado <- apply(y_train, 1, normalize_row)

# Treinar o modelo de regressão linear usando glmnet
modelo <- cv.glmnet(X_train, t(y_train_normalizado), alpha = 0, family = "mgaussian")

# Prever a distribuição de votos para toda a cidade (incluindo zonas não apuradas)
y_pred <- predict(modelo, newx = X_full_dummies, s = "lambda.min")
y_pred <- do.call(cbind, y_pred)

# Normalizar as previsões
y_pred_normalized <- normalize_predictions(y_pred)

# Calcular o erro comparando com a tabela completa original (tabela de 2020)
mse_total <- mean(rowSums((y_full_normalized %>% select(-Zona) - y_pred_normalized)^2))

# Exibir os resultados
cat("Erro Quadrático Médio para a cidade toda com", porcentagem_apurada * 100, "% de apuração:", mse_total, "\n")

# Exibir algumas das previsões e resultados reais para verificação
cat("\nPrevisões (normalizadas) para as primeiras 5 zonas:\n")
print(head(as.data.frame(y_pred_normalized), 5))

cat("\nResultados reais (normalizados) para as primeiras 5 zonas:\n")
print(head(y_full_normalized, 5))
