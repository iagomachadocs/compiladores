from os import listdir, path, mkdir, remove
import re
from lexical_analyser import LexicalAnalyser


def removeLineComment(line):
    match = re.search(r'\/\/.*', line)
    if(match):
        return line[:match.start()]
    else:
        return line

def removeMultiLineComments(lines):
    for i in range(len(lines)):
        match = re.search(r'\/\*.*\*\/', lines[i])
        if(match): # Comentário de bloco que inicia e termina na mesma linha
            lines[i] = lines[i][:match.start()] + lines[i][match.end():]
        else:
            match = re.search(r'\/\*.*', lines[i])
            if(match): # Comentário de bloco que inicia em uma linha e termina em outra
                comment = lines[i][match.start():]
                lines[i] = lines[i][:match.start()]
                j = i+1
                commentClosed = False
                while j < len(lines) and not commentClosed:
                    match = re.search(r'.*\*\/', lines[j])
                    if(match):
                        comment = comment+'\t'+lines[j][:match.end()]
                        lines[j] = lines[j][match.end():]
                        commentClosed = True
                    else:
                        comment = comment+'\t'+lines[j]
                        lines[j] = ''
                        j += 1
                if(not commentClosed):
                    errors.append({"line": str(i+1), "type": "CoMF", "lexeme": comment})
                i=j
    return lines

def writeErrors(output):
    for error in errors:
        output.write(error["line"]+' '+error["type"]+' '+error["lexeme"])

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
    inputFile = open(filePath)
    number = re.search(r'\d+', filePath)[0]
    outputFile = open('output/saida'+number+'.txt', 'w')
    source_code = inputFile.readlines()
    lexical_analyser = LexicalAnalyser(source_code)
    lexical_analyser.analyse()
    lexical_analyser.write_tokens(outputFile)
    lexical_analyser.write_errors(outputFile)    
    outputFile.close()
    inputFile.close()
