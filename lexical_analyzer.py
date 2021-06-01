"""
 Código de um analisador léxico, desenvolvido como solução do Problema 1
 do MI-Processadores de Linguagem de Programação.
 Autor: Iago Machado da Conceição Silva
"""
import re
from token_class import Token

RESERVED_WORDS = set(['var', 'const', 'typedef', 'struct', 'extends', 'procedure',
                 'function', 'start', 'return', 'if', 'else', 'then', 'while',
                 'read', 'print', 'int', 'real', 'boolean', 'string', 'true',
                 'false', 'global', 'local'])

DELIMITERS = set(['.', ',', '(', ')', ';', '[', ']', '{', '}'])
LOGICAL_OPERATORS = set(['&', '|', '!'])
ARITHMETIC_OPERATORS = set(['+','-','*','/'])
DIGITS = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
RELATIONAL_OPERATORS = set(['=', '>', '<'])
IGNORE = set([' ', '\n', '\t'])

RE_LETTER = re.compile(r'[a-zA-Z]') # Regex para identificar letra
RE_LETTER_DIGIT_UNDERSCORE = re.compile(r'[a-zA-Z0-9_]') # Regex para identificar letra, dígito ou underscore
RE_SIMBOL = re.compile(r'[\x20|\x21|\x23-\x7E]') # Regex para identificar os símbolos 32 a 126 (exceto o 34) da tabela ASCII

