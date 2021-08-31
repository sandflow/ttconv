"""CSS class"""

class CssClass:
  """CSS class definition class"""

  def __init__(self, property_name: str, value: str, classname: str):
    self._propertyname = property_name
    self._classname = classname
    self._value = value

  def to_string(self) -> str:
    """Return CSS class as formated string"""
    return str(self)

  def __str__(self) -> str:
    return "\n".join(("::cue(.{}) {{".format(self._classname),
                      "  {}: {};".format(self._propertyname, self._value), "}"))
