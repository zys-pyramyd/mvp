import py_compile
import sys
import traceback

try:
    py_compile.compile('server.py', doraise=True)
    print("Success")
except py_compile.PyCompileError as e:
    # Print the error string which usually contains the line number
    print(str(e))
except Exception as e:
    print(f"Unexpected error: {e}")
