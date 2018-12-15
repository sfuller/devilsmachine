cmake_minimum_required(VERSION 3.0)

project(devilsmachine)

find_package(PythonInterp 3.6 REQUIRED)

install(
    DIRECTORY "${PROJECT_SOURCE_DIR}/cmake"
    DESTINATION "share"
)
install(
    DIRECTORY "${PROJECT_SOURCE_DIR}/devilsmachine"
    DESTINATION "lib/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}"
)