#!/usr/bin/python3
import subprocess
from subprocess import Popen
from subprocess import PIPE
import pathlib
import sys
import re
import time
import os

# Message lambda
fail_message = lambda s1,s2,s3,elapsed: \
'''FAILED test {:3d}, {:5.3f} sec
Output:
{}
Correct:
{}'''.format(s1,elapsed,s2,s3)

# Message lambda
pass_message = lambda s1,elapsed:'Test {:3d} OK, {:5.3f} sec'.format(s1,elapsed)

def run_test(subproc,test):
    input_text = test[0].strip()
    output_text = test[1].strip()

    with Popen(subproc,\
                stdin=PIPE, stdout=PIPE,\
                universal_newlines=True) as proc:

        proc_output = proc.communicate(input_text)[0]
        if proc_output.strip() != output_text.strip():
            return proc_output
        else:
            return None

def main():

    # check arguments
    if len(sys.argv) != 3:
        print('arguments are: executable, tests')
        return

    # process arguments
    subproc = None
    path_to_exe = pathlib.Path(sys.argv[1]).absolute()
    path_to_tests = pathlib.Path(sys.argv[2]).absolute()
    if path_to_exe.suffix == '.py':
        subproc = ['python',str(path_to_exe)]
    else:
        subproc = [str(path_to_exe)]

    devnull = open(os.devnull,'w')
    try:
        subprocess.check_call(subproc,timeout=1, stdout=devnull, stderr=devnull)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('bad process call:',subproc)
        return
    except subprocess.TimeoutExpired:
        pass

    raw_tests = ''
    try:
        with open(str(path_to_tests),'r') as fd:
            raw_tests = fd.read()
    except FileNotFoundError:
        print('file:',path_to_tests, 'not found')
        return

    r = re.compile(r'\s*input begin(.+?)input end\s+?output begin(.+?)output end\s*',flags=re.DOTALL)

    for i,test in enumerate(r.findall(raw_tests)):
        start_time = time.time()
        out = run_test(subproc,test)
        end_time = time.time()
        elapsed = end_time - start_time
        if out:
            print(fail_message(i,out.strip(),test[1].strip(),elapsed))
        else:
            print(pass_message(i,elapsed))

if __name__ == '__main__':
    main()
