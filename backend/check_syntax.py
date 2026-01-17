import py_compile
try:
    py_compile.compile('server.py', doraise=True)
    print("Success")
except py_compile.PyCompileError as e:
    print(e)
except Exception as e:
    print(e)
