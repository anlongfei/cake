import os
import cake.path
from cake.tools.compilers.dummy import DummyCompiler
from cake.tools.compilers.msvc import findCompiler as findMsvcCompiler
from cake.tools.script import ScriptTool
from cake.tools.filesys import FileSystemTool
from cake.tools.env import Environment
from cake.engine import Variant

base = Variant()
base.tools["script"] = ScriptTool()
base.tools["filesys"] = FileSystemTool()
env = base.tools["env"] = Environment()
env["ROOT"] = cake.path.dirName(__file__)
env["BUILD"] = "${ROOT}/build/${PLATFORM}_${COMPILER}_${RELEASE}"

programFiles = os.environ['PROGRAMFILES']
msvsInstall = cake.path.join(programFiles, "Microsoft Visual Studio 8") 

windows = base.clone()
compiler = windows.tools["compiler"] = findMsvcCompiler()
compiler.runtimeLibraries = 'release-dll'
env = windows.tools["env"]
env["PLATFORM"] = "windows"
env["COMPILER"] = "msvc"

windowsDebug = windows.clone(name="win32-debug")
compiler = windowsDebug.tools["compiler"]
compiler.debugSymbols = True
compiler.optimisation = compiler.NO_OPTIMISATION
env = windowsDebug.tools["env"]
env["RELEASE"] = "debug"
engine.addVariant(windowsDebug, default=True)

windowsOptimised = windows.clone(name="win32-opt")
compiler = windowsOptimised.tools["compiler"]
compiler.debugSymbols = True
compiler.optimisation = compiler.PARTIAL_OPTIMISATION
env = windowsOptimised.tools["env"]
env["RELEASE"] = "optimised"
engine.addVariant(windowsOptimised)
