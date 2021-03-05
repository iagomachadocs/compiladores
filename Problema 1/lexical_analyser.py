import re
from token import Token

RESERVED_WORDS = ['var', 'const', 'typedef', 'struct', 'extends', 'procedure',
                 'function', 'start', 'return', 'if', 'else', 'then', 'while',
                 'read', 'print', 'int', 'real', 'boolean', 'string', 'true',
                 'false', 'global', 'local']

LETTER = re.compile(r'[a-zA-Z]')
LETTER_DIGIT_UNDERSCORE = re.compile(r'[a-zA-Z0-9_]')

class LexicalAnalyser:

  def __init__(self, source_code):
    self.source_code = source_code
    self.errors = []
    self.tokens = []
    self.line_index = 0
    self.column_index = 0

  def __identifier_or_reserved_word__(self):
    lexeme = ''
    line = self.source_code[self.line_index]
    while (self.column_index < len(line)):
      char = line[self.column_index]
      if(LETTER_DIGIT_UNDERSCORE.match(char)):
        lexeme += char
        self.__next_column__()
      else:
        if lexeme in RESERVED_WORDS:
          token = Token(self.line_index+1, "PRE", lexeme)
        else:
          token = Token(self.line_index+1, "IDE", lexeme)
        self.tokens.append(token)
        return
  
  def __multiline_comment__(self):
    comment_line = self.line_index
    comment = ''
    while (self.line_index < len(self.source_code)):
      while (self.column_index < len(self.source_code[self.line_index])):
        char = self.source_code[self.line_index][self.column_index]
        comment += char
        if(char == '*' and self.column_index+1 < len(self.source_code[self.line_index])):
          next_char = self.source_code[self.line_index][self.column_index+1]
          if(next_char == '/'):
            self.__next_column__()
            self.__next_column__()
            return True
        self.__next_column__()
      self.__next_line__()
      comment += '\t'
    
    error = Token(comment_line, "CoMF", comment)
    self.errors.append(error)
    return False


  def analyse(self):
    while (self.line_index < len(self.source_code)):
      while (self.column_index < len(self.source_code[self.line_index])):
        char = self.source_code[self.line_index][self.column_index]
        if(LETTER.match(char)):
          self.__identifier_or_reserved_word__()
        elif(char == '/'):
          if(self.column_index+1 < len(self.source_code[self.line_index])):
            next_char = self.source_code[self.line_index][self.column_index+1]
            if(next_char == '/'):
              self.__next_line__() # Comentário de linha
            elif(next_char == '*'):
              closed = self.__multiline_comment__() # Comentário de bloco
              if(not closed):
                return
            else:
              self.__next_column__()
        else:
          self.__next_column__()
      self.__next_line__()
  
  def write_tokens(self, output):
    for token in self.tokens:
      output.write(token.__str__()+'\n')

  def write_errors(self, output):
    for error in self.errors:
      output.write(error.__str__()+'\n')


  def __next_line__(self):
    self.line_index += 1
    self.column_index = 0
  
  def __next_column__(self):
    self.column_index += 1

  
