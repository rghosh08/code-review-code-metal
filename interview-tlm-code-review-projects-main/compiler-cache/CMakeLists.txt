cmake_minimum_required(VERSION 3.16)

set(CMAKE_CXX_STANDARD 20)
project(interceptor
        VERSION 0.0.1
        DESCRIPTION "Compiler interceptor"
        LANGUAGES CXX C)

add_executable(interceptor main.cpp)
