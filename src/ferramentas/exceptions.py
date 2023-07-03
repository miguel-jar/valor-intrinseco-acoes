
class ArquivoNaoBaixadoException(Exception):
    def __init__(self, mensagem) -> None:
        self.msg = "\nO arquivo não pode ser baixado pois " + mensagem + "\n"

    def __str__(self):
        return self.msg
    
class LeituraTabelaException(Exception):
    def __init__(self, mensagem) -> None:
        self.msg = "\nNão foi possível ler as informações pois " + mensagem + "\n"

    def __str__(self):
        return self.msg