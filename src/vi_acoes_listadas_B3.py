"""
    Calcula o valor intrínseco de todas as ações listadas na B3
"""

from ferramentas.baixa_estatisticas import download_estatisticas
from ferramentas.exceptions import ArquivoNaoBaixadoException

import pandas as pd
import yaml
import os


if __name__ == "__main__":

    try:

        with open('src/parametros.yaml', 'r') as parametros:
            args = yaml.load(parametros, yaml.SafeLoader)

        nome = args['pathDownloads'] + args['arquivoEstatisicas']

        if not os.path.isfile(nome):
            print('\nArquivo de estatisticas não encontrado. Baixando...')
            download_estatisticas(args["pathDownloads"], args['arquivoEstatisicas'], args['chromeDriver'])
        
        else:
            choice = input('\nDeseja atualizar a base de dados [s/n]? ').strip()[0]

            if choice == 's':
                print('Atualizando...')
                download_estatisticas(args["pathDownloads"], args['arquivoEstatisicas'], args['chromeDriver'])
        
        estatisticas = pd.read_csv(nome, sep=';')

        for c in estatisticas.columns:
            if c not in ['TICKER', 'PRECO', 'P/L', ' LIQUIDEZ MEDIA DIARIA', ' VPA', ' LPA']:
                estatisticas.pop(c)

        estatisticas.columns = ['TICKER', 'PRECO', 'P/L', 'LIQUIDEZ', 'VPA', 'LPA']

        g = dict()
        desconsideradas = list()

        for c in range(0, len(estatisticas)):
            ticker = estatisticas['TICKER'][c]

            pl = str(estatisticas['P/L'][c]).replace('.', '').replace(',', '.')
            pl = float(pl)

            liquidez_media = str(estatisticas['LIQUIDEZ'][c]).replace('.', '').replace(',', '.')
            liquidez_media = float(liquidez_media)

            vpa = str(estatisticas['VPA'][c]).replace('.', '').replace(',', '.')
            vpa = float(vpa)

            lpa = str(estatisticas['LPA'][c]).replace('.', '').replace(',', '.')
            lpa = float(lpa)

            if vpa > 0 and lpa > 0 and pl != 0 and liquidez_media > args["liquidezMinima"]:
                valor_instrinseco = round((22.5 * vpa * lpa) ** (1/2), 2)
                valor_atual = pl * lpa
                margem_seguranca = round(1 - valor_atual/valor_instrinseco, 2)

                g[ticker] = {'VALOR_INTRINSECO': valor_instrinseco, 'MARGEM_DE_SEGURANCA': margem_seguranca}.copy()

            else:
                desconsideradas.append(ticker)

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

        arquivoAcoesConsideradas = args["saveDirectory"] + args["arquivoConsideradas"]
        estatisticas.to_csv(arquivoAcoesConsideradas, sep=' ', header=False, index=True)

        arquivoAcoesDesconsideradas = args["saveDirectory"] + args["arquivoDesconsideradas"]

        try:

            with open(arquivoAcoesDesconsideradas, 'w') as arquivo:
                for t in desconsideradas:
                    arquivo.write(t + '\n')

        except FileNotFoundError:

            with open(arquivoAcoesDesconsideradas, 'x') as arquivo:
                for t in desconsideradas:
                    arquivo.write(t + '\n')

        print(f'\nAções desconsideradas podem ser encontradas no arquivo {args["arquivoDesconsideradas"]}')
        print(f'O resultado dos cálculos pode ser encontrado no arquivo {args["arquivoConsideradas"]}\n')

        print(f'IMPORTANTE: Ações com VPA ou LPA negativos; com PL = 0 e liquidez diária < {args["liquidezMinima"]} '
            f'foram desconsideradas no cálculo do Valor Intrínseco\n')

    except FileNotFoundError :
        print("Não foi possível ler o arquivo de parmâmetros. Programa Finalizado\n")

    except ArquivoNaoBaixadoException as e :
        print(e.msg)