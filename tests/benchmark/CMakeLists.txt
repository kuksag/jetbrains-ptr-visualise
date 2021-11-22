cmake_minimum_required(VERSION 3.16)
project(benchmark CXX)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

set (CMAKE_CXX_FLAGS "-O0 -g")

add_executable(main main.cpp)
target_link_libraries(main PRIVATE Threads::Threads)
