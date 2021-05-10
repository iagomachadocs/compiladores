from token import Token


class Parser:

  def __init__(self, tokens):
    self.tokens = tokens
    if(len(tokens) == 0):
      self.current_token = None
    else:
      self.current_token = tokens[0]
    self.current_index = 0
    self.errors = 0

  def __next_token(self):
    self.current_index += 1
    if(self.current_index >= len(self.tokens)):
      self.current_token = None
    else:
      self.current_token = self.tokens[self.current_index]

  def __token(self):
    return self.current_token
  
  def __error(self, expected, sinc_tokens):
    self.errors += 1
    token = self.__token()
    if(token != None):
      print('-> Syntax error - line {}: expected {} but found \'{}\''.format(token.line, expected, token.value))
      is_sinc = False
      while(not is_sinc and token != None):
        for sinc_token in sinc_tokens:
          if(sinc_token == 'identifier' and token.key == 'IDE'):
            is_sinc = True
            return
          elif(sinc_token == token.value):
            is_sinc = True
            return

        if(not is_sinc):
          self.__next_token()
          token = self.__token()
    else:
      print('-> Syntax error: Unexpected end of file. Expected {} but found None'.format(expected))
    
  def __exp(self):
    token = self.__token()
    if(token != None and token.key == 'IDE'):
      self.__next_token()
    elif(token != None and token.key == 'NRO'):
      self.__next_token()
    

  def __type(self):
    token = self.__token()
    if(token != None and (token.value == 'int' or token.value == 'real' or token.value == 'boolean' or token.value == 'string')):
      self.__next_token()
      return True
    elif(token != None and token.key == 'IDE'):
      self.__next_token()
      return True
    elif(token != None and token.value == 'struct'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.__next_token()
        return True
      else:
        self.__error('IDENTIFIER', ['identifier'])
        return True
    return False

  def __typedef(self):
    token = self.__token()
    is_type = self.__type()
    if(is_type):
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == ';'):
          self.__next_token()
        else:
          self.__error('\';\'', ['}', 'int', 'real', 'boolean', 'string', 'typedef', 'struct'])
      else:
        self.__error('IDENTIFIER', ['}', 'int', 'real', 'boolean', 'string', 'typedef', 'struct'])
    else:
      self.__error('\'int\', \'real\', \'boolean\', \'string\', \'struct\' or IDENTIFIER', ['}', 'int', 'real', 'boolean', 'string', 'typedef', 'struct'])
      
  def __array_def(self):
    token = self.__token()
    if(token != None and (token.value in ['!', 'true', 'false', '('] or token.key in ['IDE', 'NRO', 'CAD'])):
      self.__exp()
      token = self.__token()
      if(token != None and token.value == ','):
        self.__next_token()
        self.__array_def()
    else:
      self.__error('\'!\', \'true\', \'false\', \'(\', IDENTIFIER, NUMBER or STRING', ['}'])
  
  def __array_decl(self):
    self.__array_def()
    token = self.__token()
    if(token != None and token.value == '}'):
      self.__next_token()
    else:
      self.__error('\',\' or \'}\'', [';'])
    

  def __arrays(self):
    token = self.__token()
    if(token != None and token.key == 'NRO' or token.key == 'IDE'):
      self.__next_token()
      token = self.__token()
    if(token != None and token.value == ']'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '['):
        self.__next_token()
        self.__arrays()
    else:
      self.__error('\']\'', ['=', ',', ';', '.', '>', '<', '>=', '<=', '==', '!=', '+', '-', '*', '/', '||', '&&'])

  def __const(self):
    token = self.__token()
    if(token != None and token.key == 'IDE'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '['):
        self.__next_token()
        self.__arrays()
      token = self.__token()
      if(token != None and token.value == '='):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
          self.__array_decl()
        elif(token != None and (token.value in ['!', 'true', 'false', '('] or token.key in ['IDE', 'NRO', 'CAD'])):
          self.__next_token()
          self.__exp()
        else:
          self.__error('\'{\', \'!\', \'true\', \'false\', \'(\', IDENTIFIER, STRING or NUMBER', [',', ';'])
      else:
        self.__error('\'=\'', [',', ';'])
    else:
      self.__error('IDENTIFIER', [',', ';'])

  def __const_list(self):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      self.__const()
      self.__const_list()
    elif(token != None and token.value == ';'):
      self.__next_token()
    else:
      self.__error('\',\' or \';\'', ['int', 'real', 'boolean', 'string', 'identifier', 'typedef', 'struct', '}'])
  
  def __const_decls(self):
    token = self.__token()
    is_type = self.__type()
    if(is_type):
      self.__const()
      self.__const_list()
      self.__const_decls()
    elif(token != None and token.value == 'typedef'):
      self.__next_token()
      self.__typedef()
      self.__const_decls()

  def __const_block(self):
    token = self.__token()
    if(token != None and token.value == '{'):
      self.__next_token()
      self.__const_decls()
      token = self.__token()
      if(token != None and token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', ['var', 'function', 'procedure', 'struct', 'typedef'])
    else:
      self.__error('\'{\'', ['var', 'function', 'procedure', 'struct', 'typedef'])

  def __var(self):
    token = self.__token()
    if(token != None and token.key == 'IDE'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '['):
        self.__next_token()
        self.__arrays()
    else:
      self.__error('IDENTIFIER', [',', ';', '='])

  def __var_list(self):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      self.__var()
      self.__var_list()
    elif(token != None and token.value == '='):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '{'):
        self.__next_token()
        self.__array_decl()
        self.__var_list()
      elif(token != None and (token.value in ['!', 'true', 'false', '('] or token.key in ['IDE', 'NRO', 'CAD'])):
        self.__next_token()
        self.__exp()
        self.__var_list()
      else:
        self.__error('\'{\', \'!\', \'true\', \'false\', \'(\', IDENTIFIER, STRING or NUMBER', ['int', 'real', 'boolean', 'string', 'identifier', 'typedef', 'struct', '}'])
    elif(token != None and token.value == ';'):
      self.__next_token()
    else:
      self.__error('\',\', \';\' or \'=\'', ['int', 'real', 'boolean', 'string', 'identifier', 'typedef', 'struct', '}'])


  def __var_decls(self):
    token = self.__token()
    is_type = self.__type()
    if(is_type):
      self.__var()
      self.__var_list()
      self.__var_decls()
    elif(token != None and token.value == 'typedef'):
      self.__next_token()
      self.__typedef()
      self.__var_decls()

  def __var_block(self):
    token = self.__token()
    if(token.value == '{'):
      self.__next_token()
      self.__var_decls()
      token = self.__token()
      if(token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start', 'if', 'while', 'print', 'read', 'global', 'local', 'identifier'])
    else:
      self.__error('\'{\'', ['function', 'procedure', 'struct', 'typedef', 'start', 'if', 'while', 'print', 'read', 'global', 'local', 'identifier'])


  def __global_decl(self):
    token = self.__token()
    if(token != None and token.value == 'const'):
      self.__next_token()
      self.__const_block()
      token = self.__token()
      if(token != None and token.value == 'var'):
        self.__next_token()
        self.__var_block()
    elif (token != None and token.value == 'var'):
      self.__next_token()
      self.__var_block()
      token = self.__token()
      if(token != None and token.value == 'const'):
        self.__next_token()
        self.__const_block()

  def run(self):
    token = self.__token()
    if(token == None):
      print('-> Sintax analysis failed. Empty file.')
    else:
      self.__global_decl()
      if(self.errors == 0):
        print('-> Successful sintax analysis! No errors found.')
      else:
        if(self.errors == 1):
          print('-> Sintax analysis failed! 1 error found.')
        else:
          print('-> Sintax analysis failed! {} errors found.'.format(self.errors))
        
      
