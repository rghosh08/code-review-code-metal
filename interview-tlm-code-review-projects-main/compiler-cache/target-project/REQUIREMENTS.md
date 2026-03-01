## Objective

The object is to create a compilation command caching tool to (potentially) accelerate C++ program
builds. The tool should be usable with CMake's
[
`CMAKE_CXX_COMPILER_LAUNCHER`](https://cmake.org/cmake/help/latest/prop_tgt/LANG_COMPILER_LAUNCHER.html#prop_tgt:%3CLANG%3E_COMPILER_LAUNCHER)
setting.

For a given compilation command, if the command:

1. Hasn't been seen before: The command should be executed and its results cached.
2. Has been seen and executing it again would produce the same output: The command should not be
   executed. The result should be retrieved from the cache.
3. Has been seen before but executing it again would produce different output: The command should be
   executed and its results cached.

A sample CMake-based C++ program is included in this repository. You should ensure that your
solution works with the included project.

As an example, the included project can be configured and built with

```bash
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=/usr/bin/clang -DCMAKE_CXX_COMPILER=/usr/bin/clang++ -G Ninja -S . -B ./build
cd build
ninja
```

Your compiler launcher can be integrated by adding flags to CMake, e.g.:

```bash
-DCMAKE_CXX_COMPILER_LAUNCHER=/your/program -DCMAKE_C_COMPILER_LAUNCHER=/your/program
```

Note that the CMake project has been configured to generate
a [compile_commands.json](https://clang.llvm.org/docs/JSONCompilationDatabase.html) compilation
database. It can be used as a reference for the types of command lines you tool will be given.

Some notes on expectations for submissions:

1. Implement the tool in C++.
2. The project should work in on Linux.
3. It is not necessary to actually improve the performance of program builds.
4. It is fine to support a single compiler (e.g. just clang or just gcc), but please specify which
   is supported.
5. The design, location, and kind of cache is unspecified.
6. Document the build process so that we can recreate the tool and validate its functionality.
7. Feel free to use third partly libraries, but either vendor them or have the build process
   automatically fetch dependencies.
8. The tool may emit log files or messages to standard output or standard error as a means of
   debugging and or demonstrating a working solution.
9. If there are any questions or clarifications, don't hesitate to reach out, but note that our
   default position is to leave it up to candidates to set assumptions and scope.
