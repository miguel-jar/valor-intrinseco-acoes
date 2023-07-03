"""
    Este código calcula o valor intrínseco de todas as ações que fazem parte da composição atual do Ibovespa
"""

from ferramentas.baixa_estatisticas import download_estatisticas
from ferramentas.baixa_comp_ibov import composicao
from ferramentas.exceptions import ArquivoNaoBaixadoException

import pandas as pd
import yaml
import os

if __name__ == "__main__":

    try:

        with open('src/parametros.yaml', 'r') as parametros:
            args = yaml.load(parametros, yaml.SafeLoader)

        arquivoComposicao = args["pathDownloads"] + args['arquivoComposicao']
        arquivoEstatisticas = args["pathDownloads"] + args['arquivoEstatisicas']

        if os.path.isfile(arquivoEstatisticas) and os.path.isfile(arquivoComposicao):
                        
            choice = input('\nDeseja atualizar a base de dados [s/n]? ').strip().upper()[0]

            if choice == 'S':
                composicao(args["pathDownloads"], args['arquivoComposicao'], args['chromeDriver'])
                download_estatisticas(args["pathDownloads"], args['arquivoEstatisicas'], args['chromeDriver'])

        else:
            print('\nArquivos não encontrados. Baixando...')

            composicao(args["pathDownloads"], args['arquivoComposicao'], args['chromeDriver'])
            download_estatisticas(args["pathDownloads"], args['arquivoEstatisicas'], args['chromeDriver'])

        acoes = pd.read_csv(arquivoComposicao, sep=';', encoding='ANSI', names=['Ticker', 1, 2, 3, 4, 5], skiprows=[0, 1])

        tamanho = len(acoes)
        acoes.drop(index=[tamanho-1, tamanho-2], columns=[1, 2, 3, 4, 5], inplace=True)

        # A partir daqui, o código faz a análise das estatísticas das empresas do IBOV
        estatisticas = pd.read_csv(arquivoEstatisticas, sep=';')

        for c in estatisticas.columns:
            if c not in ['TICKER', 'PRECO', 'P/L', 'P/VP', ' VPA', ' LPA']:
                estatisticas.pop(c)

        estatisticas.columns = ['TICKER', 'PRECO', 'P/L', 'P/VP', 'VPA', 'LPA']

        g = dict()
        desconsideradas = list()

        for c in acoes['Ticker']:
            d = estatisticas['TICKER'][estatisticas['TICKER'] == c]
            indice = d.index[0]

            vpa = str(estatisticas['VPA'][indice]).replace('.', '').replace(',', '.')
            vpa = float(vpa)

            lpa = str(estatisticas['LPA'][indice]).replace('.', '').replace(',', '.')
            lpa = float(lpa)

            if vpa > 0 and lpa > 0:
                estatisticas['P/L'][indice] = estatisticas['P/L'][indice].replace('.', '')

                valorAtual = float(estatisticas['P/L'][indice].replace(',', '.')) * lpa
                valorIntrinseco = round((lpa*vpa*22.5)**(1/2), 2)
                margemSeguranca = round(1-valorAtual/valorIntrinseco, 2)

                g[c] = {'VALOR_INTRINSECO': valorIntrinseco,
                        'MARGEM_DE_SEGURANCA': margemSeguranca}.copy()
            else:
                desconsideradas.append(c)

        estatisticas = pd.DataFrame(data=g.values(), index=g.keys())

        while True:

            # Verifica como o usuário deseja que os dados sejam apresentados no CSV
            print('\n[1] Ticker em ordem alfabética'
                '\n[2] Valor intrínseco, em ordem cresecente'
                '\n[3] Valor intrínseco, em ordem decresecente'
                '\n[4] Margem de segurança, em ordem cresecente'
                '\n[5] Margem de segurança, em ordem decresecente')
            organizacao = input('\nComo deseja que o arquivo esteja ordanizado? ').strip()

            if organizacao in ['1', '2', '3', '4', '5']:
                break

            print('\nFormatação não encontrada. Tente novamente.')

        if organizacao == '2': estatisticas.sort_values(by='VALOR_INTRINSECO', inplace=True)
        elif organizacao == '3': estatisticas.sort_values(by='VALOR_INTRINSECO', ascending=False, inplace=True)
        elif organizacao == '4': estatisticas.sort_values(by='MARGEM_DE_SEGURANCA', inplace=True)
        elif organizacao == '5': estatisticas.sort_values(by='MARGEM_DE_SEGURANCA', ascending=False, inplace=True)

        estatisticas.to_csv(args["saveDirectory"] + args["arquivoConsideradasIBOV"], sep=' ', header=False, index=True)

        print(f'\nArquivo {args["arquivoConsideradasIBOV"]} criado com sucesso !!')

        print('\nAções desconsideradas, devido a VPA ou LPA negativos: ', end='')
        for r in desconsideradas:
            print(r, end=' ')
        print("\n")

    except FileNotFoundError as a:
        print("Não foi possível ler o arquivo de parmâmetros. Programa Finalizado\n")

    except ArquivoNaoBaixadoException as e:
        print(e.msg)