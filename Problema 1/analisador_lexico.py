from os import listdir, path, mkdir, remove
import re

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
else: #Delete all remaining files in output
    for f in listdir('output'):
        if(path.isfile(path.join('output', f))):
            remove(path.join('output', f))


# Create output files
for filePath in files:
    inputFile = open(filePath)
    number = re.search(r'\d+', filePath)[0]
    content = inputFile.read()
    outputFile = open('output/saida'+number+'.txt', 'w')
    outputFile.write(content)
    outputFile.close()
    inputFile.close()