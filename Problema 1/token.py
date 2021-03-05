class Token:
  
  def __init__(self, line, key, value):
    self.line = line
    self.key = key
    self.value = value
  
  def __str__(self):
    return str(self.line)+" "+str(self.key)+" "+str(self.value)
