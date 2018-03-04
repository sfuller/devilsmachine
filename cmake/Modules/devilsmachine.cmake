cmake_minimum_required(VERSION 3.2)

function(add_devilsmachine_commands
    source_files
    generated_files_var
    dm_config_file
    input_root
    output_root
)
    find_package(PythonInterp 3.6 REQUIRED)
    set(pythonpath "")
    foreach(prefix_path ${CMAKE_PREFIX_PATH})
        set(pythonpath "${pythonpath}:${prefix_path}/lib/python3")
    endforeach()
    set(pythonpath "${pythonpath}:${CMAKE_CURRENT_SOURCE_DIR}")
    set(ENV{PYTHONPATH} "${pythonpath}")

    set (all_output_files "")
    foreach(current_source_file ${source_files})
        execute_process(
            COMMAND
                "${PYTHON_EXECUTABLE}" -m devilsmachine
                -c "${dm_config_file}"
                -a list_output_files
                --ir "${input_root}"
                "${current_source_file}"
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
                "${PYTHON_EXECUTABLE}" -m devilsmachine
                -c "${dm_config_file}"
                -a process
                --ir "${input_root}"
                --or "${output_root}"
                "${current_source_file}"
            DEPENDS "${current_content_file}"
        )
    endforeach()
    set("${generated_files_var}" "${all_output_files}" PARENT_SCOPE)
endfunction()