class LexicalAnalyzer:

  def __init__(self, source_code):
    self.source_code = source_code
    self.errors = []
    self.tokens = []
    self.line_index = 0
    self.column_index = 0

  """
  Função para identificar identificadores ou palavras reservadas.
  Padrão: letra( letra | dígito| _ )*
  """
  def __identifier_or_reserved_word(self):
    lexeme = ''
    line = self.source_code[self.line_index]
    while (self.column_index < len(line)):
      char = line[self.column_index]
      if(RE_LETTER_DIGIT_UNDERSCORE.match(char)):
        lexeme += char
        self.__next_column()
      else:
        if lexeme in RESERVED_WORDS:
          token = Token(self.line_index+1, "PRE", lexeme)
        else:
          token = Token(self.line_index+1, "IDE", lexeme)
        self.tokens.append(token)
        return
  
  """
  Função para ignorar comentário de bloco.
  Padrão: /* comentário */
  Caso o comentário não seja fechado é gerado um erro de comentário mal formado.
  """
  def __multiline_comment(self):
    comment_line = self.line_index+1
    comment = '/*'
    self.__next_column()
    while (self.line_index < len(self.source_code)):
      while (self.column_index < len(self.source_code[self.line_index])):
        char = self.__get_char()
        comment += char
        if(char == '*' and self.__has_next_column()):
          self.__next_column()
          char = self.__get_char()
          if(char == '/'):
            self.__next_column()
            return True
        else:
          self.__next_column()
      self.__next_line()
      comment += '\t'
    
    error = Token(comment_line, "CoMF", comment)
    self.errors.append(error)
    return False
  
  """
  Função que identifica cadeia de caracteres.
  Padrão: "( letra | dígito| símbolo | \" )*"
  Caso a cadeia não seja fechada até o fim da linha ou caso haja caracteres inválidos
  dentro da cadeia é gerado um erro de cadeia mal formada.
  """
  def __string(self):
    string_line = self.line_index+1
    string = '\"'
    self.__next_column()
    invalid_string = False
    while (self.column_index < len(self.source_code[self.line_index])):
      char = self.__get_char()
      if(char == '\\'):
        string += char
        if(self.__has_next_column()):
          self.__next_column()
          char = self.__get_char()
          if(RE_SIMBOL.match(char) or char == '\"'):
            string += char
            self.__next_column()
          elif(char == '\n'):
            self.__next_column()
            invalid_string = True
          else:
            string += char
            self.__next_column()
            invalid_string = True
        else:
          error = Token(string_line, "CMF", string)
          self.errors.append(error)
          self.__next_column()
          return
      elif(char == '\"'):
        string += char
        if(invalid_string):
          error = Token(string_line, "CMF", string)
          self.errors.append(error)
        else:
          token = Token(string_line, "CAD", string)
          self.tokens.append(token)
        self.__next_column()
        return
      elif(char == '\n'):
        self.__next_column()
        invalid_string = True
      elif(RE_SIMBOL.match(char)):
        string += char
        self.__next_column()
      else:
        string += char
        self.__next_column()
        invalid_string = True
    error = Token(string_line, "CMF", string)
    self.errors.append(error)

  """
  Função que identifica operadores lógicos.
  Padrão: && || !
  Caso seja encontrado apenas um & ou | é gerado erro de operador mal formado.
  """
  def __logical_operator(self, char):
    operator = char
    if(self.__has_next_column()):
      self.__next_column()
      next_char = self.__get_char()
      if(char == '!'):
        if(next_char != '='):
          token = Token(self.line_index+1, "LOG", operator)
          self.tokens.append(token)
        else:
          operator += next_char
          token = Token(self.line_index+1, "REL", operator)
          self.tokens.append(token)
          self.__next_column()
      elif(char == next_char):
        operator += next_char
        token = Token(self.line_index+1, "LOG", operator)
        self.tokens.append(token)
        self.__next_column()
      else:
        error = Token(self.line_index+1, "OpMF", operator)
        self.errors.append(error)
    else:
      token = Token(self.line_index+1, "LOG", operator)
      self.tokens.append(token)
      self.__next_column()
  
  """
  Função que identifica operadores aritméticos.
  Padrão: +  -  *  /  ++  --
  """
  def __arithmetic_operator(self, char):
    if(char == '+'):
      operator = '+'
      if(self.__has_next_column()):
        self.__next_column()
        char = self.__get_char()
        if(char == '+'):
          operator = '++'
          self.__next_column()
      else:
        self.__next_column()
      token = Token(self.line_index+1, "ART", operator)
      self.tokens.append(token)
    elif(char == '-'):
      operator = '-'
      if(self.__has_next_column()):
        self.__next_column()
        char = self.__get_char()
        if(char == '-'):
          operator = '--'
          self.__next_column()
      else:
        self.__next_column()
      token = Token(self.line_index+1, "ART", operator)
      self.tokens.append(token)
    else:
      operator = char
      token = Token(self.line_index+1, "ART", operator)
      self.tokens.append(token)
      self.__next_column()

  """
  Função que identifica delimitadores.
  Padrão: ;  , ( )  { }  [ ] .
  """
  def __delimiter(self, char):
    token = Token(self.line_index+1, "DEL", char)
    self.tokens.append(token)
    self.__next_column()

  """
  Função que identifica números.
  Padrão: Dígito+(.Dígito+)?
  Caso haja um '.' que não seja seguido por um dígito é gerado um erro de
  número mal formado.
  """
  def __number(self, char):
    number = char
    self.__next_column()
    while (self.column_index < len(self.source_code[self.line_index])):
      char = self.__get_char()
      if(char in DIGITS):
        number += char
        self.__next_column()
      elif(char == '.'):
        number += char
        if(self.__has_next_column()):
          self.__next_column()
          char = self.__get_char()
          if(char in DIGITS):
            while (self.column_index < len(self.source_code[self.line_index])):
              char = self.__get_char()
              if(char in DIGITS):
                number += char
                self.__next_column()
              else:
                token = Token(self.line_index+1, "NRO", number)
                self.tokens.append(token)
                return
          else:
            error = Token(self.line_index+1, "NMF", number)
            self.errors.append(error)
            return
        else:
          error = Token(self.line_index+1, "NMF", number)
          self.errors.append(error)
          return
      else:
        token = Token(self.line_index+1, "NRO", number)
        self.tokens.append(token)
        return
    token = Token(self.line_index+1, "NRO", number)
    self.tokens.append(token)
    return

  """
  Função que identifica operadores relacionais.
  Padrão: ==  !=  >  >=  <  <=  = 
  """
  def __relational_operator(self, char):
    self.__next_column()
    next_char = self.__get_char()
    if(next_char == '='):
      operator = char+next_char
      self.__next_column()
    else:
      operator = char
    token = Token(self.line_index+1, "REL", operator)
    self.tokens.append(token)

  """
  Função que inicia a análise lexica, percorrendo todas as linhas do arquivo
  caractere a caractere.
  """
  def analyze(self):
    while (self.line_index < len(self.source_code)):
      while (self.column_index < len(self.source_code[self.line_index])):
        char = self.__get_char()
        if(char in IGNORE):
          self.__next_column()
        elif(char in DELIMITERS):
          self.__delimiter(char)
        elif(char == '/'):
          if(self.__has_next_column()):
            self.__next_column()
            next_char = self.__get_char()
            if(next_char == '/'):
              break # Comentário de linha
            elif(next_char == '*'):
              closed = self.__multiline_comment() # Comentário de bloco
              if(not closed):
                return
            else:
              token = Token(self.line_index+1, "ART", char)
              self.tokens.append(token)
          else:
            token = Token(self.line_index+1, "ART", char)
            self.tokens.append(token)
            self.__next_column()
        elif(char in DIGITS):
          self.__number(char)
        elif(char in ARITHMETIC_OPERATORS):
          self.__arithmetic_operator(char)
        elif(char in LOGICAL_OPERATORS):
          self.__logical_operator(char)
        elif(char in RELATIONAL_OPERATORS):
          self.__relational_operator(char)
        elif(char == '\"'):
          self.__string()
        elif(RE_LETTER.match(char)):
          self.__identifier_or_reserved_word()
        else:
          error = Token(self.line_index+1, "SIB", char)
          self.errors.append(error)
          self.__next_column()
      self.__next_line()
    return self.tokens
  
  """
  Função para escrever os tokens identificados durante análise léxica
  no arquivo de saída fornecido por parâmetro.
  """
  def write_tokens(self, output):
    for token in self.tokens:
      output.write(token.__str__()+'\n')

  """
  Função para escrever os erros identificados durante análise léxica
  no arquivo de saída fornecido por parâmetro.
  """
  def write_errors(self, output):
    output.write('\n')
    if(self.errors):
      for error in self.errors:
        output.write(error.__str__()+'\n')
      output.write('----------------------------\n')
      if(len(self.errors) == 1):
        output.write('1 lexical error found.')
        print('-> 1 lexical error found.')
      else:
        output.write(str(len(self.errors))+' lexical errors found.')
        print('-> '+str(len(self.errors))+' lexical errors found.')
    else:
      print('-> Successful lexical analysis! No errors found.') 

  """
  Função que retorna o número de erros léxicos identificados
  """
  def get_errors(self):
    return len(self.errors)

  """
  Avança para a próxima linha do arquivo.
  """
  def __next_line(self):
    self.line_index += 1
    self.column_index = 0
  
  """
  Avança para o próximo caractere da linha.
  """
  def __next_column(self):
    self.column_index += 1

  """
  Verifica se ainda há caracteres na linha.
  """
  def __has_next_column(self):
    return self.column_index+1 < len(self.source_code[self.line_index])

  """
  Retorna o caractere da posição atual.
  """
  def __get_char(self):
    return self.source_code[self.line_index][self.column_index]