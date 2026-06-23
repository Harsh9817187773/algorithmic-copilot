import subprocess
import os
from langchain_core.tools import tool

@tool
def execute_cpp_code(code: str, test_input: str = "") -> str:
    """Compiles and executes C++ code. Optionally pass test_input to feed standard input (stdin) to the program."""
    file_name = "temp_solution.cpp"
    out_name = "./temp_solution.out"
    
    # 1. Write the code to a file
    with open(file_name, "w") as f:
        f.write(code)
        
    # 2. Compile the code
    compile_result = subprocess.run(["g++", "-O2", file_name, "-o", out_name], capture_output=True, text=True)
    if compile_result.returncode != 0:
        return f"COMPILATION FAILED:\n{compile_result.stderr}"
        
    # 3. Execute the binary and pass the test_input
    try:
        run_result = subprocess.run([out_name], input=test_input, capture_output=True, text=True, timeout=5)
        return f"EXECUTION SUCCESSFUL.\nStandard Output:\n{run_result.stdout}\nStandard Error:\n{run_result.stderr}"
    except subprocess.TimeoutExpired:
        return "EXECUTION TIMED OUT: The program took longer than 5 seconds to run. Did you forget to provide test_input for cin?"
    finally:
        # Cleanup
        if os.path.exists(file_name): os.remove(file_name)
        if os.path.exists(out_name): os.remove(out_name)