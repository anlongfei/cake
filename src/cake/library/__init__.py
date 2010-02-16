"""Base Class and Utilities for Cake Tools.
"""

class ToolMetaclass(type):
  """This metaclass ensures that new instance variables can only be added to
  an instance during its __init__.
  """
  
  def __init__(cls, name, bases, dct):
    super(ToolMetaclass, cls).__init__(name, bases, dct)
    
    cls._initCount = 0
    
    oldInit = cls.__init__
    def __init__(self, *args, **kwargs):
      self._initCount = self._initCount + 1
      oldInit(self, *args, **kwargs)
      self._initCount = self._initCount - 1
    cls.__init__ = __init__
      
    oldSetattr = cls.__setattr__
    def __setattr__(self, name, value):
      if not self._initCount and not hasattr(self, name):
        raise AttributeError(name)
      oldSetattr(self, name, value)
    cls.__setattr__ = __setattr__

def memoise(func):
  """Decorator that can be placed on Tool methods to memoise the result.
  
  The result cache is invalidated whenever an attribute is set on the
  instance.
  
  @param func: The function to memoise.
  @type func: function
  """
  
  undefined = object()
  def run(*args, **kwargs):
    kwargsTuple = tuple((k,v) for k, v in kwargs.iteritems())
    
    self = args[0]
    key = (func, args[1:], kwargsTuple)

    cache = self._Tool__memoise
    result = cache.get(key, undefined)
    if result is undefined:
      result = func(*args, **kwargs)
      cache[key] = result
    return result
  
  try:
    run.func_name = func.func_name
    run.func_doc = func.func_doc
  except AttributeError:
    pass
  
  return run

class Tool(object):
  """Base class for user-defined Cake tools.
  """
  
  __metaclass__ = ToolMetaclass
  
  def __init__(self):
    self.__memoise = {}
  
  def __setattr__(self, name, value):
    if name != '_Tool__memoise' and hasattr(self, '_Tool__memoise'):
      self._clearCache()
    super(Tool, self).__setattr__(name, value)
  
  def _clearCache(self):
    """Clear the memoise cache due to some change.
    """
    self.__memoise.clear()
  
  def clone(self):
    """Return an independent clone of this tool.
    
    The default clone behaviour performs a shallow copy of the
    member variables of the tool. You should override this method
    if you need a more sophisticated clone.
    """
    new = self.__class__()
    new.__dict__ = deepCopyBuiltins(self.__dict__)
    return new

class FileTarget(object):
  """A class returned by tools that produce a file result.
  
  @ivar path: The path to the target file.
  @type path: string
  @ivar task: A task that completes when the target file has been written. 
  @type task: L{FileTarget}
  """
  
  def __init__(self, path, task):
    """Construct a FileTarget from a path and task.
    """
    self.path = path
    self.task = task

def getPathAndTask(file):
  """Returns a path and task given a file.
  
  @param file: The path or FileTarget to split.
  @type file: string or L{FileTarget} 
  @return: A file path and task (or None). 
  @rtype: tuple of string, L{Task}
  """
  if isinstance(file, FileTarget):
    return file.path, file.task
  else:
    return file, None

def getPathsAndTasks(files):
  """Returns a list of paths and tasks for given files.

  @param files: The paths or FileTarget's to split.
  @type files: list of string's or L{FileTarget}'s 
  @return: Lists of paths and tasks.
  @rtype: tuple of (list of string), (list of L{Task}) 
  """
  paths = []
  tasks = []
  for f in files:
    if isinstance(f, FileTarget):
      paths.append(f.path)
      tasks.append(f.task)
    else:
      paths.append(f)
  return paths, tasks

def deepCopyBuiltins(obj):
  """Returns a deep copy of only builtin types.
  
  @param obj: The given object to copy.
  @return: A copy of the given object for builtin types, and references to
  the same object for user-defined types.
  """
  if isinstance(obj, dict):
    return dict((deepCopyBuiltins(k), deepCopyBuiltins(v)) for k, v in obj.iteritems())
  elif isinstance(obj, (list, tuple, set)):
    return type(obj)(deepCopyBuiltins(i) for i in obj)
  else:
    return obj