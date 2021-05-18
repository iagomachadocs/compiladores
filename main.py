"""
 Código de um analisador sintático, desenvolvido como solução do Problema 3
 do MI-Processadores de Linguagem de Programação.
 Autor: Iago Machado da Conceição Silva
"""
from os import listdir, path, mkdir, remove
import re
from lexical_analyser import LexicalAnalyser
from token_class import Token
from parser_class import Parser

# Filtra arquivos no diretorio de entrada
files = []
p = re.compile(r'entrada\d+.txt', re.IGNORECASE)
for file in listdir('input'):
    filePath = path.join('input', file)
    if(path.isfile(filePath) and p.match(file)):
        files.append(filePath)

# Cria o diretorio de saída, caso não exista
if (not path.exists('output')):
    mkdir('output')
else:  # Remove todos os arquivos que estiverem na pasta de saída
    for f in listdir('output'):
        if(path.isfile(path.join('output', f))):
            remove(path.join('output', f))

for filePath in files:
    try:
        inputFile = open(filePath, 'r')
        number = re.search(r'\d+', filePath)[0]
        outputFile = open('output/saida'+number+'.txt', 'w')
        source_code = inputFile.readlines()
        lexical_analyser = LexicalAnalyser(source_code)
        print('--------------------------------------------------')
        print("Analysing "+path.basename(inputFile.name))
        tokens = lexical_analyser.analyse()
        lexical_analyser.write_tokens(outputFile)
        lexical_analyser.write_errors(outputFile)
        if(lexical_analyser.get_errors() == 0):
            parser = Parser(tokens, outputFile)
            parser.run()
        print("Output "+path.basename(outputFile.name)+' generated!')    
        outputFile.close()
        inputFile.close()
    except:
        print('Error processing input file', filePath)
