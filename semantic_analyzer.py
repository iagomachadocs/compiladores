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
      'duplicated function': 'Function \'{}\' has already been declared.'.format(value)
    }
    self.output.write('{} Semantic error: {}\n'.format(line, messages[error]))
    print('-> Semantic error - line {}: {}'.format(line, messages[error]))

  def check_type(self, token_type):
    PRIMITIVE_TYPES = set(['int', 'real', 'boolean', 'string'])
    if(token_type in PRIMITIVE_TYPES):
      return True
    elif(token_type in self.scopes['global']):
      id_class = self.scopes['global'][token_type]['class']
      if(id_class == 'type' or id_class == 'struct'):
        return True
    return False

  def identifier_declaration(self, token, scope, attributes):
    name = token.value
    if(name not in self.scopes[scope]):
      identifier_type = attributes['type']
      valid_type = self.check_type(identifier_type)
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
      self.error('duplicated function', token.line, name)
      return None
