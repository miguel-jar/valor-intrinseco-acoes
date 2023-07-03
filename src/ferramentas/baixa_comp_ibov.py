"""
Este código entra na página do Índice Ibovespa e
baixa os arquivos que contém as composições atual e teórica do índice
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException

import pandas as pd
import datetime
import yaml
import os


def composicao(downloads, file_composicao, chromeDriver):

    novo_nome = fr'{downloads}' + file_composicao

    dia = datetime.date.today().day
    data_atual = datetime.date.today()
    dia_semana = datetime.date.today().weekday()

    if dia_semana == 5:
        dia += 2
    elif dia_semana == 6:
        dia += 1

    nome_antigo = downloads + data_atual.strftime(fr"\IBOVDia_{dia:0>2}-%m-%y.csv")

    if os.path.isfile(nome_antigo): os.remove(nome_antigo)
    if os.path.isfile(novo_nome): os.remove(novo_nome)

    options = webdriver.ChromeOptions()
    servico = Service(executable_path=chromeDriver)

    try:
        with webdriver.Chrome(service=servico, options=options) as navegador:

            wdw = WebDriverWait(navegador, 5)

            navegador.get(r'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br')
            navegador.maximize_window()

            xpath_botao_download = '//*[@id="divContainerIframeB3"]/div/div[1]/form/div[2]/div/div[2]/div/div/div[1]/div[2]/p/a'

            try:
                download = wdw.until(ec.visibility_of_element_located((By.XPATH, xpath_botao_download)))
                navegador.execute_script("arguments[0].click();", download)  # Executa o clique usando JavaScript

                while not os.path.isfile(nome_antigo): continue
                os.rename(nome_antigo, novo_nome)  # renomeia o arquivo para ibov.csv

                print(f"\nArquivo de composicao baixado com sucesso!")
                return novo_nome

            except TimeoutException:
                raise ArquivoNaoBaixadoException("o botão de download não foi encontrado. Confira o XPATH do botão e tente novamente")

    except SessionNotCreatedException as e:
        raise ArquivoNaoBaixadoException("não foi possível iniciar o navegador. \n\n" + e.msg)    

def composicaoTeorica(downloads, file_composicao_teorica, chromeDriver):

    nome_arquivo = fr'{downloads}' + file_composicao_teorica

    if os.path.isfile(nome_arquivo):
        os.remove(nome_arquivo)

    options = webdriver.ChromeOptions()
    servico = Service(executable_path=chromeDriver)

    try:
        with webdriver.Chrome(service=servico, options=options) as navegador:

            wdw = WebDriverWait(navegador, 5)

            navegador.get('https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br')
            navegador.maximize_window()

            xpath_botao_composicao = '//*[@id="divContainerIframeB3"]/div/div[2]/app-menu-portfolio/div/ul/li[1]/a'
            xpath_botao_download = '//*[@id="divContainerIframeB3"]/div/div[1]/form/div[3]/div/div[2]/div/div/div[1]/div[2]/p/a'

            try:
                comp = wdw.until(ec.element_to_be_clickable((By.XPATH, xpath_botao_composicao)))
                navegador.execute_script("arguments[0].click();", comp)  # Executa o clique usando JavaScript

                try:
                    download = wdw.until(ec.visibility_of_element_located((By.XPATH, xpath_botao_download)))
                    navegador.execute_script("arguments[0].click();", download)  # Executa o clique usando JavaScript

                    while not os.path.isfile(nome_arquivo): continue

                    print(f"\nArquivo de composicao teórica baixado com sucesso!")
                    return nome_arquivo
                                
                except TimeoutException:
                    raise ArquivoNaoBaixadoException("o botão de download não foi encontrado. Confira o XPATH do botão e tente novamente")
            
            except TimeoutException:
                raise ArquivoNaoBaixadoException("o botão de seleção da composição não foi encontrado. Confira o XPATH do botão e tente novamente")

    except SessionNotCreatedException as e:
        raise ArquivoNaoBaixadoException("não foi possível iniciar o navegador. \n\n" + e.msg)        

if __name__ == '__main__':

    from exceptions import ArquivoNaoBaixadoException  # foi indicado aqui pra não conflitar com a chamada dos códigos VI

    try:
        
        with open('src/ferramentas/parametros.yaml', 'r') as parametros:
            args = yaml.load(parametros, yaml.SafeLoader)

        try:
            name = composicao(args['diretorioDownloads'], args['fileCompAtual'], chromeDriver=args['chromeDriver'])
            # name = composicaoTeorica(args['diretorioDownloads'], args['fileCompTeorica'], chromeDriver=args['chromeDriver'])

            dataFrame = pd.read_csv(name, sep=';', encoding='ANSI', 
                                    names=['Código', 'Ação', 'Tipo', 'Qtde. Teórica', 'Part. (%)', 0], skiprows=[0, 1])

            tamanho = len(dataFrame)
            dataFrame.drop(columns=[0], index=[tamanho-1, tamanho-2], inplace=True)

            print(f"\n{dataFrame}\n")
        
        except ArquivoNaoBaixadoException as e:
            print(e.msg)

    except FileNotFoundError:
        print("\nNão foi possível ler o arquivo de parmâmetros. Programa Finalizado\n")
