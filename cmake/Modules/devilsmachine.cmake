cmake_minimum_required(VERSION 3.2)

function(add_devilsmachine_commands
    source_files
    generated_files_var
    dm_config_file
    input_root
    output_root
)
    if (WIN32)
        set(sep ";")
    else()
        set(sep ":")
    endif()

    find_package(PythonInterp 3.6 REQUIRED)
    set(pythonpath "")
    foreach(prefix_path ${CMAKE_PREFIX_PATH})
        set(pythonpath "${pythonpath}${sep}${prefix_path}/lib/python3")
    endforeach()
    set(pythonpath "${pythonpath}${sep}${CMAKE_CURRENT_SOURCE_DIR}")
    set(ENV{PYTHONPATH} "${pythonpath}")

    set(venv_path "${CMAKE_CURRENT_BINARY_DIR}/devilsmachine_venv")
    set(venv_dummyfile_path "${CMAKE_CURRENT_BINARY_DIR}/devilsmachine_venv_dummy")

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

    message(STATUS "Updating dependencies for devilsmachine virtual env")
    execute_process(
        COMMAND
            "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
            "${venv_path}/bin/python" -m devilsmachine -a update_dependencies
            -c "${dm_config_file}"
            --venv-dummy-file "${venv_dummyfile_path}"
        RESULT_VARIABLE update_venv_dependencies_result
        OUTPUT_VARIABLE update_venv_dependencies_output
        ERROR_VARIABLE  update_venv_dependencies_error
    )
    if (NOT update_venv_dependencies_result EQUAL 0)
        message(FATAL_ERROR "Cannot update devilsmachine venv dependencies: result: ${update_venv_dependencies_result}. stderr:\n${update_venv_dependencies_error}")
    endif()

    add_custom_command(
        OUTPUT "${venv_dummyfile_path}"
        COMMAND
            "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
            "${venv_path}/bin/python" -m devilsmachine -a update_dependencies
            -c "${dm_config_file}"
            --venv-dummy-file "${venv_dummyfile_path}"
        DEPENDS
            "${dm_config_file}"
    )

    set (all_output_files "")
    foreach(current_source_file ${source_files})
        execute_process(
            COMMAND
                "${venv_path}/bin/python" -m devilsmachine
                -c "${dm_config_file}"
                -a list_output_files
                --ir "${input_root}"
                --or "${output_root}"
                --input-file "${current_source_file}"
            OUTPUT_VARIABLE current_output_files
            ERROR_VARIABLE dmerror
            RESULT_VARIABLE dmresult
        )
        if (NOT dmresult EQUAL 0)
            message(SEND_ERROR "Error running devilsmachine. result: ${dmresult}. stderr:\n${dmerror}")
            continue()
        endif()
        string(STRIP "${current_output_files}" current_output_files)
        list(APPEND all_output_files "${current_output_files}")
        add_custom_command(
            OUTPUT "${current_output_files}"
            COMMAND
                "${CMAKE_COMMAND}" -E env "PYTHONPATH=${pythonpath}"
                "${venv_path}/bin/python" -m devilsmachine
                -c "${dm_config_file}"
                -a process
                --ir "${input_root}"
                --or "${output_root}"
                --input-file "${current_source_file}"
            DEPENDS "${current_source_file}" "${venv_dummyfile_path}"
        )
    endforeach()
    set("${generated_files_var}" "${all_output_files}" PARENT_SCOPE)
endfunction()
