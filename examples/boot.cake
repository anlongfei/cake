from cake.library.compilers.dummy import DummyCompiler
from cake.library.compilers.gcc import GccCompiler
from cake.library.compilers.msvc import findCompiler as findMsvcCompiler
from cake.library.script import ScriptTool
from cake.library.filesys import FileSystemTool
from cake.library.variant import VariantTool
from cake.library.env import Environment
from cake.engine import Variant

def setupVariant(variant):
  platform = variant.keywords["platform"]
  compilerName = variant.keywords["compiler"]
  release = variant.keywords["release"]
  compiler = variant.tools["compiler"]
  
  env = variant.tools["env"]
  env["BUILD"] = "build/" + "_".join([
    platform,
    compilerName,
    compiler.architecture,
    release,
    ])

  if release == "debug":
    compiler.debugSymbols = True
  elif release == "release":
    compiler.optimisation = compiler.FULL_OPTIMISATION

  return variant
  
base = Variant()
base.tools["script"] = ScriptTool()
base.tools["filesys"] = FileSystemTool()
base.tools["variant"] = VariantTool()
env = base.tools["env"] = Environment()
env["EXAMPLES"] = "."

# Dummy
dummy = base.clone(platform="windows", compiler="dummy")
dummy.tools["compiler"] = DummyCompiler()

dummyDebug = dummy.clone(release="debug")
engine.addVariant(setupVariant(dummyDebug), default=True)

dummyRelease = dummy.clone(release="release")
engine.addVariant(setupVariant(dummyRelease))

# Msvc
msvc = base.clone(platform="windows", compiler="msvc")
msvc.tools["compiler"] = findMsvcCompiler() 

msvcDebug = msvc.clone(release="debug")
engine.addVariant(setupVariant(msvcDebug))

msvcRelease = msvc.clone(release="release")
engine.addVariant(setupVariant(msvcRelease))

# Gcc
gcc = base.clone(platform="windows", compiler="gcc")
gcc.tools["compiler"] = GccCompiler(
  ccExe="C:/Tools/MinGW/bin/gcc.exe",
  arExe="C:/Tools/MinGW/bin/ar.exe",
  ldExe="C:/Tools/MinGW/bin/gcc.exe",
  architecture="x86",
  )

gccDebug = gcc.clone(release="debug")
engine.addVariant(setupVariant(gccDebug))

gccRelease = gcc.clone(release="release")
engine.addVariant(setupVariant(gccRelease))
