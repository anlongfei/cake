"""Variant Tool.
"""

from cake.engine import Script
from cake.library import Tool

class VariantTool(Tool):
  
  def __getattribute__(self, name):
    """Return a variant keywords current value given its name.
    
    @param name: The name of the keyword to query.
    @type name: string
    @return: The current value of the named keyword.
    @rtype: string
    """
    try:
      return object.__getattribute__(self, name)
    except AttributeError:
      try:
        return Script.getCurrent().variant.keywords[name]
      except KeyError:
        raise AttributeError("Unknown attribute '%s'" % name)
  