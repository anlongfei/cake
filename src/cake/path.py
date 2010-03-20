"""Path Utilities.

@see: Cake Build System (http://sourceforge.net/projects/cake-build)
@copyright: Copyright (c) 2010 Lewis Baker, Stuart McMahon.
@license: Licensed under the MIT license.
"""

import os
import os.path
import platform

def dirName(path):
  """Get the directory part of the path.
  
  @param path: The path to split.
  @type path: string
  
  @return: The directory part of the path.
  @rtype: string
  """
  return os.path.dirname(path)

def baseName(path):
  """Get the file-name part of the path.

  @param path: The path to split.
  @type path: string
  
  @return: The file-name part of the path.
  @rtype: string
  """
  return os.path.basename(path)

def split(path):
  """Split the path into directory and base parts.

  @param path: The path to split.
  @type path: string
  
  @return: The directory and base parts of the path.
  @rtype: tuple(string, string)
  """
  return os.path.split(path)

def hasExtension(path):
  """Query if the last part of a path has a file extension.
  
  A file extension is any part after the last dot inclusively.

  @param path: The path to check.
  @type path: string
  
  @return: True if the path has an extension, otherwise False.
  @rtype: bool
  """ 
  end = path.rfind("\\")
  end = max(path.rfind("/", end + 1), end) + 1
  # We search in the substring AFTER the last slash.
  # In the case that a slash is not found, the -1 returned by rfind becomes zero, 
  # and so searches the whole string
  extStart = path.rfind(".", end)
  return extStart > end and path.count(".", end, extStart) != extStart - end

def extension(path):
  """Get the file extension of the last part of a path.
  
  A file extension is any part after the last dot inclusively.

  @param path: The path to split.
  @type path: string
  
  @return: The extension part of the path.
  @rtype: string
  """ 
  end = path.rfind("\\")
  end = max(path.rfind("/", end + 1), end) + 1
  # We search in the substring AFTER the last slash.
  # In the case that a slash is not found, the -1 returned by rfind becomes zero, 
  # and so searches the whole string
  extStart = path.rfind(".", end)
  if extStart > end and path.count(".", end, extStart) != extStart - end:
    return path[extStart:]
  else:
    return ""

def stripExtension(path):
  """Return the part of the path before the extension.
  
  @param path: The path to split.
  @type path: string
  
  @return: The part of the path before the extension.
  @rtype: string
  """
  end = path.rfind("\\")
  end = max(path.rfind("/", end + 1), end) + 1
  # We search in the substring AFTER the last slash.
  # In the case that a slash is not found, the -1 returned by rfind becomes zero, 
  # and so searches the whole string
  extStart = path.rfind(".", end)
  if extStart > end and path.count(".", end, extStart) != extStart - end:
    return path[:extStart]
  else:
    return path

def addPrefix(path, prefix):
  """Prefix the baseName part of a path and return the result.

  @param path: The path to prefix.
  @type path: string
  @param prefix: The prefix to prepend to the baseName part.
  @type prefix: string
  
  @return: The path with it's baseName part prefixed with 'prefix'.
  @rtype: string
  """
  if not prefix:
    return path
  
  head, tail = os.path.split(path)
  tail = prefix + tail
  if head:
    return os.path.join(head, tail)
  else:
    return tail

def forcePrefixSuffix(path, prefix, suffix):
  """Force both a prefix and suffix only if the suffix does not match.

  @param path: The path to modify.
  @type path: string
  @param prefix: The prefix to prepend to the baseName part.
  @type prefix: string
  @param suffix: The suffix to append to the path.
  @type suffix: string
  @return: The path with the given prefix and suffix if the suffix did
  not exist, otherwise the original path.
  @rtype: string
  """
  if os.path.normcase(extension(path)) != os.path.normcase(suffix):
    return addPrefix(path, prefix) + suffix
  else:
    return path
  
def forceExtension(path, ext):
  """Return the path modified if needed to have the specified extension.
  
  @param path: The path to force an extension onto.
  @type path: string
  
  @return: The path with the specified extension.
  @rtype: string
  """
  if not os.path.normcase(path).endswith(os.path.normcase(ext)):
    return path + ext
  else:
    return path

def baseNameWithoutExtension(path):
  """Get the file-name part of the path without the extension.

  @param path: The path to split.
  @type path: string
  
  @return: The file-name part of the path without the extension.
  @rtype: string
  """
  end = path.rfind("\\")
  end = max(path.rfind("/", end + 1), end) + 1
  # We search in the substring AFTER the last slash.
  # In the case that a slash is not found, the -1 returned by rfind becomes zero, 
  # and so searches the whole string
  extStart = path.rfind(".", end)
  if extStart > end and path.count(".", end, extStart) != extStart - end:
    return path[end:extStart]
  else:
    return path[end:]

