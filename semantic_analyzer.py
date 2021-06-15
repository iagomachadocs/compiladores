class SemanticAnalyzer:
  def __init__(self, output):
    self.output = output
    self.scopes = {
      'global': {}
    }
  
  def error(self, error, line, value):
    messages = {
      'duplicated identifier': 'Identifier \'{}\' has already been declared.'.format(value),
      'invalid type': '\'{}\' is not a valid type.'.format(value),
      'duplicated function': 'Function \'{}\' has already been declared.'.format(value),
      'duplicated procedure': 'Procedure \'{}\' has already been declared.'.format(value),
      'not defined': '\'{}\' is not defined.'.format(value),
      'array index type': 'Array index must be integer.',
      'const assign': '\'{}\' is a constant and cannot be assigned.'.format(value),
    }
    self.output.write('{} Semantic error: {}\n'.format(line, messages[error]))
    print('-> Semantic error - line {}: {}'.format(line, messages[error]))

  def check_type(self, token_type, scope='global'):
    PRIMITIVE_TYPES = set(['int', 'real', 'boolean', 'string'])
    if(token_type in PRIMITIVE_TYPES):
      return True
    elif(token_type in self.scopes[scope]):
      id_class = self.scopes[scope][token_type]['class']
      if(id_class == 'type' or id_class == 'struct'):
        return True
    elif(scope != 'global' and token_type in self.scopes['global']):
      id_class = self.scopes['global'][token_type]['class']
      if(id_class == 'type' or id_class == 'struct'):
        return True
    return False

  def identifier_declaration(self, token, scope, attributes):
    name = token.value
    if(name not in self.scopes[scope]):
      identifier_type = attributes['type']
      valid_type = self.check_type(identifier_type, scope)
      if(valid_type):
        self.scopes[scope][name] = attributes
      else:
        self.error('invalid type', token.line, identifier_type)
    else:
      self.error('duplicated identifier', token.line, token.value)


  def check_params_type(self, params):
    for param in params:
      valid_type = self.check_type(param['type'])
      if(not valid_type):
        return param['type']
    return True

  def params_to_string(self, params):
    string = '('
    first = True
    for param in params:
      if(first):
        first = False
      else:
        string += ', '
      string += param['type']
      if(param['array']):
        string += '[]'
    string += ')'
    return string
  
  def params_declaration(self, scope, params):
    for param in params:
      name = param['name']
      self.scopes[scope][name] = {'type': param['type'], 'class': 'var', 'array': param['array']}

  def function_declaration(self, token, return_type, params):
    params_str = self.params_to_string(params)
    name = token.value + params_str
    if(name not in self.scopes['global']):
      valid_types = self.check_params_type(params)
      if(valid_types == True):
        valid_return_type = self.check_type(return_type)
        if(valid_return_type):
          self.scopes['global'][name] = {'type': return_type, 'class': 'function'}
          self.scopes[name] = {}
          self.params_declaration(name, params)
          return name
        else:
          self.error('invalid type', token.line, return_type)
          return None
      else:
        self.error('invalid type', token.line, valid_types)
        return None
    else:
      self.error('duplicated function', token.line, name)
      return None

  def procedure_declaration(self, token, params):
    params_str = self.params_to_string(params)
    name = token.value + params_str
    if(name not in self.scopes['global']):
      valid_types = self.check_params_type(params)
      if(valid_types == True):
        self.scopes['global'][name] = {'type': None, 'class': 'procedure'}
        self.scopes[name] = {}
        self.params_declaration(name, params)
        return name
      else:
        self.error('invalid type', token.line, valid_types)
        return None
    else:
      self.error('duplicated procedure', token.line, name)
      return None

  def type_declaration(self, typedef_type, token, scope):
    valid_type = self.check_type(typedef_type, scope)
    identifier = token.value
    if(valid_type):
      if(identifier not in self.scopes[scope]):
        self.scopes[scope][identifier] = {'type': typedef_type, 'class': 'type'}
      else:
        self.error('duplicated identifier', token.line, token.value)
    else:
      self.error('invalid type', token.line, typedef_type)

  def struct_declaration(self, token, extends=None):
    identifier = 'struct '+token.value
    if(identifier not in self.scopes['global']):
      if(extends != None):
        self.scopes['global'][identifier] = {'class': 'struct'}
        self.scopes[identifier] = {}
        if(self.check_type(extends)):
          self.scopes[identifier] = self.scopes[extends].copy()   
        else:
          self.error('invalid type', token.line, extends)
        return identifier
      else:
        self.scopes['global'][identifier] = {'class': 'struct'}
        self.scopes[identifier] = {}
        return identifier  
    else:
      self.error('duplicated identifier', token.line, identifier)

  def typedef_struct_declaration(self, token):
    identifier = 'struct '+token.value
    if(identifier not in self.scopes['global']):
      self.scopes['global'][identifier] = self.scopes['global']['struct _temp'].copy()
      self.scopes[identifier] = self.scopes['struct _temp'].copy()
      self.type_declaration(identifier, token, 'global')
    else:
      self.error('duplicated identifier', token.line, identifier) 
    del self.scopes['global']['struct _temp']
    del self.scopes['struct _temp']

  def is_integer(self, token):
    if(token.key == 'NRO'):
      identifier = str(token.value)
      if('.' not in identifier):
        return True
    return False

  def array_index_type(self, token, scope):
    value = token.value
    if(value == 'IDE'):
      if(value in self.scopes[scope]):
        if(self.scopes[scope][value]['type'] == 'int'):
          return True
        else:
          self.error('array index type', token.line, value)
      elif(value in self.scopes['global']):
        if(self.scopes['global'][value]['type'] == 'int'):
          return True
        else:
          self.error('array index type', token.line, value)  
      else:
        self.error('not defined', token.line, value)
      return False
    elif(self.is_integer(token)):
      return True
    else:
      self.error('array index type', token.line, value)
      return False

  def check_const_assign(self, token, scope, scope_definition=None):
    identifier = token.value
    if(scope == 'global' or scope_definition == 'global'):
      if(identifier in self.scopes['global']):
        if(self.scopes['global'][identifier]['class'] == 'const'):
          self.error('const assign', token.line, identifier)
      else:
        self.error('not defined', token.line, identifier)
    
        

      
