"""
 Código de um analisador sintático, desenvolvido como solução do Problema 3
 do MI-Processadores de Linguagem de Programação.
 Autor: Iago Machado da Conceição Silva
"""
from token import Token

class Parser:

  def __init__(self, tokens, output):
    self.output = output
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

  # Função para tratamento de erro pelo método do pânico
  def __error(self, expected, sinc_tokens):
    self.errors += 1
    token = self.__token()
    if(token != None):
      self.output.write('{} Syntax error: expected {} but found \'{}\'\n'.format(token.line, expected, token.value))
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
      self.output.write(' Syntax error: Unexpected end of file. Expected {} but found None\n'.format(expected))
      print('-> Syntax error: Unexpected end of file. Expected {} but found None'.format(expected))

  # Função para o tratamento de erro pelo método de correção local
  def __local_fix(self, expected):
    token = self.__token()
    if(token != None):
      self.output.write('{} Syntax error: expected {} but found \'{}\'\n'.format(token.line, expected, token.value))
      print('-> Syntax error - line {}: expected {} but found \'{}\''.format(token.line, expected, token.value))
    else:
      self.output.write(' Syntax error: Unexpected end of file. Expected {} but found None\n'.format(expected))
      print('-> Syntax error: Unexpected end of file. Expected {} but found None'.format(expected))

  def __args_list(self):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      self.__exp()
      self.__args_list()

  def __args(self):
    token = self.__token()
    if(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
      self.__exp()
      self.__args_list()


  def __id_value(self):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__args()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
      else:
        self.__error('\')\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
    elif(token != None and token.value == '['):
      self.__next_token()
      self.__arrays()
    self.__accesses()

  def __value(self):
    token = self.__token()
    if(token != None and token.value == '-'):
      self.__next_token()
      self.__value()
    elif(token != None and (token.key == 'NRO' or token.key == 'CAD' or token.value == 'true' or token.value == 'false')):
      self.__next_token()
    elif(token != None and (token.value == 'local' or token.value == 'global')):
      self.__next_token()
      self.__access()
      self.__accesses()
    elif(token != None and token.key == 'IDE'):
      self.__next_token()
      self.__id_value()
    elif(token != None and token.value == '('):
      self.__next_token()
      self.__exp()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
      else:
        self.__error('\')\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
    else:
      self.__error('\'(\', IDENTIFIER, STRING, NUMBER, \'true\', \'false\', \'global\' or \'local\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
  
  def __unary(self):
    token = self.__token()
    if(token != None and token.value == '!'):
      self.__next_token()
      self.__unary()
    else:
      self.__value()
  
  def __mult_aux(self):
    token = self.__token()
    if(token != None and (token.value == '*' or token.value == '/')):
      self.__next_token()
      self.__unary()
      self.__mult_aux()

  def __mult(self):
    self.__unary()
    self.__mult_aux()  
  
  def __add_aux(self):
    token = self.__token()
    if(token != None and (token.value == '+' or token.value == '-')):
      self.__next_token()
      self.__mult()
      self.__add_aux()

  def __add(self):
    self.__mult()
    self.__add_aux()

  def __compare_aux(self):
    token = self.__token()
    if(token != None and (token.value == '<' or token.value == '>' or token.value == '<=' or token.value == '>=')):
      self.__next_token()
      self.__add()
      self.__compare_aux()

  def __compare(self):
    self.__add()
    self.__compare_aux()
  
  def __equate_aux(self):
    token = self.__token()
    if(token != None and (token.value == '==' or token.value == '!=')):
      self.__next_token()
      self.__compare()
      self.__equate_aux()

  def __equate(self):
    self.__compare()
    self.__equate_aux()
  
  def __and_aux(self):
    token = self.__token()
    if(token != None and token.value == '&&'):
      self.__next_token()
      self.__equate()
      self.__and_aux()

  def __and(self):
    self.__equate()
    self.__and_aux()

  def __or(self):
    token = self.__token()
    if(token != None and token.value == '||'):
      self.__next_token()
      self.__and()
      self.__or()  
  
  def __exp(self):
    self.__and()
    self.__or()

  def __log_value(self):
    token = self.__token()
    if(token != None and (token.key == 'NRO' or token.key == 'CAD' or token.value == 'true' or token.value == 'false')):
      self.__next_token()
    elif(token != None and (token.value == 'local' or token.value == 'global')):
      self.__next_token()
      self.__access()
      self.__accesses()
    elif(token != None and token.key == 'IDE'):
      self.__next_token()
      self.__id_value()
    elif(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
      else:
        self.__error('\')\'', ['!=', '==', '&&', '||', '>', '<', '>=', '<=', ')'])
    else:
      self.__error('\'(\', IDENTIFIER, NUMBER, STRING, \'true\', \'false\', \'global\' or \'local\'', ['!=', '==', '&&', '||', '>', '<', '>=', '<=', ')'])

  def __log_unary(self):
    token = self.__token()
    if(token != None and token.value == '!'):
      self.__next_token()
      self.__log_unary()
    else:
      self.__log_value()

  def __log_compare_aux(self):
    token = self.__token()
    if(token != None and (token.value == '<' or token.value == '>' or token.value == '<=' or token.value == '>=')):
      self.__next_token()
      self.__log_unary()
      self.__log_compare_aux()

  def __log_compare(self):
    self.__log_unary()
    self.__log_compare_aux()

  def __log_equate_aux(self):
    token = self.__token()
    if(token != None and (token.value == '==' or token.value == '!=')):
      self.__next_token()
      self.__log_compare()
      self.__log_equate_aux()

  def __log_equate(self):
    self.__log_compare()
    self.__log_equate_aux()

  def __log_and_aux(self):
    token = self.__token()
    if(token != None and token.value == '&&'):
      self.__next_token()
      self.__log_equate()
      self.__log_and_aux()

  def __log_and(self):
    self.__log_equate()
    self.__log_and_aux()

  def __log_or(self):
    token = self.__token()
    if(token != None and token.value == '||'):
      self.__next_token()
      self.__log_and()
      self.__log_or()

  def __log_exp(self):
    self.__log_and()
    self.__log_or()
    
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
    if(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
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
        elif(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
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
    else:
      self.__local_fix('\'{\'')
    self.__const_decls()
    token = self.__token()
    if(token != None and token.value == '}'):
      self.__next_token()
    else:
      self.__error('\'}\'', ['var', 'function', 'procedure', 'struct', 'typedef'])

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
      elif(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
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
    else:
      self.__local_fix('\'{\'')
    self.__var_decls()
    token = self.__token()
    if(token.value == '}'):
      self.__next_token()
    else:
      self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start', 'if', 'while', 'print', 'read', 'global', 'local', 'identifier'])


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

  def __param_mult_arrays(self):
    token = self.__token()
    if(token != None and token.value == '['):
      self.__next_token()
      token = self.__token()
      if(token != None and token.key == 'NRO'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == ']'):
          self.__next_token()
          self.__param_mult_arrays()
        else:
          self.__error('\']\'', [',', ')'])
      else:
        self.__error('NUMBER', [',', ')'])

  def __param_arrays(self):
    token = self.__token()
    if(token != None and token.value == '['):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == ']'):
        self.__next_token()
        self.__param_mult_arrays()
      else:
        self.__error('\']\'', [',', ')'])

  def __params_list(self):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      is_type = self.__type()
      if(is_type):
        token = self.__token()
        if(token != None and token.key == 'IDE'):
          self.__next_token()
          self.__param_arrays()
          self.__params_list()
        else:
          self.__error('IDENTIFIER', [',', ')'])
      else:
        self.__error('\'int\', \'real\', \'boolean\', \'string\', \'struct\' or IDENTIFIER', [',', ')'])

  def __params(self):
    is_type = self.__type()
    if(is_type):
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.__next_token()
        self.__param_arrays()
        self.__params_list()
      else:
        self.__error('IDENTIFIER', [')'])

  def __else_stm(self):
    token = self.__token()
    if(token != None and token.value == 'else'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '{'):
        self.__next_token()
      else:
        self.__local_fix('\'{\'')
      self.__func_stms()
      token = self.__token()
      if(token != None and token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

  def __if_stm(self):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == 'then'):
          self.__next_token()
          token = self.__token()
          if(token != None and token.value == '{'):
            self.__next_token()
          else:
            self.__local_fix('\'{\'')
          self.__func_stms()
          token = self.__token()
          if(token != None and token.value == '}'):
            self.__next_token()
            self.__else_stm()
          else:
            self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
        else:
          self.__error('\'then\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

  def __while_stm(self):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
        else:
          self.__local_fix('\'{\'')
        self.__func_stms()
        token = self.__token()
        if(token != None and token.value == '}'):
          self.__next_token()
        else:
          self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
  
  def __else_proc_stm(self):
    token = self.__token()
    if(token != None and token.value == 'else'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '{'):
        self.__next_token()
      else:
        self.__local_fix('\'{\'')
      self.__proc_stms()
      token = self.__token()
      if(token != None and token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])

  def __if_proc_stm(self):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == 'then'):
          self.__next_token()
          token = self.__token()
          if(token != None and token.value == '{'):
            self.__next_token()
          else:
            self.__local_fix('\'{\'')
          self.__proc_stms()
          token = self.__token()
          if(token != None and token.value == '}'):
            self.__next_token()
            self.__else_proc_stm()
          else:
            self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
        else:
          self.__error('\'then\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])

  def __while_proc_stm(self):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
        else:
          self.__local_fix('\'{\'')
        self.__proc_stms()
        token = self.__token()
        if(token != None and token.value == '}'):
          self.__next_token()
        else:
          self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])

  def __access(self):
    token = self.__token()
    if(token != None and token.value == '.'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '['):
          self.__next_token()
          self.__arrays()
      else:
        self.__error('IDENTIFIER', ['.', '=', '++', '--', ';'])
    else:
      self.__error('\'.\'', ['.', '=', '++', '--', ';'])
        
  def __accesses(self):
    token = self.__token()
    if(token != None and token.value == '.'):
      self.__access()
      self.__accesses()

  def __assign(self):
    token = self.__token()
    if(token != None and token.value == '='):
      self.__next_token()
      self.__exp()
      token = self.__token()
      if(token != None and token.value == ';'):
        self.__next_token()
      else:
        self.__error(';', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    elif(token != None and token.value == '++'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == ';'):
        self.__next_token()
      else:
        self.__error(';', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    elif(token != None and token.value == '--'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == ';'):
        self.__next_token()
      else:
        self.__error(';', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'=\', \'++\' or \'--\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    
  def __stm_id(self):
    token = self.__token()
    if(token != None and (token.value == '=' or token.value == '++' or token.value == '--')):
      self.__assign()
    elif(token != None and token.value == '['):
      self.__next_token()
      self.__arrays()
      self.__accesses()
      self.__assign()
    elif(token != None and token.value == '.'):
      self.__access()
      self.__accesses()
      self.__assign()
    elif(token != None and token.value == '('):
      self.__next_token()
      self.__args()
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == ';'):
          self.__next_token()
        else:
          self.__error('\';\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'=\', \'++\', \'--\', \'[\', \'.\' or \'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

     

  def __var_stm(self):
    token = self.__token()
    if(token != None and (token.value == 'local' or token.value == 'global')):
      self.__next_token()
      self.__access()
      self.__accesses()
      self.__assign()
    elif(token != None and token.key == 'IDE'):
      self.__next_token()
      self.__stm_id()
    elif(token != None and (token.value == 'print' or token.value == 'read')):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '('):
        self.__next_token()
        self.__args()
        token = self.__token()
        if(token != None and token.value == ')'):
          self.__next_token()
          token = self.__token()
          if(token != None and token.value == ';'):
            self.__next_token()
          else:
            self.__error('\';\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
        else:
          self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
      else:
        self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'local\', \'global\', IDENTIFIER, \'print\' or \'read\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

  def __proc_stms(self):
    token = self.__token()
    if(token != None and token.value == 'if'):
      self.__next_token()
      self.__if_proc_stm()
      self.__proc_stms()
    elif(token != None and token.value == 'while'):
      self.__next_token()
      self.__while_proc_stm()
      self.__proc_stms()
    elif(token != None and (token.key == 'IDE' or token.value == 'local' or token.value == 'global' or token.value == 'print' or token.value == 'read')):
      self.__var_stm()
      self.__proc_stms()

  def __proc_block(self):
    token = self.__token()
    if(token != None and token.value == '{'):
      self.__next_token()
      token = self.__token()
    else:
      self.__local_fix('\'{\'')
    if(token != None and token.value == 'var'):
      self.__next_token()
      self.__var_block()
    self.__proc_stms()
    token = self.__token()
    if(token != None and token.value == '}'):
      self.__next_token()
    else:
      self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start'])    

  def __func_stms(self):
    token = self.__token()
    if(token != None and token.value == 'if'):
      self.__next_token()
      self.__if_stm()
      self.__func_stms()
    elif(token != None and token.value == 'while'):
      self.__next_token()
      self.__while_stm()
      self.__func_stms()
    elif(token != None and (token.key == 'IDE' or token.value == 'local' or token.value == 'global' or token.value == 'print' or token.value == 'read')):
      self.__var_stm()
      self.__func_stms()
    elif(token != None and token.value == 'return'):
      self.__next_token()
      self.__exp()
      token = self.__token()
      if(token != None and token.value == ';'):
        self.__next_token()
      else:
        self.__error('\';\'', ['}'])


  def __func_block(self):
    token = self.__token()
    if(token != None and token.value == '{'):
      self.__next_token()
      token = self.__token()
    else:
      self.__local_fix('\'{\'')
    if(token != None and token.value == 'var'):
      self.__next_token()
      self.__var_block()
    self.__func_stms()
    token = self.__token()
    if(token != None and token.value == '}'):
      self.__next_token()
    else:
      self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start'])


  def __func_decl(self):
    is_type = self.__type()
    if(is_type):
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '('):
          self.__next_token()
          self.__params()
          token = self.__token()
          if(token != None and token.value == ')'):
            self.__next_token()
            self.__func_block()
          else:
            self.__error('\')\'', ['function', 'procedure', 'struct', 'typedef', 'start'])
        else:
          self.__error('\'(\'', ['function', 'procedure', 'struct', 'typedef', 'start'])
      else:
        self.__error('IDENTIFIER', ['function', 'procedure', 'struct', 'typedef', 'start'])
    else:
      self.__error('\'int\', \'real\', \'boolean\', \'string\', \'struct\' or IDENTIFIER', ['function', 'procedure', 'struct', 'typedef', 'start'])
        
  def __proc_decl(self):
    token = self.__token()
    if(token != None and token.key == 'IDE'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '('):
        self.__next_token()
        self.__params()
        token = self.__token()
        if(token != None and token.value == ')'):
          self.__next_token()
          self.__proc_block()
        else:
          self.__error('\')\'', ['function', 'procedure', 'struct', 'typedef', 'start'])
      else:
        self.__error('\'(\'', ['function', 'procedure', 'struct', 'typedef', 'start'])
    else:
      self.__error('IDENTIFIER', ['function', 'procedure', 'struct', 'typedef', 'start'])

  def __extends(self):
    token = self.__token()
    if(token != None and token.value == 'extends'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == 'struct'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.key == 'IDE'):
          self.__next_token()
        else:
          self.__error('IDENTIFIER', ['{'])
      else:
        self.__error('\'struct\'', ['{'])
    
  
  def __struct_block(self):
    token = self.__token()
    if(token != None and token.value == 'struct'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.__next_token()
        self.__extends()
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
        else:
          self.__local_fix('\'{\'')
        self.__var_decls()
        token = self.__token()
        if(token != None and token.value == '}'):
          self.__next_token()
        else:
          self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start'])
      else:
        self.__error('IDENTIFIER', ['function', 'procedure', 'struct', 'typedef', 'start'])
    elif(token != None and token.value == 'typedef'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == 'struct'):
        self.__next_token()
        self.__extends()
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
        else:
          self.__local_fix('\'{\'')
        self.__var_decls()
        token = self.__token()
        if(token != None and token.value == '}'):
          self.__next_token()
          token = self.__token()
          if(token != None and token.key == 'IDE'):
            self.__next_token()
            token = self.__token()
            if(token != None and token.value == ';'):
              self.__next_token()
            else:
              self.__error('\';\'', ['function', 'procedure', 'struct', 'typedef', 'start'])
          else:
            self.__error('IDENTIFIER', ['function', 'procedure', 'struct', 'typedef', 'start'])
        else:
          self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start'])
      else:
        self.__error('\'struct\'', ['function', 'procedure', 'struct', 'typedef', 'start'])

  def __decls(self):
    token = self.__token()
    if(token != None and token.value == 'function'):
      self.__next_token()
      self.__func_decl()
      self.__decls()
    elif (token != None and token.value == 'procedure'):
      self.__next_token()
      self.__proc_decl()
      self.__decls()
    elif (token != None and (token.value == 'struct' or token.value == 'typedef')):
      self.__struct_block()
      self.__decls()

  def __start_block(self):
    token = self.__token()
    if(token != None and token.value == 'start'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '('):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == ')'):
          self.__next_token()
          self.__proc_block()
        else:
          self.__error('\')\'', ['function', 'procedure', 'struct', 'typedef'])
      else:
        self.__error('\'(\'', ['function', 'procedure', 'struct', 'typedef'])
    else:
      self.__error('\'start\'', ['function', 'procedure', 'struct', 'typedef'])

  def __program(self):
    self.__global_decl()
    self.__decls()
    self.__start_block()
    self.__decls()
        
  def run(self):
    token = self.__token()
    if(token == None):
      print('-> Syntax analysis failed. Empty file.')
    else:
      self.__program()
      self.output.write('----------------------------\n')
      self.output.write('Successful lexical analysis! No errors found.\n')
      if(self.errors == 0):
        self.output.write('Successful syntax analysis! No errors found.\n')
        print('-> Successful syntax analysis! No errors found.')
      else:
        if(self.errors == 1):
          self.output.write('Syntax analysis failed! 1 error found.\n')
          print('-> Syntax analysis failed! 1 error found.')
        else:
          self.output.write('Syntax analysis failed! {} errors found.\n'.format(self.errors))
          print('-> Syntax analysis failed! {} errors found.'.format(self.errors))
        
      
