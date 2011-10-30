#-------------------------------------------------------------------------------
# This script recursively builds all examples that are known to work.
#-------------------------------------------------------------------------------
from cake.tools import script, compiler

script.execute([
  "compileprogram/build.cake",
  "compilescriptresult/build.cake",
  "copydirectory/build.cake",
  "copyfile/build.cake",
  "env/build.cake",
  "findfiles/build.cake",
  "pythontool/build.cake",
  "queryvariant/build.cake",
  "scriptresult/build.cake",
  "shell/build.cake",
  "unzip/build.cake",
  "uselibrary/main/build.cake",
  "usemodule/main/build.cake",
  "usepch/build.cake",
  "zip/build.cake",
  ])

if compiler.name == "msvc":
  script.execute([
    "cppdotnet/program/build.cake",
    ])
