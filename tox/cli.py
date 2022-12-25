from typing import Tuple, Dict, Union

import os
import sys
import glob
import subprocess

from tqdm import tqdm

from tox.utils.colors import *

OptArgs = Dict[str, str]
ReqArgs = Dict[str, Union[str, bool]]
possible_exec_modes = ["run", "build", "test", "euler"]
possible_opt_args = ["-o","--output", "-v", "--verbose", "-rec", "--record", "-clc", "--clean-up"]
recognized_args = possible_exec_modes + possible_opt_args

def print_help():
    print(f"{COLOR_BLUE}Usage{RESET_COLOR}: tox [EXECUTION MODES] [ARGUMENTS] [OPTIONS]")
    print()
    print(f"{COLOR_BLUE}ARGUMENTS{RESET_COLOR}:")
    print(f"  {COLOR_GREEN}input{RESET_COLOR}  The input file. Must be a '.tox' file.")
    print()
    print(f"{COLOR_BLUE}EXECUTION MODES{RESET_COLOR}:")
    print(f"  {COLOR_GREEN}run{RESET_COLOR}    Compiles and runs the program.")
    print(f"  {COLOR_GREEN}build{RESET_COLOR}  Compile the program to EWVM.")
    print(f"  {COLOR_GREEN}euler{RESET_COLOR}  Check the solutions of the Euler problems.")
    print(f"  {COLOR_GREEN}test{RESET_COLOR}   Compile and simulate the test programs. Compare the outputs with the expected outputs.")
    print()
    print(f"{COLOR_BLUE}OPTIONS{RESET_COLOR}:")
    print(f"  {COLOR_GREEN}-h{RESET_COLOR}, {COLOR_GREEN}--help{RESET_COLOR}"       +" "*14 +   "Show this help message and exit.")
    print(f"  {COLOR_GREEN}-o{RESET_COLOR}, {COLOR_GREEN}--ouput{RESET_COLOR}"      +" "*13 +   "Specify the output file.")
    print(f"  {COLOR_GREEN}-rec{RESET_COLOR}, {COLOR_GREEN}--record{RESET_COLOR}"       +" "*10 +   "Record the output of the executed programs. (Only for 'test' command)")
    print(f"  {COLOR_GREEN}-clc{RESET_COLOR}, {COLOR_GREEN}--clean-up{RESET_COLOR}"     +" "*8 +   "Clear the output of the executed programs. (Only for 'test' command)")
    print(f"  {COLOR_GREEN}-v{RESET_COLOR}, {COLOR_GREEN}--verbose{RESET_COLOR}"        +" "*11 +   "Show verbose output.")

def error(msg: str, verbose: bool = False):
    print(f"{COLOR_RED}[ERROR]{RESET_COLOR}", msg)
    sys.exit(1)

def echo_cmd(cmd: str, verbose: bool = False) -> Tuple[bool, str]:
    if verbose: print(f"{COLOR_BLUE}[CMD]{RESET_COLOR} {cmd}")
    if cmd.startswith("diff"):
        output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8")
        if output != "":
            return False, output
    else:
        completed_process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
        if completed_process.returncode != 0:
            return False, completed_process.stderr.decode("utf-8")
    return True, ""

def warn_cmd(msg: str, verbose: bool = False):
    if verbose: print(f"{COLOR_YELLOW}[WARN]{RESET_COLOR} {msg}")

def info_cmd(msg: str, verbose: bool = False):
    if verbose: print(f"{COLOR_BLUE}[INFO]{RESET_COLOR} {msg}")

def prepare_cmd_args() -> Tuple[OptArgs, ReqArgs]:
    if "-h" in sys.argv or "--help" in sys.argv: print_help(); sys.exit(0)

    # Handle Optional Arguments
    input_file = None
    for arg in sys.argv[1:]:
        if arg.endswith(".tox"):
            input_file = arg
            continue
        if arg not in recognized_args:
            if "-o" in sys.argv and sys.argv.index("-o") == sys.argv.index(arg) - 1:
                continue
            error(f"Unrecognized argument: {arg}. Use -h or --help to see the help message.")

    output_file = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else None
    rec = True if "-rec" in sys.argv else False
    clc = True if "-clc" in sys.argv else False
    verbose = True if "-v" in sys.argv else False #TODO: Implement verbose output

    if verbose: warn_cmd("Verbose output is not implemented yet.")

    opt_args = {"-o": output_file, "-v": verbose, "-rec": rec, "-clc": clc}

    # Handle Required Arguments
    run   = True if "run"   in sys.argv else False 
    build = True if "build" in sys.argv else False 
    test  = True if "test"  in sys.argv else False 
    euler = True if "euler" in sys.argv else False 
    modes = [run, build, test, euler]
    if len(list(filter(bool, modes))) == 0: error(f"No execution mode specified. (run, build, test, euler)")
    if len(list(filter(bool, modes))) >  1: error("Multiple execution modes specified.")

    req_args = {"input": input_file, "run": run, "build": build, "test": test, "euler": euler}

    return opt_args, req_args

def run_execute(req_args: ReqArgs, opt_args: OptArgs):
    from tox import parser

    if not req_args["input"]: error("No input file specified.")
    if not opt_args["-o"]:
        opt_args["-o"] = os.path.splitext(req_args['input'])[0] + ".vms"
    build_execute(req_args, opt_args)
    info_cmd(f"Running {opt_args['-o']}", verbose=opt_args["-v"])
    ret = echo_cmd(f"vms {opt_args['-o']}", verbose=opt_args["-v"])
    if not ret[0]:
        print(ret[1])
        sys.exit(1)

