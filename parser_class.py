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

  def __args_list(self, scope, args_list=[]):
    token = self.__token()
    if(token != None and token.value == ','):
      self.__next_token()
      arg_type = self.__exp(scope)
      args_list.append(arg_type)
      return self.__args_list(scope, args_list)
    return args_list

  def __args(self, scope, args_list=[]):
    token = self.__token()
    if(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
      arg_type = self.__exp(scope)
      args_list.append(arg_type)
      return self.__args_list(scope, args_list)
    return args_list


  def __id_value(self, scope, identifier):
    identifier_access = {'token': identifier}
    function_call = False
    token = self.__token()
    if(token != None and token.value == '('):
      function_call = True
      self.__next_token()
      args_list = self.__args(scope, [])
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        func_type = self.semantic.function_call(identifier, args_list)
      else:
        self.__error('\')\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
    elif(token != None and token.value == '['):
      self.__next_token()
      self.__arrays(scope)
      identifier_access['array'] = True
    else:
      identifier_access['array'] = False
    accesses = self.__accesses(scope, [])
    if(not function_call):
      return self.semantic.check_accesses(scope, identifier_access, accesses)
    else:
      return func_type

  def __value(self, scope):
    token = self.__token()
    id_type = None
    if(token != None and token.value == '-'):
      token_aux = token
      self.__next_token()
      id_type = self.__value(scope)
      if(not (id_type == 'int' or id_type == 'real') and id_type != None):
        self.semantic.error('invalid operation', token_aux.line, id_type)
        id_type = None
    elif(token != None and (token.key == 'NRO' or token.key == 'CAD' or token.value == 'true' or token.value == 'false')):
      if(token.key == 'NRO'):
        id_type = self.semantic.int_or_real(token)
      elif(token.key == 'CAD'):
        id_type = 'string'
      else:
        id_type = 'boolean'
      self.__next_token()
    elif(token != None and (token.value == 'local' or token.value == 'global')):
      scope_definition = token.value
      self.__next_token()
      first_access = self.__access(scope, []) 
      accesses = self.__accesses(scope, [])
      if(len(first_access) > 0):
        identifier = first_access[0]
        id_type = self.semantic.check_accesses(scope, identifier, accesses, scope_definition)
    elif(token != None and token.key == 'IDE'):
      identifier = token
      self.__next_token()
      id_type = self.__id_value(scope, identifier)
    elif(token != None and token.value == '('):
      self.__next_token()
      id_type = self.__exp(scope)
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
      else:
        self.__error('\')\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
    else:
      self.__error('\'(\', IDENTIFIER, STRING, NUMBER, \'true\', \'false\', \'global\' or \'local\'', ['*', '/', '+', '-', '>', '<', '<=', '>=', '==', '!=', '&&', '||', '}', ']', ')', ',', ';'])
    return id_type
  
  def __unary(self, scope):
    token = self.__token()
    if(token != None and token.value == '!'):
      token_aux = token
      self.__next_token()
      id_type = self.__unary(scope)
      if(id_type != 'boolean' and id_type != None):
        self.semantic.error('invalid operation', token_aux.line, id_type)
        id_type = None
    else:
      id_type = self.__value(scope)
    return id_type
  
  def __mult_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '*' or token.value == '/')):
      self.__next_token()
      type_unary = self.__unary(scope)
      type_mult = self.__mult_aux(scope)
      id_type = self.semantic.check_numbers(type_unary, type_mult, token.line)
      return id_type
    return None

  def __mult(self, scope):
    line = self.__token().line
    type_unary = self.__unary(scope)
    type_mult = self.__mult_aux(scope)
    if(type_mult == None):
      return type_unary
    else:
      return self.semantic.check_numbers(type_unary, type_mult, line)
  
  def __add_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '+' or token.value == '-')):
      self.__next_token()
      type_mult = self.__mult(scope)
      type_add = self.__add_aux(scope)
      id_type = self.semantic.check_numbers(type_mult, type_add, token.line)
      return id_type
    return None

  def __add(self, scope):
    line = self.__token().line
    type_mult = self.__mult(scope)
    type_add = self.__add_aux(scope)
    if(type_add == None):
      return type_mult
    else:
      return self.semantic.check_numbers(type_mult, type_add, line)

  def __compare_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '<' or token.value == '>' or token.value == '<=' or token.value == '>=')):
      self.__next_token()
      type_add = self.__add(scope)
      type_compare = self.__compare_aux(scope)
      id_type = self.semantic.check_numbers(type_add, type_compare, token.line)
      return id_type
    return None

  def __compare(self, scope):
    line = self.__token().line
    type_add = self.__add(scope)
    type_compare = self.__compare_aux(scope)
    if(type_compare == None):
      return type_add
    elif(type_add == None):
      return None
    else:
      id_type = self.semantic.check_numbers(type_add, type_compare, line)
      if(id_type != None):
        return 'boolean'
      return None
  
  def __equate_aux(self, scope):
    token = self.__token()
    if(token != None and (token.value == '==' or token.value == '!=')):
      self.__next_token()
      type_compare = self.__compare(scope)
      type_equate = self.__equate_aux(scope)
      if(type_equate == None):
        return type_compare
      elif(type_compare == None):
        return None
      else:
        return 'boolean'
    return None

  def __equate(self, scope):
    type_compare = self.__compare(scope)
    type_equate = self.__equate_aux(scope)
    if(type_equate == None):
      return type_compare
    elif(type_compare == None):
      return None
    else:
      return 'boolean'

  def __and_aux(self, scope):
    token = self.__token()
    if(token != None and token.value == '&&'):
      line = token.line
      self.__next_token()
      type_equate = self.__equate(scope)
      type_and = self.__and_aux(scope)
      return self.semantic.check_boolean(type_equate, type_and, line)
    return None

  def __and(self, scope):
    line = self.__token().line
    type_equate = self.__equate(scope)
    type_and = self.__and_aux(scope)
    return self.semantic.check_boolean(type_equate, type_and, line)

  def __or(self, scope):
    token = self.__token()
    if(token != None and token.value == '||'):
      self.__next_token()
      type_and = self.__and(scope)
      type_or = self.__or(scope)
      return self.semantic.check_boolean(type_and, type_or, token.line)
    return None
  
  def __exp(self, scope):
    line = self.__token().line
    type_and = self.__and(scope)
    type_or = self.__or(scope)
    return self.semantic.check_boolean(type_and, type_or, line)

  def __log_value(self, scope):
    token = self.__token()
    if(token != None and (token.key == 'NRO' or token.key == 'CAD' or token.value == 'true' or token.value == 'false')):
      self.__next_token()
    elif(token != None and (token.value == 'local' or token.value == 'global')):
      self.__next_token()
      self.__access(scope)
      self.__accesses(scope)
    elif(token != None and token.key == 'IDE'):
      identifier = token
      self.__next_token()
      self.__id_value(scope, identifier)
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
        type_assigned = None
        if(token != None and token.value == '{'):
          self.__next_token()
          self.__array_decl()
        elif(token != None and (token.value in ['!', 'true', 'false', '(', 'global', 'local'] or token.key in ['IDE', 'NRO', 'CAD'])):
          type_assigned = self.__exp('global')
          self.semantic.identifier_declaration(identifier, 'global', identifier_attributes)
          self.semantic.compare_types(const_type, type_assigned, token.line)
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
        type_assigned = self.__exp(scope)
        self.semantic.compare_types(var_type, type_assigned, token.line)
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
      self.__var_block('global')
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

  def __else_stm(self, scope, func_type):
    token = self.__token()
    if(token != None and token.value == 'else'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '{'):
        self.__next_token()
      else:
        self.__local_fix('\'{\'')
      self.__func_stms(scope, func_type)
      token = self.__token()
      if(token != None and token.value == '}'):
        self.__next_token()
      else:
        self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

  def __if_stm(self, scope, func_type):
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
          self.__func_stms(scope, func_type)
          token = self.__token()
          if(token != None and token.value == '}'):
            self.__next_token()
            self.__else_stm(scope, func_type)
          else:
            self.__error('\'}\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
        else:
          self.__error('\'then\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
      else:
        self.__error('\')\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])
    else:
      self.__error('\'(\'', ['if', 'while', 'print', 'read', 'global', 'local', 'identifier', 'return', '}'])

  def __while_stm(self, scope, func_type):
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
        self.__func_stms(scope, func_type)
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
      self.__log_exp(scope)
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

  def __access(self, scope, accesses):
    token = self.__token()
    if(token != None and token.value == '.'):
      self.__next_token()
      token = self.__token()
      if(token != None and token.key == 'IDE'):
        identifier = {'token': token}
        self.__next_token()
        token = self.__token()
        if(token != None and token.value == '['):
          identifier['array'] = True
          self.__next_token()
          self.__arrays(scope)
        else:
          identifier['array'] = False
        accesses.append(identifier)
      else:
        self.__error('IDENTIFIER', ['.', '=', '++', '--', ';'])
    else:
      self.__error('\'.\'', ['.', '=', '++', '--', ';'])
    return accesses
        
  def __accesses(self, scope, accesses):
    token = self.__token()
    if(token != None and token.value == '.'):
      accesses = self.__access(scope, accesses)
      accesses = self.__accesses(scope, accesses)
    return accesses

  def __assign(self, scope, type_expected):
    token = self.__token()
    if(token != None and token.value == '='):
      self.__next_token()
      type_assigned = self.__exp(scope)
      self.semantic.compare_types(type_expected, type_assigned, token.line)
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
      identifier_access = {'token': identifier, 'array': False }
      id_type = self.semantic.check_accesses(scope, identifier_access, [])  
      self.__assign(scope, id_type)
    elif(token != None and token.value == '['):
      self.__next_token()
      self.__arrays(scope)
      identifier_access = {'token': identifier, 'array': True }
      accesses = self.__accesses(scope, [])
      self.semantic.check_const_assign(identifier, scope)
      id_type = self.semantic.check_accesses(scope, identifier_access, accesses)
      self.__assign(scope, id_type)
    elif(token != None and token.value == '.'):
      identifier_access = {'token': identifier, 'array': False}
      accesses = self.__access(scope, [])
      accesses = self.__accesses(scope, accesses)
      self.semantic.check_const_assign(identifier, scope)
      id_type = self.semantic.check_accesses(scope, identifier_access, accesses)
      self.__assign(scope, id_type)
    elif(token != None and token.value == '('):
      self.__next_token()
      args_list = self.__args(scope, [])
      token = self.__token()
      if(token != None and token.value == ')'):
        self.__next_token()
        self.semantic.function_call(identifier, args_list)
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
      first_access = self.__access(scope, [])
      first_identifier = first_access[0]
      accesses = self.__accesses(scope, [])
      id_type = None
      if(len(first_access) > 0):
        identifier = first_identifier['token']
        self.semantic.check_const_assign(identifier, scope, scope_definition)
        id_type = self.semantic.check_accesses(scope, first_identifier, accesses, scope_definition)
      self.__assign(scope, id_type)
    elif(token != None and token.key == 'IDE'):
      identifier = token
      self.__next_token()
      self.__stm_id(scope, identifier)
    elif(token != None and (token.value == 'print' or token.value == 'read')):
      self.__next_token()
      token = self.__token()
      if(token != None and token.value == '('):
        self.__next_token()
        self.__args(scope, [])
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

  def __func_stms(self, scope, func_type):
    token = self.__token()
    if(token != None and token.value == 'if'):
      self.__next_token()
      self.__if_stm(scope, func_type)
      self.__func_stms(scope, func_type)
    elif(token != None and token.value == 'while'):
      self.__next_token()
      self.__while_stm(scope, func_type)
      self.__func_stms(scope, func_type)
    elif(token != None and (token.key == 'IDE' or token.value == 'local' or token.value == 'global' or token.value == 'print' or token.value == 'read')):
      self.__var_stm(scope)
      self.__func_stms(scope, func_type)
    elif(token != None and token.value == 'return'):
      self.__next_token()
      exp_type = self.__exp(scope)
      self.semantic.compare_types(func_type, exp_type, token.line)
      token = self.__token()
      if(token != None and token.value == ';'):
        self.__next_token()
      else:
        self.__error('\';\'', ['}'])


  def __func_block(self, scope, func_type):
    token = self.__token()
    if(token != None and token.value == '{'):
      self.__next_token()
      token = self.__token()
    else:
      self.__local_fix('\'{\'')
    if(token != None and token.value == 'var'):
      self.__next_token()
      self.__var_block(scope)
    self.__func_stms(scope, func_type)
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
            self.__func_block(name, func_type)
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
      if(self.semantic.errors == 0):
        self.output.write('Successful semantic analysis! No errors found.\n')
        print('-> Successful semantic analysis! No errors found.')
      else:
        if(self.semantic.errors == 1):
          self.output.write('Semantic analysis failed! 1 error found.\n')
          print('-> Semantic analysis failed! 1 error found.')
        else:
          self.output.write('Semantic analysis failed! {} errors found.\n'.format(self.semantic.errors))
          print('-> Semantic analysis failed! {} errors found.'.format(self.semantic.errors))
        
      
