from os import listdir, path, mkdir
import re

# Filtering the files in input directory
files = []
p = re.compile(r'entrada\d+.txt', re.IGNORECASE)
for file in listdir('input'):
    filePath = path.join('input', file)
    if(path.isfile(filePath) and p.match(file)):
        files.append(filePath)

# Creating output directory
if (not path.exists('output')):    
    mkdir('output')

# Creating output files
for filePath in files:
    inputFile = open(filePath)
    number = re.search(r'\d+', filePath)[0]
    content = inputFile.read()
    outputFile = open('output/saida'+number+'.txt', 'w')
    outputFile.write(content)
    outputFile.close()
    inputFile.close()