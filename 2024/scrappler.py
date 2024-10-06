from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import re
import time

# Configurações do WebDriver
options = Options()
options.add_argument('--headless')  # Modo headless (sem interface gráfica)
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('start-maximized')

# Usando o webdriver_manager para instalar e gerenciar o ChromeDriver
service = Service(ChromeDriverManager().install())

# Inicializar o WebDriver com o ChromeDriver gerenciado
driver = webdriver.Chrome(service=service, options=options)

# Carregar o arquivo eleitores_filiados e obter as zonas válidas
eleitores_filiados = pd.read_csv('2024/2024_eleitores_filiados.csv', delimiter=';', encoding='ISO-8859-1')
zonas_eleitorais = eleitores_filiados['Zona'].unique()  # Obter as zonas únicas

# Inicializar a lista para armazenar os dados
dados_votos = []

# Loop para iterar sobre cada zona eleitoral válida
for zona in zonas_eleitorais:
    try:
        # Construir a URL para a zona atual
        url = f"https://resultados.tse.jus.br/oficial/app/index.html#/divulga/votacao-nominal;e=619;cargo=11;uf=rs;mu=88013;zona={zona}"
        driver.get(url)

        # Esperar a página carregar completamente
        time.sleep(5)

        # Número de candidatos variável: tentar até dar erro
        candidato = 1
        while True:
            try:
                # XPath para o número de votos do candidato j
                votos_xpath = f'/html/body/app-root/ion-app/ion-router-outlet/ng-component/ion-content/ng-component/div/div/div[1]/app-lista-candidatos/virtual-scroller/div[2]/div[{candidato+1}]/div[3]/div'
                
                # XPath para o nome do partido do candidato j
                partido_xpath = f'/html/body/app-root/ion-app/ion-router-outlet/ng-component/ion-content/ng-component/div/div/div[1]/app-lista-candidatos/virtual-scroller/div[2]/div[{candidato+1}]/div[1]/div[2]'
                
                # Extração dos dados
                votos_raw = driver.find_element(By.XPATH, votos_xpath).text
                partido = driver.find_element(By.XPATH, partido_xpath).text
                
                # Limpar o número de votos e converter para inteiro
                votos = re.search(r'(\d+)', votos_raw).group(1)  # Extrair apenas o número de votos
                
                # Armazenar os dados na lista (zona, partido, votos)
                dados_votos.append([zona, partido, int(votos)])
                
                # Incrementar o número do candidato
                candidato += 1

            except Exception as e:
                # Se der erro (não há mais candidatos), sair do loop
                print(f"Erro ao capturar dados do candidato {candidato} na zona {zona}: {e}")
                break

    except Exception as e:
        print(f"Erro ao capturar dados da zona {zona}: {e}")

# Fechar o navegador
driver.quit()

# Transformar os dados em um DataFrame
df_votos = pd.DataFrame(dados_votos, columns=["Zona", "Partido", "Votos"])

# Criar uma tabela pivô com uma linha por zona e uma coluna por partido
tabela_pivot = df_votos.pivot_table(index="Zona", columns="Partido", values="Votos", fill_value=0)

# Ajustar os nomes das colunas para o formato desejado (sem "Partido_" no início)
tabela_pivot.columns.name = None  # Remove o nome das colunas gerado pela tabela pivô

# Exibir a tabela resultante
print(tabela_pivot)

# Salvar os dados no formato desejado
tabela_pivot.to_csv('2024/2024_votos.csv', index=True)

print("Scraping concluído e arquivo CSV criado no formato desejado.")
