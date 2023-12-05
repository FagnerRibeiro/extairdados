import json
import sys
import requests
from bs4 import BeautifulSoup

url_base = 'site.com'
url_pesquisa = f'{url_base}/solucao/cnpj'
headers = {'User-Agent': 'SeuAgenteDeUsuario'}
entrada = input("Entrada da pesquisa: ")
entradaUF = input("Estado em siglas: ")
entradaMunicipio = input("Municipio:  ")
payload = {'q':entrada, 'uf':entradaUF, municipio:entradaMunicipio }

def extrair_links_detalhes(url_pesquisa, headers, payload):
    try:
        requisicao = requests.get(url_pesquisa, headers=headers, params=payload)
        requisicao.raise_for_status()

        soup = BeautifulSoup(requisicao.text, 'html.parser')

        total_resultados_element = soup.find('p', class_='subtitle is-5')
        total_resultados = int(total_resultados_element.find('b').text.strip())

        print(f"Total de Resultados Encontrados: {total_resultados}")

        dados_empresas = []

        for page_number in range(1, (total_resultados // 10) + 2):
            payload['page'] = page_number

            requisicao = requests.get(url_pesquisa, headers=headers, params=payload)
            requisicao.raise_for_status()

            soup = BeautifulSoup(requisicao.text, 'html.parser')

            detalhes_divs = soup.find_all('div', class_='box')

            for detalhe_div in detalhes_divs:
                link_detalhes = detalhe_div.find('a')['href']
                url_detalhes = f'{url_base}{link_detalhes}'
                print(f"Link para mais detalhes: {url_detalhes}")

                # Extrair informações desejadas do HTML, incluindo a situação cadastral
                situacao_cadastral = obter_situacao_cadastral(url_detalhes, headers)
                if situacao_cadastral == 'ATIVA':
                    dados_empresa = extrair_informacoes_detalhes(url_detalhes, headers)
                    dados_empresas.append(dados_empresa)
                    print(f"Link para mais detalhes: {url_detalhes}")

        return dados_empresas

    except requests.exceptions.RequestException as err:
        print("Something went wrong with the request:", err)
        return None

def extrair_informacoes_detalhes(url_detalhes, headers):
    try:
        requisicao_detalhes = requests.get(url_detalhes, headers=headers)
        requisicao_detalhes.raise_for_status()

        soup_detalhes = BeautifulSoup(requisicao_detalhes.text, 'html.parser')

        # Extrair informações desejadas do HTML
        cnpj = obter_texto_safado(soup_detalhes.find('p', string='CNPJ'))
        razao_social = obter_texto_safado(soup_detalhes.find('p', string='Razão Social'))
        nome_fantasia = obter_texto_safado(soup_detalhes.find('p', string='Nome Fantasia'))
        tipo = obter_texto_safado(soup_detalhes.find('p', string='Tipo'))

        situacao_cadastral = obter_texto_safado(soup_detalhes.find('p', string='Situação Cadastral'))
        telefone = obter_texto_safado(soup_detalhes.find('p', string='Telefone'))
        email = obter_texto_safado(soup_detalhes.find('p', string='E-MAIL'))
        # ... Adicione outras informações conforme necessário

        # Criar um dicionário com as informações
        dados_empresa = {
            'CNPJ': cnpj,
            'Razao_Social': razao_social,
            'Nome_Fantasia': nome_fantasia,
            'Tipo': tipo,
            'situacao_cadastral': situacao_cadastral,
            'telefone' :telefone,
            'email' :email,
            # ... Adicione outras chaves conforme necessário
        }

        # Imprimir as informações no terminal (opcional)
        print(json.dumps(dados_empresa, indent=2))

        return dados_empresa

    except requests.exceptions.RequestException as err:
        print("Something went wrong with the request:", err)
        return None

def obter_texto_safado(elemento):
    if elemento and elemento.find_next('p'):
        return elemento.find_next('p').text.strip()
    else:
        return None

def obter_situacao_cadastral(url_detalhes, headers):
    try:
        requisicao_detalhes = requests.get(url_detalhes, headers=headers)
        requisicao_detalhes.raise_for_status()

        soup_detalhes = BeautifulSoup(requisicao_detalhes.text, 'html.parser')
        situacao_cadastral = obter_texto_safado(soup_detalhes.find('p', string='Situação Cadastral'))

        return situacao_cadastral

    except requests.exceptions.RequestException as err:
        print("Something went wrong with the request:", err)
        return None

# Nome do arquivo JSON
nome_arquivo = entrada

# Abrir o arquivo em modo de escrita
with open(nome_arquivo, 'w') as arquivo_json:
    # Redefinir a saída padrão para o arquivo
    sys.stdout = arquivo_json

# Restaurar a saída padrão
sys.stdout = sys.__stdout__

# Adicionar um espaço entre as chamadas ou modificar o payload conforme necessário
print("\n\n")

# Abrir o arquivo em modo de escrita novamente
with open(nome_arquivo, 'a') as arquivo_json:
    # Redefinir a saída padrão para o arquivo
    sys.stdout = arquivo_json

    # Chamada da função mágica 
    extrair_links_detalhes(url_pesquisa, headers, payload)

# Restaurar a saída padrão
sys.stdout = sys.__stdout__

# Carregar e imprimir as informações do arquivo JSON no terminal
with open(nome_arquivo, 'r') as arquivo_json:
    dados_json = json.load(arquivo_json)
    print(json.dumps(dados_json, indent=2))

print(f"As informações foram salvas em '{nome_arquivo}'")