def commonPath(path1, path2):
  """
  Given two paths, find their common root path, if any.
  
  @param path1: The first path to scan.
  @type path1: string
  @param path2: The second path to scan.
  @type path2: string
  @return: The common root path of the two paths.
  @rtype: string
  """
  seps = [os.path.sep, os.path.altsep]
  path1len = len(path1)
  path2len = len(path2)
  charCount = min(path1len, path2len)
  safeCount = 0

  for i in xrange(charCount):
    if path1[i] != path2[i]:
      return path1[:safeCount] # No more matches
    elif path1[i] in seps:
      safeCount = i # Last safe path match

  # All characters matched in at least one string. For the path to be valid,
  #   the next character in other string must be a slash
  if path1len > charCount:
    if path1[charCount] in seps:
      safeCount = charCount
  elif path2len > charCount:
    if path2[charCount] in seps:
      safeCount = charCount
  elif path1len == path2len and path1len and path1[-1] not in seps:
    safeCount = path1len
  return path1[:safeCount]

if platform.system() == "Windows":
  try:
    import win32file
    def _fileSystemBaseName(path, stem, leaf):
      findData = win32file.FindFilesIterator(path).next()
      return str(findData[8])
  except ImportError:
    def _fileSystemBaseName(path, stem, leaf):
      leafNorm = os.path.normcase(leaf)
      for f in os.listdir(stem):
        if os.path.normcase(f) == leafNorm:
          return f
      return leaf

  def fileSystemPath(path):
    """Look up the correctly cased path from the file system.
  
    This is only relevant on file systems that are case insensitive such
    as Windows.
    
    '/' and '\\' will be left intact.
  
    '.' and '..' will be left intact.
    
    A drive letter will be capitalized.
    
    @param path: The path to look up.
    @type path: string
    
    @return: The correctly cased file system path.
    @rtype: string
    """
    seps = frozenset([os.path.sep, os.path.altsep])

    parts = list()
    while path:
      stem, leaf = os.path.split(path)
      if leaf != '.' and leaf != '..':
        try:
          leaf = _fileSystemBaseName(path, stem, leaf)
        except Exception:
          pass
      parts.append(leaf)
  
      if stem and len(path) > len(stem):
        sep = path[len(stem)]
        if sep in seps:
          parts.append(sep)
          
      path = stem
      
      if not leaf:
        # Reached root path
        break
  
    if path:
      # Capitalise drive letter if found
      if len(path) >= 2 and path[1] == ':':
        path = path.capitalize()
      parts.append(path)
  
    return "".join(reversed(parts))

else:
  # Assume a case-sensitive file-system
  def fileSystemPath(path):
    return path

def join(*args):
  """Find the cross product of any amount of input paths or lists of paths.
  
  Examples::
    join("a", "b", "c") -> "a/b/c"
    join("a", ["b", "c"], "d") -> ["a/b/d", "a/c/d"]
    join(["a", "b"], ["c", "d"]) -> ["a/c", "a/d", "b/c", "b/d"]
    
  @param args: The arguments to cross.
  @type args: string or list(string)
  
  @return: The cross product of the given arguments.
  @rtype: string or list(string)
  """
  results = []

  if not args:
    return ""
  elif len(args) == 1:
    return args[0]

  anyLists = False
  
  last = args[-1]
  if isinstance(last, basestring):
    results = [last]
  else:
    results = last
    anyLists = True

  osJoin = os.path.join

  for i in xrange(len(args) - 2, -1, -1):
    arg = args[i]
    if isinstance(arg, basestring):
      results = [osJoin(arg, r) for r in results]
    else:
      anyLists = True
      newResults = []
      for a in arg:
        newResults.extend(osJoin(a, r) for r in results)
      results = newResults
  
  if anyLists:
    return results
  else:
    return results[0]

def expandVars(path, env):
  """Recursively expand shell variables of the form $var and ${var}.

  This function is a copy of os.path.expandvars() with added support for
  recursion.
  
  Unknown variables are replaced with {MISSING_SYMBOL_<varname>}.
  
  @param path: The path to expand.
  @type path: string
  @param env: A dictionary of symbols to their values.
  @type env: dict
  
  @return: The expanded path.
  @rtype: string
  """
  if '$' not in path:
    return path
  import string
  varchars = string.ascii_letters + string.digits + '_-'
  res = ''
  index = 0
  pathlen = len(path)
  while index < pathlen:
    c = path[index]
    if c == '\'':   # no expansion within single quotes
      path = path[index + 1:]
      pathlen = len(path)
      try:
        index = path.index('\'')
        res = res + '\'' + path[:index + 1]
      except ValueError:
        res = res + path
        index = pathlen - 1
    elif c == '$':  # variable or '$$'
      if path[index + 1:index + 2] == '$':
        res = res + c
        index = index + 1
      elif path[index + 1:index + 2] == '{':
        path = path[index + 2:]
        pathlen = len(path)
        try:
          index = path.index('}')
          var = path[:index]
          if var in env:
            res = res + expandVars(env[var], env)
          else:
            res = res + '{MISSING_SYMBOL_' + var + '}'
        except ValueError:
          res = res + path
          index = pathlen - 1
      else:
        var = ''
        index = index + 1
        c = path[index:index + 1]
        while c != '' and c in varchars:
          var = var + c
          index = index + 1
          c = path[index:index + 1]
        if var in env:
          res = res + expandVars(env[var], env)
        else:
          res = res + '{MISSING_SYMBOL_' + var + '}'
        if c != '':
          res = res + c
    else:
      res = res + c
    index = index + 1
  return res
