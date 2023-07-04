"""
Este código entre na página da B3 que tem a composição do Índice Ibovespa, seleciona a composição teórica,
configura a tabela para 120 linhas e cria um dataFrame com as informações contidas na tabela
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, WebDriverException

import pandas as pd
import yaml

def leComposicao(chromedriver):

    options = webdriver.ChromeOptions()
    servico = Service(executable_path=chromedriver)

    try:
        with webdriver.Chrome(service=servico, options=options) as navegador:

            wdw = WebDriverWait(navegador, 5)

            navegador.maximize_window()
            navegador.get(r'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br')

            idSelecao = 'selectPage'
            xpath_botao = '//*[@id="divContainerIframeB3"]/div/div[1]/form/div[2]/div/table'
            
            try:
                muda_tamanho = wdw.until(ec.element_to_be_clickable((By.ID, idSelecao)))
                seleciona_120 = Select(muda_tamanho)
                seleciona_120.select_by_visible_text('120')
 
                try:
                    tabela = wdw.until(ec.visibility_of_element_located((By.XPATH, xpath_botao)))
                    tabela_html = tabela.get_attribute('outerHTML')

                    data_frame = pd.read_html(tabela_html)[0] 

                    tamanho = len(data_frame)
                    data_frame.drop(index=[tamanho - 1, tamanho - 2], inplace=True)

                    return data_frame
    
                except TimeoutException:
                    raise LeituraTabelaException("a tabela não foi encontrada na página. Confira o XPATH da tabela e tente novamente")

            except TimeoutException:
                raise LeituraTabelaException("o campo de seleção do tamanho da tabela não foi encontrado. Confira o ID do campo e tente novamente")

    except SessionNotCreatedException as e:
        raise LeituraTabelaException("não foi possível iniciar o navegador. O chromedriver está desatualizado.\n\n" + e.msg)
    
    except WebDriverException as e:
        raise LeituraTabelaException("não foi possível iniciar o navegador. Chromedriver não encontrado.\n\n" + e.msg)   


def leComposicaoTeorica(chromedriver):

    options = webdriver.ChromeOptions()
    servico = Service(executable_path=chromedriver)

    try:
        with webdriver.Chrome(service=servico, options=options) as navegador:

            wdw = WebDriverWait(navegador, 5)

            navegador.maximize_window()
            navegador.get('https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br')

            xpath_botao_teoria = '//*[@id="divContainerIframeB3"]/div/div[2]/app-menu-portfolio/div/ul/li[1]/a'
            idSelecao = 'selectPage'
            xpath_tabela = '//*[@id="divContainerIframeB3"]/div/div[1]/form/div[3]/div/table'

            try:
                botaoTeorica = wdw.until(ec.element_to_be_clickable((By.XPATH, xpath_botao_teoria)))
                navegador.execute_script("arguments[0].click();", botaoTeorica)  # Executa o clique usando JavaScript
                
                try:
                    mudaTamanho = wdw.until(ec.element_to_be_clickable((By.ID, idSelecao)))  # encontra o botão de seleção da quantidade de linhas da tabela
                    seleciona_120 = Select(mudaTamanho)  # diz que o botão é uma lista de seleção
                    seleciona_120.select_by_visible_text('120')  # seleciona a opção 120
                
                    try:
                        tabela = wdw.until(ec.visibility_of_element_located((By.XPATH, xpath_tabela)))  # pega os elementos da tabela
                        tabelaHTML = tabela.get_attribute('outerHTML')  # converte a tabela no formato X para uma estrutura html

                        data_frame = pd.read_html(tabelaHTML)[0]  # cria um data frame a partir do html da tabela

                        tamanho = len(data_frame)
                        data_frame.drop(index=[tamanho-1, tamanho-2], inplace=True)

                        return data_frame
                    
                    except TimeoutException:
                        raise LeituraTabelaException("a tabela não foi encontrada na página. Confira o XPATH da tabela e tente novamente")
                
                except TimeoutException:
                    raise LeituraTabelaException("o campo de seleção do tamanho da tabela não foi encontrado. Confira o ID do campo e tente novamente")

            except TimeoutException:
                raise LeituraTabelaException("o botão de seleção não foi encontrado. Confira o XPATH do botão e tente novamente")

    except SessionNotCreatedException as e:
        raise LeituraTabelaException("não foi possível iniciar o navegador. O chromedriver está desatualizado.\n\n" + e.msg)
    
    except WebDriverException as e:
        raise LeituraTabelaException("não foi possível iniciar o navegador. Chromedriver não encontrado.\n\n" + e.msg)   


if __name__ == '__main__':

    from exceptions import LeituraTabelaException  # foi indicado aqui pra não conflitar com a chamada dos códigos VI

    try:
        
        with open('src/ferramentas/parametros.yaml', 'r') as parametros:
            args = yaml.load(parametros, yaml.SafeLoader)

        try:
            dataFrame = leComposicao(args['chromeDriver'])
            dataFrame = leComposicaoTeorica(args['chromeDriver'])

            print(f"\n{dataFrame}\n")

        except LeituraTabelaException as e:
            print(e.msg)

    except FileNotFoundError:
        print("Não foi possível ler o arquivo de parmâmetros. Programa Finalizado\n")
