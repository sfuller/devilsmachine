cmake_minimum_required(VERSION 3.0)

project(devilsmachine)

install(
    DIRECTORY "${PROJECT_SOURCE_DIR}/cmake"
    DESTINATION "share"
)
install(
    DIRECTORY "${PROJECT_SOURCE_DIR}/devilsmachine"
    DESTINATION "lib/python3"
)