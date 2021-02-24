import os
import ycm_core

flags = [
  '-std=c++17',
  '-Iinclude',
  '-fno-use-cxa-atexit',
  '-nostdlib',
  '-fno-builtin',
  '-fno-rtti',
  '-fno-exceptions',
  '-Wno-write-strings'
]

# Base directory of the project, parent directory of all source files
project_dir = os.path.dirname(os.path.abspath(__file__))

# This assumes that everyone coding for this project builds inside the 'build'
# directory
compilation_database_folder = project_dir + "/build"

if os.path.exists(compilation_database_folder):
  database = ycm_core.CompilationDatabase(compilation_database_folder)
else:
  database = None

SOURCE_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.c', '.m', '.mm']

# Converts all relative paths in the given flag list to absolute paths with
# working_directory as the base directory
def MakeRelativePathsInFlagsAbsolute(flags, working_directory):
  if not working_directory:
    return list(flags)
  new_flags = []
  make_next_absolute = False
  path_flags = ['-isystem', '-I', '-iquote', '--sysroot=']
  for flag in flags:
    new_flag = flag

    if make_next_absolute:
      make_next_absolute = False
      if not flag.startswith('/'):
        new_flag = os.path.join(working_directory, flag)

    for path_flag in path_flags:
      if flag == path_flag:
        make_next_absolute = True
        break

      if flag.startswith(path_flag):
        path = flag[len(path_flag):]
        new_flag = path_flag + os.path.join(working_directory, path)
        break

    if new_flag:
      new_flags.append(new_flag)
  return new_flags

def IsHeaderFile(filename):
  extension = os.path.splitext(filename)[1]
  return extension in ['.h', '.hxx', '.hpp', '.hh', ".inl"]

# Tries to query the compilation database for flags
# For header files it tries to use the flags for a corresponding source file
def GetCompilationInfoForFile(filename):
  if not database:
    return None

  # The compilation_commands.json file generated by CMake does not have entries
  # for header files. We try to use the compile flags used for the corresponding
  # source file.
  #
  # For this try to replace the file extension with an extension that
  # corresponds to a source and we also try to replace the 'include' folder in
  # the path with 'src'
  if IsHeaderFile(filename) :
    basename = os.path.splitext(filename)[0]

    # Absolute path of the include and source directories
    include_dir = project_dir + "/include"
    src_dir = project_dir + "/src"

    # Absolute path without file extension, with the 'include' folder replaced
    # with 'src' in the path
    src_basename = None
    # If the header file is inside the include dir, try to search in the src dir
    if basename.startswith(include_dir):
      # file path relative to include dir
      rel_path_include = os.path.relpath(basename, include_dir)
      src_basename = os.path.join(src_dir, rel_path_include)

    for extension in SOURCE_EXTENSIONS:
      # A list of all possible replacement files to be searched
      replacement_files = [basename + extension]

      if src_basename:
        replacement_files.append(src_basename + extension)

      for replacement_file in replacement_files:
        if os.path.exists(replacement_file):
          comp_info = database.GetCompilationInfoForFile(replacement_file)
          if comp_info.compiler_flags_:
            return comp_info
  return database.GetCompilationInfoForFile(filename)

def FlagsForFile(filename, **kwargs):
  compilation_info = GetCompilationInfoForFile(filename)
  if compilation_info and compilation_info.compiler_flags_:
    # Bear in mind that compilation_info.compiler_flags_ does NOT return a
    # python list, but a "list-like" StringVec object
    final_flags = MakeRelativePathsInFlagsAbsolute(
        [x for x in compilation_info.compiler_flags_ if x != "-Werror"],
        compilation_info.compiler_working_dir_)
  else:
    # We use default flags if GetCompilationInfoForFile can't find any flags
    relative_to = project_dir
    final_flags = MakeRelativePathsInFlagsAbsolute(flags, relative_to)

  return {'flags': final_flags, 'do_cache': True}
