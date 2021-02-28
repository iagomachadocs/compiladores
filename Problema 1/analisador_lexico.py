from os import listdir, path, mkdir, remove
import re

reservedWords = ['var', 'const', 'typedef', 'struct', 'extends', 'procedure',
                 'function', 'start', 'return', 'if', 'else', 'then', 'while',
                 'read', 'print', 'int', 'real', 'boolean', 'string', 'true',
                 'false', 'global', 'local']

letter = re.compile(r'[a-zA-Z]')
letterDigit_ = re.compile(r'[a-zA-Z0-9_]')


def isIdentifierOrReservedWord(line, position):
    lexeme = ''
    for i in range(position, len(line)):
        char = line[i]
        if(letterDigit_.match(char)):
            lexeme += char
        else:
            if lexeme in reservedWords:
                return {"lexeme": lexeme, "type": "PRE", "next": i}
            else:
                return {"lexeme": lexeme, "type": "IDE", "next": i}


def removeLineComment(line):
    match = re.search(r'\/\/.*', line)
    if(match):
        return line[:match.start()]
    else:
        return line


# Filter files in input directory
files = []
p = re.compile(r'entrada\d+.txt', re.IGNORECASE)
for file in listdir('input'):
    filePath = path.join('input', file)
    if(path.isfile(filePath) and p.match(file)):
        files.append(filePath)

# Create output directory
if (not path.exists('output')):
    mkdir('output')
else:  # Delete all remaining files in output
    for f in listdir('output'):
        if(path.isfile(path.join('output', f))):
            remove(path.join('output', f))


for filePath in files:
    inputFile = open(filePath)
    number = re.search(r'\d+', filePath)[0]
    outputFile = open('output/saida'+number+'.txt', 'w')
    lines = inputFile.readlines()
    for i in range(len(lines)):
        line = lines[i]
        line = removeLineComment(line)
        j = 0
        while j < len(line):
            char = line[j]
            if(letter.match(char)):
                token = isIdentifierOrReservedWord(line, j)
                outputFile.write(
                    str(i+1)+' '+token['type']+' '+token['lexeme']+'\n'
                )
                j = token['next']
            else:
                j += 1
    outputFile.close()
    inputFile.close()
