#
#      _             _ _                        _     _
#     | |           (_) |                      | |   (_)
#   _ | | ____ _   _ _| | ___ ____   ____  ____| | _  _ ____   ____
#  / || |/ _  ) | | | | |/___)    \ / _  |/ ___) || \| |  _ \ / _  )
# ( (_| ( (/ / \ V /| | |___ | | | ( ( | ( (___| | | | | | | ( (/ /
#  \____|\____) \_/ |_|_(___/|_|_|_|\_||_|\____)_| |_|_|_| |_|\____)
#
# This is the devilsmacine CMake module, A good portion of what makes devilsmachine actually usefull is implemented
# inside of this module.
#
cmake_minimum_required(VERSION 3.2)

#
# This is the primary function used to integrate your CMake project with devilsmachine!!
#
# So, um.. I don't know if CMake has doc comments. But anyway, here's what all of these parameters do:
# (If CMake DOES support doc comments, please comment me! I'm too lazy to Google!!)
#
# source_files:
#   A list of all source files that should be processed with devils machine. You'll probably want to glob a 'content'
#   directory and pass that in here!
#
# generated_files_var:
#   The name of the variable that this function should set. This variable will be set to an array of files which will
#   be generated by devilsmachine during build time.
#
# dm_config_file:
#   Path to the devilsmachine config file to use with devilsmachine.
#
# input_root:
#   Path of the root directory of each source file.
#
# output_root:
#   Root path where each generated file will be placed, based on the relative path of the source file and the input_root
#   parameter.
#
function(add_devilsmachine_commands
    source_files
    generated_files_var
    dm_config_file
    input_root
    output_root
)
    #
    # Get name of python executable. We gotta add a '.exe' prefix if we're on windows, obviously.
    #
    if (WIN32)
        set(sep ";")
        set(python_executable_name "python.exe")
    else()
        set(sep ":")
        set(python_executable_name "python")
    endif()

    #
    # Find our python interpreter, and set up some python related variables. Also, set the current cmake system
    # environment to use our python path when running python commands during the CMake configure phase.
    #
    find_package(PythonInterp 3.6 REQUIRED)
    set(pythonpath "")
    foreach(prefix_path ${CMAKE_PREFIX_PATH})
        set(pythonpath "${pythonpath}${sep}${prefix_path}/lib/python3")
    endforeach()
    set(pythonpath "${pythonpath}${sep}${CMAKE_CURRENT_SOURCE_DIR}")
    set(ENV{PYTHONPATH} "${pythonpath}")

    set(venv_path "${CMAKE_CURRENT_BINARY_DIR}/devilsmachine_venv")
    set(venv_dummyfile_path "${CMAKE_CURRENT_BINARY_DIR}/devilsmachine_venv_dummy")

    #
    # Setup the virtual env for devils machine to use if it hasn't been set up.
    #
    if (NOT EXISTS "${venv_path}")
        message(STATUS "Creating virtual env at ${venv_path}")
        execute_process(
            COMMAND "${PYTHON_EXECUTABLE}" -m ensurepip
            RESULT_VARIABLE update_venv_result
            OUTPUT_VARIABLE update_venv_output
            ERROR_VARIABLE  update_venv_error
        )
        if (NOT update_venv_result EQUAL 0)
            message(FATAL_ERROR "Failed to run ensurepip module: result: ${update_venv_result}. stderr:\n${update_venv_error}")
        endif()

        execute_process(
            COMMAND "${PYTHON_EXECUTABLE}" -m pip install virtualenv
            RESULT_VARIABLE update_venv_result
            OUTPUT_VARIABLE update_venv_output
            ERROR_VARIABLE  update_venv_error
        )
        if (NOT update_venv_result EQUAL 0)
            message(FATAL_ERROR "Failed to install virtualenv with pip: result: ${update_venv_result}. stderr:\n${update_venv_error}")
        endif()

        execute_process(
            COMMAND "${PYTHON_EXECUTABLE}" -m virtualenv "${venv_path}"
            RESULT_VARIABLE update_venv_result
            OUTPUT_VARIABLE update_venv_output
            ERROR_VARIABLE  update_venv_error
        )
        if (NOT update_venv_result EQUAL 0)
            message(FATAL_ERROR "Cannot update devilsmachine venv: result: ${update_venv_result}. stderr:\n${update_venv_error}")
        endif()
    endif()

    #
    # Determine the path of the virutla env python wrapper. It's different on Windows.
    #
    set(venv_python_executable_path "bin/${python_executable_name}")
    if (NOT EXISTS "${venv_python_executable_path}" AND WIN32)
        set(venv_python_executable_path "Scripts/${python_executable_name}")
    endif()

    #
    # Make sure our virtual env has the dependencies listed by the project's dmconfig file installed.
    #
    message(STATUS "Updating dependencies for devilsmachine virtual env")
    execute_process(
        COMMAND
            "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
            "${venv_path}/${venv_python_executable_path}" -m devilsmachine -a update_dependencies
            -c "${dm_config_file}"
            --venv-dummy-file "${venv_dummyfile_path}"
        RESULT_VARIABLE update_venv_dependencies_result
        OUTPUT_VARIABLE update_venv_dependencies_output
        ERROR_VARIABLE  update_venv_dependencies_error
    )
    if (NOT update_venv_dependencies_result EQUAL 0)
        message(FATAL_ERROR "Cannot update devilsmachine venv dependencies: result: ${update_venv_dependencies_result}. stderr:\n${update_venv_dependencies_error}")
    endif()

    #
    # Setup a build-time target that does the same thing as the above step.
    # This way, the project does not need to be re-configured manually if the dependencies change in the dmconfig file.
    #
    add_custom_command(
        OUTPUT "${venv_dummyfile_path}"
        COMMAND
            "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
            "${venv_path}/${venv_python_executable_path}" -m devilsmachine -a update_dependencies
            -c "${dm_config_file}"
            --venv-dummy-file "${venv_dummyfile_path}"
        DEPENDS
            "${dm_config_file}"
    )

    #
    # Query devilsmachine for all of the command line tools we'll need...
    #
    set(all_input_file_args "")
    foreach(source_file ${source_files})
        list(APPEND all_input_file_args "--input-file" "${source_file}")
    endforeach()
    execute_process(
        COMMAND
            "${venv_path}/${venv_python_executable_path}" -m devilsmachine
            -c "${dm_config_file}"
            -a list_tools
            ${all_input_file_args}
        RESULT_VARIABLE list_tools_result
        OUTPUT_VARIABLE list_tools_output
        ERROR_VARIABLE  list_tools_error
    )
    if (NOT list_tools_result EQUAL 0)
        message(FATAL_ERROR "Failed to get required tools from devilsmachine: result: ${list_tools_result}. stderr:\n${list_tools_error}")
    endif()

    #
    # ...and find them with CMake.
    #
    set(tool_args "")
    set(missing_tools "")
    foreach(tool_name ${list_tools_output})
        set(tool_varname "devilsmachine_dependency_${tool_name}_path")
        find_program("${tool_varname}" "${tool_name}")
        set(tool_path "${${tool_varname}}")
        if (tool_path STREQUAL "${tool_varname}-NOTFOUND")
            message(SEND_ERROR "Tool \"${tool_name}\" required by devilsmachine was not found!")
            list(APPEND missing_tools "${tool_name}")
            continue()
        endif()
        list(APPEND tool_args "--tool" "${tool_name}=${tool_path}")
    endforeach()
    list(LENGTH missing_tools missing_tools_len)
    if (missing_tools_len GREATER 0)
        message(FATAL_ERROR "Missing tools required by devilsmachine preprocessors: ${missing_tools}")
    endif()

    #
    # Set up devilsmachine preprocessor targets for all files which will be processed by devilsmachine.
    #
    set(all_output_files "")
    foreach(current_source_file ${source_files})

        #
        # During configure time, query devilsmachine for the outputs of a the current source file.
        #
        execute_process(
            COMMAND
                "${venv_path}/${venv_python_executable_path}" -m devilsmachine
                -c "${dm_config_file}"
                -a list_output_files
                --ir "${input_root}"
                --or "${output_root}"
                --input-file "${current_source_file}"
                ${tool_args}
            OUTPUT_VARIABLE current_output_files
            ERROR_VARIABLE dmerror
            RESULT_VARIABLE dmresult
        )
        if (NOT dmresult EQUAL 0)
            message(SEND_ERROR "Error running devilsmachine. result: ${dmresult}. stderr:\n${dmerror}")
            continue()
        endif()

        #
        # Set up a build target for the outputs given to us by the above commands.
        #
        string(STRIP "${current_output_files}" current_output_files)
        list(APPEND all_output_files "${current_output_files}")
        add_custom_command(
            OUTPUT "${current_output_files}"
            COMMAND
                "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
                "${venv_path}/${venv_python_executable_path}" -m devilsmachine
                -c "${dm_config_file}"
                -a process
                --ir "${input_root}"
                --or "${output_root}"
                --input-file "${current_source_file}"
                ${tool_args}
            DEPENDS "${current_source_file}" "${venv_dummyfile_path}"
        )

    endforeach()

    #
    # "Return" a list of all files that will be generated during build time.
    #
    set("${generated_files_var}" "${all_output_files}" PARENT_SCOPE)


    #
    # Thank you for using devilsmachine! We love you!!!
    #
endfunction()
