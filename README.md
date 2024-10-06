
# Previsão de Votos - Projeto Flask com Estatística

Este projeto utiliza **Flask** para servir um modelo de **regressão linear** que faz previsões sobre a distribuição de votos em diferentes partidos políticos, com base em dados reais e incompletos de apurações eleitorais. O site exibe previsões de porcentagem de votos por partido, o partido vencedor projetado, e uma análise das tendências de voto entre grupos específicos (gênero, escolaridade, idade, etc.).

## Requisitos

- **Python 3.6+**
- **Bibliotecas Python**:
  - Flask
  - Pandas
  - NumPy
  - Scikit-learn
  - Selenium
  - Webdriver-manager

## Instalação

1. Clone o repositório para sua máquina local:

    ```bash
    git clone https://github.com/Martche02/TSE.git
    cd TSE
    ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):

    ```bash
    python -m venv venv
    source venv/bin/activate   # Para Linux/Mac
    venv\Scripts\activate      # Para Windows
    ```

3. Instale as dependências do projeto:

    ```bash
    pip install -r requirements.txt
    ```

## Obtenção dos Dados

O projeto requer dois conjuntos de dados:

1. **Tabela de Votos (`2024/2020_votos.csv`)**:
   - Utilize o arquivo `2024/scrappler.py` para extrair a tabela de votos diretamente do site oficial do TSE.
   - Para configurar o scraper, use o código da sua cidade (mu = município) e o código do cargo eleitoral.
   - Exemplo para Porto Alegre (mu = 88013):
     ```
     https://resultados.tse.jus.br/oficial/app/index.html#/divulga/votacao-nominal;e=619;cargo=11;uf=rs;mu=88013;zona=1
     ```

2. **Tabela de Eleitores (`2024/2020_eleitores_filiados.csv`)**:
   - Baixe os dados de eleitores a partir do site do TSE:
     ```
     https://sig.tse.jus.br/ords/dwapr/r/seai/sig-eleicao-filiados/
     ```
   - O arquivo deve estar no formato CSV e ser carregado corretamente no projeto.

## Configuração e Execução

1. **Rodar o site Flask**:
   O arquivo principal do projeto é o `2024/app.py`, que cria um servidor Flask e exibe as previsões via navegador.

    ```bash
    python app.py
    ```

2. **Acesse no navegador**:
   O servidor será iniciado localmente em `http://127.0.0.1:5000/`. Visite essa URL no navegador para visualizar as previsões de votos.

## Estrutura do Projeto

```
2024/
│
├── app.py                  # Arquivo principal com o Flask e lógica de previsão
├── script.py               # Arquivo com a lógica de previsão
├── script.r                # Arquivo com a lógica de previsão/emulação em r
├── scrappler.py            # Script para extrair os votos do site do TSE
├── templates/
│   └── resultado.html       # Template HTML para exibição dos resultados
├── static/
│   └── css/
│       └── style.css        # Arquivo de estilo (CSS) para o site
├── 2020_votos.csv       # Arquivo CSV com os votos (gerado pelo scraper)
└── 2020_eleitores_filiados.csv # Arquivo CSV com os dados dos eleitores
```

## Explicação do Modelo

Este projeto utiliza **regressão linear** (da biblioteca Scikit-learn) para modelar a distribuição de votos com base nos dados de eleitores e votos parciais:

- **Entrada**: Gênero, escolaridade, idade e partido dos eleitores.
- **Saída**: Distribuição de votos entre os partidos.
  
O modelo prevê a distribuição de votos em zonas eleitorais com base nos dados disponíveis, normalizando a previsão para garantir que ela reflita corretamente as porcentagens de voto por partido.

### Funcionalidades do Site:

- **Previsão de Votos**: Mostra a porcentagem prevista de votos para cada partido.
- **Partido Vencedor**: Exibe o partido que teria mais votos com base na previsão.
- **Tendências de Grupos**: Analisa como diferentes grupos (por exemplo, homens, mulheres, pessoas com ensino superior) afetam as chances de voto para diferentes partidos.

## Como Contribuir

1. Faça um fork do projeto.
2. Crie uma nova branch para suas modificações:
    ```bash
    git checkout -b minha-feature
    ```
3. Faça o commit de suas mudanças:
    ```bash
    git commit -m 'Adicionei uma nova funcionalidade'
    ```
4. Faça o push para o repositório:
    ```bash
    git push origin minha-feature
    ```
5. Crie um Pull Request no GitHub.

## Licença

Este projeto está licenciado sob os termos da **MIT License**. Consulte o arquivo `LICENSE` para mais informações.
