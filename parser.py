from token import Token


class Parser:

  def __init__(self, tokens):
    self.tokens = tokens
    self.current_token = tokens[0]
    self.current_index = 0

  def __next_token(self):
    self.current_index += 1
    if(self.current_index >= len(self.tokens)):
      self.current_token = None
    else:
      self.current_token = self.tokens[self.current_index]

  def __token(self):
    return self.current_token
  
  def __error(self, expected, found, line):
    print('Syntax error - line {}: expected {} but found \'{}\''.format(line, expected, found))
    exit()

  def __type(self):
    token = self.__token()
    if(token.value == 'int' or token.value == 'real' or token.value == 'boolean' or token.value == 'string'):
      self.__next_token()
      return True
    elif(token.value == 'struct'):
      self.__next_token()
      token = self.__token()
      if(token.key == 'IDE'):
        self.__next_token()
        return True
      else:
        self.__error('IDENTIFIER', token.value, token.line)
    elif(token.key == 'IDE'):
      self.__next_token()
      return True
    return False

  def __value(self):
    token = self.__token()
    if(token.key == 'NRO'):
      self.__next_token()
    elif(token.value == 'true' or token.value == 'false'):
      self.__next_token()
    elif(token.key == 'CAD'):
      self.__next_token()
    else:
      self.__error('NUMBER, BOOLEAN or STRING', token.value, token.line)

  def __const(self):
    token = self.__token()
    if(token.key == 'IDE'):
      self.__next_token()
      token = self.__token()
      if(token.value == '='):
        self.__next_token()
        self.__value()
        token = self.__token()
        if(token.value == ','):
          self.__next_token()
          self.__const()
        elif(token.value == ';'):
          self.__next_token()
        else:
          self.__error('\',\' or \';\'', token.value, token.line)
      else:
        self.__error('\'=\'', token.value, token.line)
    else:
      self.__error('IDENTIFIER', token.value, token.line)

  
  def __const_list(self):
    is_type = self.__type()
    if(is_type):
      self.__const()
      self.__const_list()

  def __const_decl(self):
    token = self.__token()
    if(token.value == '{'):
      self.__next_token()
      self.__const_list()
      token = self.__token()
      if(token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', token.value, token.line)
    else:
      self.__error('\'{\'', token.value, token.line)

  def __variable(self):
    token = self.__token()
    if(token.key == 'IDE'):
      self.__next_token()
      token = self.__token()
      if(token.value == '='):
        self.__next_token()
        self.__value()
        token = self.__token()
        if(token.value == ','):
          self.__next_token()
          self.__variable()
        elif(token.value == ';'):
          self.__next_token()
        else:
          self.__error('\',\' or \';\'', token.value, token.line)
      elif(token.value == ','):
        self.__next_token()
        self.__variable()
      elif(token.value == ';'):
        self.__next_token()
      elif(token.value == '['):
        print('IMPLEMENTAR DECLARAÇÃO DE VETORES, LINHA 117')
        exit()
      else:
        self.__error('\'[\', \'=\', \',\' or \';\'', token.value, token.line)
    else:
      self.__error('IDENTIFIER', token.value, token.line)


  def __var_list(self):
    is_type = self.__type()
    if(is_type):
      self.__variable()
      self.__var_list()

  def __var_decl(self):
    token = self.__token()
    if(token.value == '{'):
      self.__next_token()
      self.__var_list()
      token = self.__token()
      if(token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', token.value, token.line)
    else:
      self.__error('\'{\'', token.value, token.line)


  def __global_decl(self):
    token = self.__token()
    if(token.value == 'const'):
      self.__next_token()
      self.__const_decl()
      token = self.__token()
      if(token != None and token.value == 'var'):
        self.__next_token()
        self.__var_decl()
    elif (token.value == 'var'):
      self.__next_token()
      self.__var_decl()
      token = self.__token()
      if(token != None and token.value == 'const'):
        self.__next_token()
        self.__const_decl()

  def run(self):
    token = self.__token()
    if(token == None):
      print('-> Sintax analysis failed. Empty file.')
    else:
      self.__global_decl()
      print('-> Successful sintax analysis! No errors found.')
