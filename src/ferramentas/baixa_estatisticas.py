"""
O objetivo deste código é entrar no Status Invest e baixar um csv que contém as
estatísticas financeiras de todas as empresas listadas na B3
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, WebDriverException

import pandas as pd
import os
import yaml

def download_estatisticas(path, file_estatisicas, chromedriver):

    nome_arquivo = path + file_estatisicas

    if os.path.isfile(nome_arquivo):  
        os.remove(nome_arquivo)

    options = webdriver.ChromeOptions()
    servico = Service(executable_path=chromedriver)

    try:

        with webdriver.Chrome(service=servico, options=options) as navegador:
            wdw = WebDriverWait(navegador, timeout=5)

            navegador.maximize_window()
            navegador.get('https://statusinvest.com.br/acoes/busca-avancada')

            xpath_botao_busca = '//*[@id="main-2"]/div[3]/div/div/div/button[2]'
            xpath_botao_download = '//*[@id="main-2"]/div[4]/div/div[1]/div[2]/a'
            
            try:
                botao = wdw.until(ec.visibility_of_element_located((By.XPATH, xpath_botao_busca)))
                navegador.execute_script("arguments[0].click();", botao)  # Executa o clique usando JavaScript

                try:
                    download = wdw.until(ec.visibility_of_element_located((By.XPATH, xpath_botao_download)))
                    navegador.execute_script("arguments[0].click();", download)  # Executa o clique usando JavaScript

                    while not os.path.isfile(nome_arquivo): continue # espera o arquivo ser baixado
                
                    print(f"\nArquivo de estatísticas baixado com sucesso!")
                    return nome_arquivo
                
                except TimeoutException:
                    raise ArquivoNaoBaixadoException("o botão de download não foi encontrado. Confira o XPATH do botão e tente novamente")

            except TimeoutException:
                raise ArquivoNaoBaixadoException("o botão de busca não foi encontrado. Confira o XPATH do botão e tente novamente")

    except SessionNotCreatedException as e:
        raise ArquivoNaoBaixadoException("não foi possível iniciar o navegador. O chromedriver está desatualizado.\n\n" + e.msg)
    
    except WebDriverException as e:
        raise ArquivoNaoBaixadoException("não foi possível iniciar o navegador. Chromedriver não encontrado.\n\n" + e.msg)     


if __name__ == '__main__':

    from exceptions import ArquivoNaoBaixadoException  # foi indicado aqui pra não conflitar com a chamada dos códigos VI

    try:

        with open('src/ferramentas/parametros.yaml', 'r') as parametros:
            args = yaml.load(parametros, yaml.SafeLoader)

        try:
            nome = download_estatisticas(args['diretorioDownloads'], args['fileEstatisicas'], args['chromeDriver'])
            dataFrame = pd.read_csv(nome, sep=';')
            print(f'\n{dataFrame.head(5)}')
            print()
        
        except ArquivoNaoBaixadoException as e:
            print(e.msg)

    except FileNotFoundError:
        print("Não foi possível ler o arquivo de parmâmetros. Programa Finalizado\n")
