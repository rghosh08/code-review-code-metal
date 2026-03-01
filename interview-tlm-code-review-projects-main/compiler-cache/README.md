# Compiler Cache

To try it:

1. Build the interceptor with `cmake .; make`.

1. Then, build the demo as follows:
```
cd target-project
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=/usr/bin/clang \
    -DCMAKE_CXX_COMPILER=/usr/bin/clang++ \
     -DCMAKE_CXX_COMPILER_LAUNCHER=./interceptor \
      -DCMAKE_C_COMPILER_LAUNCHER=./interceptor \
 -G Ninja -S . -B ./build
cd build;
ninja
```

Adjust the `interceptor` path to match your layout. I used github codespaces.cd

# Design
We keep a cache in a folder, named by . There is a metadata file, in JSON, that associates commandlines with the set of runtime dependencies and the time we last built that object.

When run, the interceptor  reads the cache metadata, and checks if the command line is present.
If so, it checks whether the dependencies are all older than the build. If yes, it copies back the built artifact. If no, it rebuilds.

I wanted to keep dependencies light, so everything is just JSON. (SQLite was the other option I considered.)
