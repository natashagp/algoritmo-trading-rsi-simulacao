import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

pd.options.mode.chained_assignment = None

# Escolher o ativo
ativo = "PETR4.SA"

# Obter dados do Yahoo Finance
dados_ativo = yf.download(ativo)

# Calcular os retornos
dados_ativo['retornos'] = dados_ativo['Adj Close'].pct_change().dropna()

# Separar retornos negativos dos positivos
dados_ativo['retornos_positivos'] = dados_ativo['retornos'].apply(lambda x: x if x > 0 else 0)
dados_ativo['retornos_negativos'] = dados_ativo['retornos'].apply(lambda x: abs(x) if x < 0 else 0)

# Calcular média de retornos positivos e negativos (últimos 22 dias)
dados_ativo['media_retornos_positivos'] = dados_ativo['retornos_positivos'].rolling(window = 22).mean()
dados_ativo['media_retornos_negativos'] = dados_ativo['retornos_negativos'].rolling(window = 22).mean()
dados_ativo = dados_ativo.dropna()

# Calcular o RSI
dados_ativo['RSI'] = (100 - 100 / (1 + dados_ativo['media_retornos_positivos']/dados_ativo['media_retornos_negativos']))

# Sinais de compra ou venda
# Compramos quando o RSI for menor que 30
dados_ativo.loc[dados_ativo['RSI'] < 30, 'compra'] = 'sim'
dados_ativo.loc[dados_ativo['RSI'] > 30, 'compra'] = 'nao'

data_compra = []
data_venda = []

for i in range(len(dados_ativo)):

    if "sim" in dados_ativo['compra'].iloc[i]:

        data_compra.append(dados_ativo.iloc[i+1].name)

        for j in range(1, 11):

            # Vendemos quando o RSI for maior que 40
            if dados_ativo['RSI'].iloc[i+j] > 40:
                data_venda.append(dados_ativo.iloc[i+j+1].name)
                break

            # Ou vendermos quando estiver na posição a 10 dias
            elif j == 10:
                data_venda.append(dados_ativo.iloc[i+j+1].name)

# Calculando Lucros
lucros = dados_ativo.loc[data_venda]['Open'].values/dados_ativo.loc[data_compra]['Open'].values - 1

# Analisando Lucros
operacoes_vencedoras = len(lucros[lucros > 0])/len(lucros)
media_ganhos = np.mean(lucros[lucros > 0])
media_perdas = abs(np.mean(lucros[lucros < 0]))
expectativa_matematica_modelo = (operacoes_vencedoras * media_ganhos) - ((1 - operacoes_vencedoras) * media_perdas)
performance_acumulada = (np.cumprod(1 + lucros) - 1)
retorno_buy_and_hold = dados_ativo['Adj Close'].iloc[-1]/dados_ativo['Adj Close'].iloc[0] - 1

print(f"Operações vencedoras: {round(operacoes_vencedoras * 100, 2)}%")
print(f"Média de ganhos: {round(media_ganhos * 100, 2)}%")
print(f"Média de perdas: {round(media_perdas * 100, 2)}%")
print(f"Expectativa matemática do modelo: {round(expectativa_matematica_modelo * 100, 2)}%")
print(f"Performance acumulada: {round((performance_acumulada * 100)[-1], 2)}%")
print(f"Retorno Buy and Hold: {round(retorno_buy_and_hold * 100, 2)}%")

# Observando pontos de compra ao longo do tempo
plt.figure(figsize=(12,5))
plt.scatter(dados_ativo.loc[data_compra].index, dados_ativo.loc[data_compra]['Adj Close'], marker='^', c='g')
plt.plot(dados_ativo['Adj Close'], alpha = 0.7)
plt.show()
