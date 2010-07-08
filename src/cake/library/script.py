"""Script Tool.

@see: Cake Build System (http://sourceforge.net/projects/cake-build)
@copyright: Copyright (c) 2010 Lewis Baker, Stuart McMahon.
@license: Licensed under the MIT license.
"""

from cake.engine import Script
from cake.library import Tool, ScriptResult, FileTarget, getPaths, getTasks

class ScriptTool(Tool):
  """Tool that provides utilities for performing Script operations.
  """
  
  @property
  def path(self):
    """The path of the currently executing script.
    """
    return Script.getCurrent().path
  
  @property
  def dir(self):
    """The path of the directory of the currently executing script.
    """
    return Script.getCurrent().dir
  
  @property
  def variant(self):
    """The Variant the currently executing script is being built with.
    """
    return Script.getCurrent().variant

  def setResult(self, **kwargs):
    """Export a result from this script that other scripts can import.
    
    Other scripts can use getResult(script, name) to get the result
    exported by the other script calling setResult(name=result).
    """
    Script.getCurrent().setResult(**kwargs)
  
  def getResult(self, script, name):
    """Get a placeholder value that will yield the result of another
    script once that other script has finished executing.
    """
    return self.get(script).getResult(name)
  
  def get(self, script, keywords={}, useContext=None, configScript=None, configScriptName=None):
    """Get another script to use in referencing targets.
    
    @param script: Path of the script to load.
    @type script: string
    
    @param keywords: A set of keywords used to find the variant the script
    will be executed with. The variant is looked up in the script's configuration.
    @type keywords: dictionary of string -> string
    
    @param useContext: If False or if None and either configScript or configScriptName
    are not None then lookup the corresponding configuration script starting from the
    script's path, if True then use the current configuration/variant.
    @type useContext: bool or None
    
    @param configScript: The path of the configuration script to use to execute the script.
    Ignored if useContext is True.
    @type configScript: string or None
    
    @param configScriptName: If not None and configScript is None then find the
    configuration script with this name starting the search at the script's path.
    Ignored if useContext is True.
    @type configScriptName: string or None
    """
  
    if not isinstance(script, basestring):
      raise ValueError("'script' must be a string")
  
    if useContext is None:
      useContext = configScript is None and configScriptName is None
  
    if useContext:
      # Use the current configuration and lookup the variant relative
      # to the current variant.
      baseVariant = Script.getCurrent().variant 
      def execute():
        variant = self.configuration.findVariant(keywords, baseVariant=baseVariant)
        return self.configuration.execute(path=script, variant=variant)
    else:
      # Re-evaluate the configuration to execute the script with.
      # Uses the keywords specified to find the variant in the variants
      # defined in that configuration.
      def execute():
        path = self.configuration.abspath(script)
        if configScript is None:
          configuration = self.engine.findConfiguration(
            path=path,
            configScriptName=configScriptName,
            )
        else:
          configuration = self.engine.getConfiguration(
            path=self.configuration.abspath(configScript),
            )
        variant = configuration.findVariant(keywords)
        return configuration.execute(path=path, variant=variant)
      
    return ScriptProxy(execute)

  def cwd(self, *args):
    """Return the path prefixed with the this script's directory.
    
    Examples::
      env.cwd("a") -> "{cwd}/a"
      env.cwd(["a", "b", "c"]) -> ["{cwd}/a", "{cwd}/b", "{cwd}/c"]
      
    @param args: The arguments that need to have the prefix added.
    @type args: string or list(string)
    
    @return: The path prefixed with this script's directory.
    @rtype: string or list(string)
    """
    script = Script.getCurrent()
    return script.cwd(*args)
    
  def include(self, scripts):
    """Include another script within the context of the currently
    executing script.
    
    A given script will only be included once.
    
    @param scripts: A path or sequence of paths of scripts to include.
    @type scripts: string or sequence of string
    """
    include = Script.getCurrent().include
    if isinstance(scripts, basestring):
      include(scripts)
    else:
      for path in scripts:
        include(path)
    
  def execute(self, scripts, **keywords):
    """Execute another script as a background task.

    Executes the other script using the current script's configuration
    but potentially a different build variant.
    
    If you need to execute a script using a different configuration
    then use the 'executeNoContext' method instead. 

    @param scripts: A path or sequence of paths of scripts to execute.
    @type scripts: string or sequence of string

    @return: A Script object or sequence of Script objects that can be used
    to determine what scripts will be executed. The script's task will
    complete when the script has finished executing.
    @rtype: L{Script} or C{list} of L{Script}
    """
    script = Script.getCurrent()
    configuration = script.configuration
    variant = configuration.findVariant(keywords, baseVariant=script.variant)
    execute = configuration.execute
    if isinstance(scripts, basestring):
      return execute(scripts, variant)
    else:
      return [execute(path, variant) for path in scripts]


  def run(self, func, args=None, targets=None, sources=[]):
    """Execute the specified python function as a task.

    Only executes the function after the sources have been built and only
    if the target exists, args is the same as last run and the sources
    haven't changed.

    @note: I couldn't think of a better class to put this function in so
    for now it's here although it doesn't really belong.
    """
    engine = self.engine
    configuration = self.configuration

    sourceTasks = getTasks(sources)

    def _run():
      sourcePaths = getPaths(sources)
      if targets:
        buildArgs = (args, sourcePaths)
        try:
          _, reason = configuration.checkDependencyInfo(
            targets[0],
            buildArgs,
            )
          if reason is None:
            # Up to date
            return
          
          engine.logger.outputDebug(
            "reason",
            "Building '%s' because '%s'\n" % (targets[0], reason),
            )
        except EnvironmentError:
          pass

      try:
        return func()
      finally:
        if targets:
          newDependencyInfo = configuration.createDependencyInfo(
            targets=targets,
            args=buildArgs,
            dependencies=sourcePaths,
            )
          configuration.storeDependencyInfo(newDependencyInfo)

    task = engine.createTask(_run)
    task.startAfter(sourceTasks)

    if targets is not None:
      return [FileTarget(path=t, task=task) for t in targets]
    else:
      return task

class ScriptProxy(object):
  """A proxy that can be used to perform actions on a particular
  script.
  """
 
  def __init__(self, execute):
    self.__execute = execute

  def execute(self):
    """Start the execution of the script if it hasn't already been started.
    
    The script will complete execution at some point in the future.
    
    @return: The Script object that will be executed.
    """
    return self.__execute()
  
  def getResult(self, name):
    """Get a placeholder for the result defined by this script when it is
    executed.
    
    The script will be executed if the result is ever required.
    """
    return ScriptResult(self.__execute, name)

