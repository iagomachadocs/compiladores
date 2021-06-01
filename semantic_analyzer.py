class SemanticAnalyzer:
  def __init__(self, output):
    self.output = output
    self.scopes = {
      'global': {}
    }
  
  def error(self, error, line, value):
    messages = {
      'duplicated identifier': 'Identifier \'{}\' has already been declared.'.format(value),
      'invalid type': '\'{}\' is not a valid type.'.format(value)
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

