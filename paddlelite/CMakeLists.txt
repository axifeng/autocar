cmake_minimum_required(VERSION 2.8.12)
project(paddlelite)

set(PADDLE_INCLUDE_DIR "${PROJECT_SOURCE_DIR}/include" )
set(PADDLE_LIB_DIR "${PROJECT_SOURCE_DIR}/lib" )

include_directories(${PADDLE_INCLUDE_DIR})
link_directories(${PADDLE_LIB_DIR})

set(PROJECT_SOURCES src/pybind.h src/pybind.cc)

add_subdirectory(pybind11)
pybind11_add_module(${PROJECT_NAME} ${PROJECT_SOURCES})
target_link_libraries(${PROJECT_NAME} PRIVATE paddle_full_api_shared) 
