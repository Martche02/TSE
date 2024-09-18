from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from parsel import Selector
import re
driPath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('start-maximized')
options = Options()

def pegarElemento(xpath, fonte):
    return re.sub('[^0-9]', '', str(BeautifulSoup(Selector(fonte).xpath(xpath).getall()[0], 'html.parser').encode_contents()))

def lerSite(estado):
    link = "https://resultados.tse.jus.br/oficial/app/index.html#/m/eleicao-cargo/1;e=e545;uf="+estado+";ufbu="+estado
    print(link)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(link)
    time.sleep(3)
    # with open("teste.html", "w") as arquivo:
    #     arquivo.write(str(BeautifulSoup(driver.page_source)))
    votosLul = int(pegarElemento("/html/body/app-root/ion-app/ion-router-outlet/ng-component/div/div[2]/ng-component/ng-component/app-centralizar/div[2]/div[2]/div[1]/div/virtual-scroller/div[2]/ul/li[1]/app-linha-candidato/div/div/div/div[2]/div[1]/text()[2]", driver.page_source))
    votosBol = int(pegarElemento("/html/body/app-root/ion-app/ion-router-outlet/ng-component/div/div[2]/ng-component/ng-component/app-centralizar/div[2]/div[2]/div[1]/div/virtual-scroller/div[2]/ul/li[2]/app-linha-candidato/div/div/div/div[2]/div[1]/text()[2]", driver.page_source))
    porceTot = str(BeautifulSoup(Selector(driver.page_source).xpath("/html/body/app-root/ion-app/ion-router-outlet/ng-component/div/div[2]/ng-component/ng-component/app-centralizar/app-barra-acompanhamento/div/div[1]/div/text()").getall()[0], 'html.parser').encode_contents())
    porceTot = int(re.sub('[^0-9]', '', str(porceTot[:porceTot.find("%")])))/10000
    porceTot = porceTot+1 if porceTot == 0 else porceTot
    votosVal = pegarElemento("/html/body/app-root/ion-app/ion-router-outlet/ng-component/div/div[2]/ng-component/ng-component/app-centralizar/div[2]/div[2]/div[2]/section/div/app-legenda-votacao/ul/div[1]/h2/span", driver.page_source)
    votosVal = int(votosVal[(3-len(votosVal))::])/10000
    driver.quit()
    return [votosLul, votosBol, porceTot, votosVal]

votFutLul = []
votFutBol = []
votFutLulTot = 0
votFutBolTot = 0
estados = ["ac", "al", "ap", "am", "ba", "ce", "df", "es", "zz", "go", "ma", "mt", "ms", "mg", "pr", "pb", "pa", "pe", "pi", "rj", "rn", "rs", "ro", "rr", "sc", "se", "sp", "to"]
for estado in estados:
    try:
        x = lerSite(estado)
        votFutLul.append(x[0]/x[2])
        votFutBol.append(x[1]/x[2])
        votFutLulTot += votFutLul[-1]
        votFutBolTot += votFutBol[-1]
    except Exception:
        pass

VotosTotais = votFutLulTot+votFutBolTot
PorcentagemLula = votFutLulTot/VotosTotais*100
PorcentagemBolsonaro = votFutBolTot/VotosTotais*100
print(VotosTotais)
print(PorcentagemLula)
print(PorcentagemBolsonaro)
print('''Lula tem '''+str(PorcentagemLula)+'''%
Bolsonaro tem '''+str(PorcentagemBolsonaro)+'''%''')