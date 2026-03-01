cmake_minimum_required(VERSION 3.30)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(sample
        VERSION 0.0.1
        DESCRIPTION "Sample C++ project"
        LANGUAGES CXX C)

include(cmake/Dependencies.cmake)

add_subdirectory(src)