def build_execute(req_args: ReqArgs, opt_args: OptArgs):
    from tox import parser

    if not req_args["input"]: error("No input file specified.")
    with open(req_args["input"], "r") as f:
        info_cmd(f"Compiling {req_args['input']}", verbose=opt_args["-v"])
        content = f.read()
        parser.input = content
        output = parser.parse(content)
        if not opt_args["-o"]:
            opt_args["-o"] = os.path.splitext(req_args['input'])[0] + ".vms"
        with open(opt_args["-o"], "w") as f:
            f.write(output)

def test_execute(req_args: ReqArgs, opt_args: OptArgs):
    input_files = glob.glob("test/*.tox")
    output_files = [os.path.splitext(input_file)[0]+".vms" for input_file in input_files]
    num_tests = len(input_files)
    failed_tests: list[Tuple[str, str]] = []

    iterable = tqdm(zip(input_files, output_files), total=len(input_files), desc="Testing", colour="green") if not opt_args["-v"] else zip(input_files, output_files)
    if opt_args["-rec"]:
        for input_file, output_file in iterable:
            if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
            req_args["input"] = input_file
            opt_args["-o"] = output_file
            echo_cmd(f"tox build {input_file} -o {output_file}", verbose=opt_args['-v'])
            echo_cmd(f"vms {output_file} > {os.path.splitext(output_file)[0]}_com_expected.out", verbose=opt_args['-v'])
    else:
        for input_file, output_file in iterable:
            if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
            ret = echo_cmd(f"tox build {input_file} -o {output_file}", verbose=opt_args['-v'])
            if not ret[0]:
                num_tests -= 1
                failed_tests.append((input_file, ret[1]))
                continue
            ret = echo_cmd(f"vms {output_file} > {os.path.splitext(output_file)[0]}_com.out", verbose=opt_args['-v'])
            if not ret[0]:
                num_tests -= 1
                failed_tests.append((input_file, ret[1]))
                continue
            ret = echo_cmd(f"diff {os.path.splitext(output_file)[0]}_com_expected.out {os.path.splitext(output_file)[0]}_com.out", verbose=opt_args['-v'])
            if not ret[0]:
                num_tests -= 1
                failed_tests.append((input_file, ret[1]))
        if opt_args['-clc']:
            if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
            echo_cmd("rm test/*_com.out", verbose=opt_args['-v'])
            echo_cmd("rm test/*.vms", verbose=opt_args['-v'])
        if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
        for failed_test, error_msg in failed_tests:
            print(f"{COLOR_RED}Failed: {failed_test}.{RESET_COLOR}")
            print(f"{COLOR_RED}{error_msg}{RESET_COLOR}")
        if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
        print(f"{COLOR_GREEN}Passed: {num_tests}.{RESET_COLOR}", end=" ")
        print(f"{COLOR_RED}Failed: {len(failed_tests)}.{RESET_COLOR}")

def euler_execute(req_args: ReqArgs, opt_args: OptArgs):
    input_files = glob.glob("euler/problem*/*.tox")
    output_files = [os.path.splitext(input_file)[0]+".vms" for input_file in input_files]
    num_tests = len(input_files)
    failed_tests: list[Tuple[str, str]] = []

    iterable = tqdm(zip(input_files, output_files), total=len(input_files), desc="Testing", colour="green") if not opt_args["-v"] else zip(input_files, output_files)
    for input_file, output_file in iterable:
        if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
        ret = echo_cmd(f"tox build {input_file} -o {output_file}", verbose=opt_args['-v'])
        if not ret[0]:
            num_tests -= 1
            failed_tests.append((input_file, ret[1]))
            continue
        ret = echo_cmd(f"vms {output_file} > {os.path.splitext(output_file)[0]}.out", verbose=opt_args['-v'])
        if not ret[0]:
            num_tests -= 1
            failed_tests.append((input_file, ret[1]))
            continue
        ret = echo_cmd(f"diff {os.path.splitext(output_file)[0]}.ans {os.path.splitext(output_file)[0]}.out", verbose=opt_args['-v'])
        if not ret[0]:
            num_tests -= 1
            failed_tests.append((input_file, ret[1]))
    if opt_args['-clc']:
        if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
        echo_cmd("rm euler/problem*/*.out")
        echo_cmd("rm euler/problem*/*.vms")
    if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
    for failed_test, error_msg in failed_tests:
        print(f"{COLOR_RED}Failed: {failed_test}.{RESET_COLOR}")
        print(f"{COLOR_RED}{error_msg}{RESET_COLOR}")
    if opt_args['-v']: print(COLOR_GREEN + "-"*80 + RESET_COLOR)
    print(f"{COLOR_GREEN}Passed: {num_tests}{RESET_COLOR}", end=" ")
    print(f"{COLOR_RED}Failed: {len(failed_tests)}.{RESET_COLOR}")

def execute(opt_args: OptArgs, req_args: ReqArgs):
    if req_args["run"]  : run_execute(req_args, opt_args)
    if req_args["build"]: build_execute(req_args, opt_args)
    if req_args["test"] : test_execute(req_args, opt_args)
    if req_args["euler"]: euler_execute(req_args, opt_args)

def tox_cli():
    opt_args, req_args = prepare_cmd_args()
    execute(opt_args, req_args)