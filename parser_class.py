"""
 Código de um analisador sintático, desenvolvido como solução do Problema 3
 do MI-Processadores de Linguagem de Programação.
 Autor: Iago Machado da Conceição Silva
"""
from token_class import Token
from semantic_analyzer import SemanticAnalyzer

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
    self.semantic = SemanticAnalyzer(output)

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

  def __args_list(self, scope):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      self.__exp(scope)
      self.__args_list(scope)

  def __args(self, scope):
    token = self.__token()
    if(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
      self.__exp(scope)
      self.__args_list(scope)


  def __id_value(self, scope):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__args(scope)
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
      else:
        self.__error('\')\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
    elif(token != None and token.value == '['):
      self.__next_token()
      self.__arrays(scope)
    self.__accesses(scope)

  def __value(self, scope):
    token = self.__token()
    if(token != None and token.value == '-'):
      self.__next_token()
      self.__value(scope)
    elif(token != None and (token.key == 'NRO' or token.key == 'CAD' or token.value == 'true' or token.value == 'false')):
      self.__next_token()
    elif(token != None and (token.value == 'local' or token.value == 'global')):
      self.__next_token()
      self.__access(scope)
      self.__accesses(scope)
    elif(token != None and token.key == 'IDE'):
      self.__next_token()
      self.__id_value(scope)
    elif(token != None and token.value == '('):
      self.__next_token()
      self.__exp(scope)
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
      else:
        self.__error('\')\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
    else:
      self.__error('\'(\', IDENTIFIER, STRING, NUMBER, \'true\', \'false\', \'global\' or \'local\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
  
  def __unary(self, scope):
    token = self.__token()
    if(token != None and token.value == '!'):
      self.__next_token()
      self.__unary(scope)
    else:
      self.__value(scope)
  
  def __mult_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '*' or token.value == '/')):
      self.__next_token()
      self.__unary(scope)
      self.__mult_aux(scope)

  def __mult(self, scope):
    self.__unary(scope)
    self.__mult_aux(scope)  
  
  def __add_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '+' or token.value == '-')):
      self.__next_token()
      self.__mult(scope)
      self.__add_aux(scope)

  def __add(self, scope):
    self.__mult(scope)
    self.__add_aux(scope)

  def __compare_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '<' or token.value == '>' or token.value == '<=' or token.value == '>=')):
      self.__next_token()
      self.__add(scope)
      self.__compare_aux(scope)

  def __compare(self, scope):
    self.__add(scope)
    self.__compare_aux(scope)
  
  def __equate_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '==' or token.value == '!=')):
      self.__next_token()
      self.__compare(scope)
      self.__equate_aux(scope)

  def __equate(self, scope):
    self.__compare(scope)
    self.__equate_aux(scope)
  
  def __and_aux(self, scope):
    token = self.__token()
    if(token != None and token.value == '&&'):
      self.__next_token()
      self.__equate(scope)
      self.__and_aux(scope)

  def __and(self, scope):
    self.__equate(scope)
    self.__and_aux(scope)

  def __or(self, scope):
    token = self.__token()
    if(token != None and token.value == '||'):
      self.__next_token()
      self.__and(scope)
      self.__or(scope)  
  
  def __exp(self, scope):
    self.__and(scope)
    self.__or(scope)

  def __log_value(self, scope):
    token = self.__token()
    if(token != None and (token.key == 'NRO' or token.key == 'CAD' or token.value == 'true' or token.value == 'false')):
      self.__next_token()
    elif(token != None and (token.value == 'local' or token.value == 'global')):
      self.__next_token()
      self.__access(scope)
      self.__accesses(scope)
    elif(token != None and token.key == 'IDE'):
      self.__next_token()
      self.__id_value(scope)
    elif(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp(scope)
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
      else:
        self.__error('\')\'', ['!=', '==', '&&', '||', '>', '<', '>=', '<=', ')'])
    else:
      self.__error('\'(\', IDENTIFIER, NUMBER, STRING, \'true\', \'false\', \'global\' or \'local\'', ['!=', '==', '&&', '||', '>', '<', '>=', '<=', ')'])

  def __log_unary(self, scope):
    token = self.__token()
    if(token != None and token.value == '!'):
      self.__next_token()
      self.__log_unary(scope)
    else:
      self.__log_value(scope)

  def __log_compare_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '<' or token.value == '>' or token.value == '<=' or token.value == '>=')):
      self.__next_token()
      self.__log_unary(scope)
      self.__log_compare_aux(scope)

  def __log_compare(self, scope):
    self.__log_unary(scope)
    self.__log_compare_aux(scope)

  def __log_equate_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '==' or token.value == '!=')):
      self.__next_token()
      self.__log_compare(scope)
      self.__log_equate_aux(scope)

  def __log_equate(self, scope):
    self.__log_compare(scope)
    self.__log_equate_aux(scope)

  def __log_and_aux(self, scope):
    token = self.__token()
    if(token != None and token.value == '&&'):
      self.__next_token()
      self.__log_equate(scope)
      self.__log_and_aux(scope)

  def __log_and(self, scope):
    self.__log_equate(scope)
    self.__log_and_aux(scope)

  def __log_or(self, scope):
    token = self.__token()
    if(token != None and token.value == '||'):
      self.__next_token()
      self.__log_and(scope)
      self.__log_or(scope)

  def __log_exp(self, scope):
    self.__log_and(scope)
    self.__log_or(scope)
    
  def __type(self):
    token = self.__token()
    if(token != None and (token.value == 'int' or token.value == 'real' or token.value == 'boolean' or token.value == 'string')):
      self.__next_token()
      return token.value
    elif(token != None and token.key == 'IDE'):
      self.__next_token()
      return token.value
    elif(token != None and token.value == 'struct'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.__next_token()
        return 'struct '+token.value
      else:
        self.__error('IDENTIFIER', ['identifier'])
        return False
    return False

  def __typedef(self, scope):
    token = self.__token()
    typedef_type = self.__type()
    if(typedef_type != False):
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        typedef_token = token
        self.semantic.type_declaration(typedef_type, typedef_token, scope)
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
      
  def __array_def(self, scope):
    token = self.__token()
    if(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
      self.__exp(scope)
      token = self.__token()
      if(token != None and token.value == ','):
        self.__next_token()
        self.__array_def(scope)
    else:
      self.__error('\'!\', \'true\', \'false\', \'(\', IDENTIFIER, NUMBER or STRING', ['}'])
  
  def __array_decl(self):
    self.__array_def()
    token = self.__token()
    if(token != None and token.value == '}'):
      self.__next_token()
    else:
      self.__error('\',\' or \'}\'', [';'])
    

  def __arrays(self, scope):
    token = self.__token()
    if(token != None and token.key == 'NRO' or token.key == 'IDE'):
      self.semantic.array_index_type(token, scope)
      self.__next_token()
      token = self.__token()
    if(token != None and token.value == ']'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '['):
        self.__next_token()
        self.__arrays(scope)
    else:
      self.__error('\']\'', ['=', ',', ';', '.', '>', '<', '>=', '<=', '==', '!=', '+', '-', '*', '/', '||', '&&'])

  def __const(self, const_type):
    token = self.__token()
    if(token != None and token.key == 'IDE'):
      identifier_attributes = {'type': const_type, 'class': 'const'}
      identifier = token
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '['):
        identifier_attributes['array'] = True
        self.__next_token()
        self.__arrays('global')
      else:
        identifier_attributes['array'] = False
      token = self.__token()
      if(token != None and token.value == '='):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
          self.__array_decl()
        elif(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
          self.__exp('global')
          self.semantic.identifier_declaration(identifier, 'global', identifier_attributes)
        else:
          self.__error('\'{\', \'!\', \'true\', \'false\', \'(\', IDENTIFIER, STRING or NUMBER', [',', ';'])
      else:
        self.__error('\'=\'', [',', ';'])
    else:
      self.__error('IDENTIFIER', [',', ';'])

  def __const_list(self, const_type):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      self.__const(const_type)
      self.__const_list(const_type)
    elif(token != None and token.value == ';'):
      self.__next_token()
    else:
      self.__error('\',\' or \';\'', ['int', 'real', 'boolean', 'string', 'identifier', 'typedef', 'struct', '}'])
  
  def __const_decls(self):
    token = self.__token()
    const_type = self.__type()
    if(const_type != False):
      self.__const(const_type)
      self.__const_list(const_type)
      self.__const_decls()
    elif(token != None and token.value == 'typedef'):
      self.__next_token()
      self.__typedef('global')
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

  def __var(self, scope, var_type):
    token = self.__token()
    if(token != None and token.key == 'IDE'):
      identifier_attributes = {'type': var_type, 'class': 'var'}
      identifier = token
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '['):
        identifier_attributes['array'] = True
        self.__next_token()
        self.__arrays(scope)
      else:
        identifier_attributes['array'] = False
      self.semantic.identifier_declaration(identifier, scope, identifier_attributes)
    else:
      self.__error('IDENTIFIER', [',', ';', '='])

  def __var_list(self, scope, var_type):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      self.__var(scope, var_type)
      self.__var_list(scope, var_type)
    elif(token != None and token.value == '='):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '{'):
        self.__next_token()
        self.__array_decl()
        self.__var_list(scope, var_type)
      elif(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
        self.__exp(scope)
        self.__var_list(scope, var_type)
      else:
        self.__error('\'{\', \'!\', \'true\', \'false\', \'(\', IDENTIFIER, STRING or NUMBER', ['int', 'real', 'boolean', 'string', 'identifier', 'typedef', 'struct', '}'])
    elif(token != None and token.value == ';'):
      self.__next_token()
    else:
      self.__error('\',\', \';\' or \'=\'', ['int', 'real', 'boolean', 'string', 'identifier', 'typedef', 'struct', '}'])


  def __var_decls(self, scope):
    token = self.__token()
    var_type = self.__type()
    if(var_type != False):
      self.__var(scope, var_type)
      self.__var_list(scope, var_type)
      self.__var_decls(scope)
    elif(token != None and token.value == 'typedef'):
      self.__next_token()
      self.__typedef(scope)
      self.__var_decls(scope)

  def __var_block(self, scope):
    token = self.__token()
    if(token.value == '{'):
      self.__next_token()
    else:
      self.__local_fix('\'{\'')
    self.__var_decls(scope)
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
        self.__var_block('global')
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
        return True
      else:
        self.__error('\']\'', [',', ')'])
    return False

  def __params_list(self, params):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      param_type = self.__type()
      if(param_type):
        token = self.__token()
        if(token != None and token.key == 'IDE'):
          param_name = token.value
          self.__next_token()
          param_isarray = self.__param_arrays()
          param = {'name': param_name, 'type': param_type, 'array': param_isarray}
          params.append(param)
          params = self.__params_list(params)
        else:
          self.__error('IDENTIFIER', [',', ')'])
      else:
        self.__error('\'int\', \'real\', \'boolean\', \'string\', \'struct\' or IDENTIFIER', [',', ')'])
    return params

  def __params(self):
    params = []
    param_type = self.__type()
    if(param_type != False):
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        param_name = token.value
        self.__next_token()
        param_isarray = self.__param_arrays()
        param = {'name': param_name, 'type': param_type, 'array': param_isarray}
        params.append(param)
        self.__params_list(params)
      else:
        self.__error('IDENTIFIER', [')'])
    return params

  def __else_stm(self, scope):
    token = self.__token()
    if(token != None and token.value == 'else'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '{'):
        self.__next_token()
      else:
        self.__local_fix('\'{\'')
      self.__func_stms(scope)
      token = self.__token()
      if(token != None and token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

  def __if_stm(self, scope):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp(scope)
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
          self.__func_stms(scope)
          token = self.__token()
          if(token != None and token.value == '}'):
            self.__next_token()
            self.__else_stm(scope)
          else:
            self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
        else:
          self.__error('\'then\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

  def __while_stm(self, scope):
    token = self.__token()
    if(token != None and token.value == '('):
      self.__next_token()
      self.__log_exp(scope)
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
        else:
          self.__local_fix('\'{\'')
        self.__func_stms(scope)
        token = self.__token()
        if(token != None and token.value == '}'):
          self.__next_token()
        else:
          self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
  
  def __else_proc_stm(self, scope):
    token = self.__token()
    if(token != None and token.value == 'else'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '{'):
        self.__next_token()
      else:
        self.__local_fix('\'{\'')
      self.__proc_stms(scope)
      token = self.__token()
      if(token != None and token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])

  def __if_proc_stm(self, scope):
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
          self.__proc_stms(scope)
          token = self.__token()
          if(token != None and token.value == '}'):
            self.__next_token()
            self.__else_proc_stm(scope)
          else:
            self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
        else:
          self.__error('\'then\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])

  def __while_proc_stm(self, scope):
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
        self.__proc_stms(scope)
        token = self.__token()
        if(token != None and token.value == '}'):
          self.__next_token()
        else:
          self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', '}'])

  def __access(self, scope, scope_definition=None):
    token = self.__token()
    if(token != None and token.value == '.'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        self.semantic.check_const_assign(token, scope, scope_definition)
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '['):
          self.__next_token()
          self.__arrays(scope)
      else:
        self.__error('IDENTIFIER', ['.', '=', '++', '--', ';'])
    else:
      self.__error('\'.\'', ['.', '=', '++', '--', ';'])
        
  def __accesses(self, scope):
    token = self.__token()
    if(token != None and token.value == '.'):
      self.__access(scope)
      self.__accesses(scope)

  def __assign(self, scope):
    token = self.__token()
    if(token != None and token.value == '='):
      self.__next_token()
      self.__exp(scope)
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
    
  def __stm_id(self, scope, identifier):
    token = self.__token()
    if(token != None and (token.value == '=' or token.value == '++' or token.value == '--')):
      self.semantic.check_const_assign(identifier, scope)
      self.__assign(scope)
    elif(token != None and token.value == '['):
      self.__next_token()
      self.__arrays(scope)
      self.__accesses(scope)
      self.semantic.check_const_assign(identifier, scope)
      self.__assign(scope)
    elif(token != None and token.value == '.'):
      self.__access(scope)
      self.__accesses(scope)
      self.semantic.check_const_assign(identifier, scope)
      self.__assign(scope)
    elif(token != None and token.value == '('):
      self.__next_token()
      self.__args(scope)
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

     

  def __var_stm(self, scope):
    token = self.__token()
    if(token != None and (token.value == 'local' or token.value == 'global')):
      scope_definition = token.value
      self.__next_token()
      self.__access(scope, scope_definition)
      self.__accesses(scope)
      self.__assign(scope)
    elif(token != None and token.key == 'IDE'):
      identifier = token
      self.__next_token()
      self.__stm_id(scope, identifier)
    elif(token != None and (token.value == 'print' or token.value == 'read')):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '('):
        self.__next_token()
        self.__args(scope)
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

  def __proc_stms(self, scope):
    token = self.__token()
    if(token != None and token.value == 'if'):
      self.__next_token()
      self.__if_proc_stm(scope)
      self.__proc_stms(scope)
    elif(token != None and token.value == 'while'):
      self.__next_token()
      self.__while_proc_stm(scope)
      self.__proc_stms(scope)
    elif(token != None and (token.key == 'IDE' or token.value == 'local' or token.value == 'global' or token.value == 'print' or token.value == 'read')):
      self.__var_stm(scope)
      self.__proc_stms(scope)

  def __proc_block(self, scope):
    token = self.__token()
    if(token != None and token.value == '{'):
      self.__next_token()
      token = self.__token()
    else:
      self.__local_fix('\'{\'')
    if(token != None and token.value == 'var'):
      self.__next_token()
      self.__var_block(scope)
    self.__proc_stms(scope)
    token = self.__token()
    if(token != None and token.value == '}'):
      self.__next_token()
    else:
      self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start'])    

  def __func_stms(self, scope):
    token = self.__token()
    if(token != None and token.value == 'if'):
      self.__next_token()
      self.__if_stm()
      self.__func_stms(scope)
    elif(token != None and token.value == 'while'):
      self.__next_token()
      self.__while_stm()
      self.__func_stms(scope)
    elif(token != None and (token.key == 'IDE' or token.value == 'local' or token.value == 'global' or token.value == 'print' or token.value == 'read')):
      self.__var_stm(scope)
      self.__func_stms(scope)
    elif(token != None and token.value == 'return'):
      self.__next_token()
      self.__exp(scope)
      token = self.__token()
      if(token != None and token.value == ';'):
        self.__next_token()
      else:
        self.__error('\';\'', ['}'])


  def __func_block(self, scope):
    token = self.__token()
    if(token != None and token.value == '{'):
      self.__next_token()
      token = self.__token()
    else:
      self.__local_fix('\'{\'')
    if(token != None and token.value == 'var'):
      self.__next_token()
      self.__var_block(scope)
    self.__func_stms(scope)
    token = self.__token()
    if(token != None and token.value == '}'):
      self.__next_token()
    else:
      self.__error('\'}\'', ['function', 'procedure', 'struct', 'typedef', 'start'])


  def __func_decl(self):
    func_type = self.__type()
    if(func_type):
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        func = token
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '('):
          self.__next_token()
          params = self.__params()
          token = self.__token()
          if(token != None and token.value == ')'):
            name = self.semantic.function_declaration(func, func_type, params)
            self.__next_token()
            self.__func_block(name)
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
      proc = token
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '('):
        self.__next_token()
        params = self.__params()
        token = self.__token()
        if(token != None and token.value == ')'):
          name = self.semantic.procedure_declaration(proc, params)
          self.__next_token()
          self.__proc_block(name)
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
          return 'struct '+token.value
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
        struct_id = token
        self.__next_token()
        extends = self.__extends()
        scope = self.semantic.struct_declaration(struct_id, extends)
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
        else:
          self.__local_fix('\'{\'')
        self.__var_decls(scope)
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
        extends = self.__extends()
        scope = self.semantic.struct_declaration(Token(None, None, '_temp'), extends)
        token = self.__token()
        if(token != None and token.value == '{'):
          self.__next_token()
        else:
          self.__local_fix('\'{\'')
        self.__var_decls(scope)
        token = self.__token()
        if(token != None and token.value == '}'):
          self.__next_token()
          token = self.__token()
          if(token != None and token.key == 'IDE'):
            self.semantic.typedef_struct_declaration(token)
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
          self.__proc_block('start')
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
      print(self.semantic.scopes)
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
        
      
