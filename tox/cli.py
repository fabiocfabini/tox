from typing import Tuple, Dict

import os
import sys
import glob
import subprocess

COLOR_RED = "\033[1;31m"
COLOR_BLUE = "\033[1;34m"
COLOR_GREEN = "\033[1;32m"
RESET_COLOR = "\033[0;0m"

OptArgs = Dict[str, str]
ReqArgs = Dict[str, bool]

def print_help():
    print(f"{COLOR_BLUE}Usage{RESET_COLOR}: python tox.py [sim|com] [OPTIONS]")
    print()
    print(f"{COLOR_BLUE}ARGUMENTS{RESET_COLOR}:")
    print(f"  {COLOR_GREEN}com{RESET_COLOR}    Compile the program to EWVM.")
    print(f"  {COLOR_GREEN}test{RESET_COLOR}   Compile and simulate the test programs. Compare the outputs with the expected outputs.")
    print(f"  {COLOR_GREEN}euler{RESET_COLOR}  Check the solutions of the Euler problems.")
    print()
    print(f"{COLOR_BLUE}OPTIONS{RESET_COLOR}:")
    print(f"  {COLOR_GREEN}-h{RESET_COLOR}, {COLOR_GREEN}--help{RESET_COLOR}"       +" "*14 +   "Show this help message and exit.")
    print(f"  {COLOR_GREEN}-i{RESET_COLOR}, {COLOR_GREEN}--input{RESET_COLOR}"      +" "*13 +   "Specify the input file.")
    print(f"  {COLOR_GREEN}-o{RESET_COLOR}, {COLOR_GREEN}--ouput{RESET_COLOR}"      +" "*13 +   "Specify the output file.")
    print(f"  {COLOR_GREEN}-r{RESET_COLOR}, {COLOR_GREEN}--run{RESET_COLOR}"        +" "*15 +   "Run the compiled program. (Only for com")
    print(f"  {COLOR_GREEN}-rec{RESET_COLOR}, {COLOR_GREEN}--record{RESET_COLOR}"       +" "*10 +   "Record the output of the executed programs. (Only for 'test' command)")
    print(f"  {COLOR_GREEN}-clc{RESET_COLOR}, {COLOR_GREEN}--clean-up{RESET_COLOR}"     +" "*8 +   "Clear the output of the executed programs. (Only for 'test' command)")
    print(f"  {COLOR_GREEN}-v{RESET_COLOR}, {COLOR_GREEN}--verbose{RESET_COLOR}"        +" "*11 +   "Show verbose output.")

def error(msg: str):
    print(f"{COLOR_RED}Error:{RESET_COLOR}", msg)
    print_help()
    sys.exit(1)

def echo_cmd(cmd: str) -> Tuple[bool, str]:
    print(f"{COLOR_BLUE}[CMD]{RESET_COLOR} {cmd}")
    if cmd.startswith("diff"):
        output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8")
        if output != "":
            return False, output
    else:
        completed_process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
        if completed_process.returncode != 0:
            return False, completed_process.stderr.decode("utf-8")
    return True, ""

def info_cmd(msg: str):
    print(f"{COLOR_BLUE}[INFO]{RESET_COLOR} {msg}")

def prepare_cmd_args() -> Tuple[OptArgs, ReqArgs]:
    if "-h" in sys.argv or "--help" in sys.argv: print_help(); sys.exit(0)

    # Handle Optional Arguments
    input_file = sys.argv[sys.argv.index("-i") + 1] if "-i" in sys.argv else None
    output_file = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else None
    run = True if "-r" in sys.argv else False
    rec = True if "-rec" in sys.argv else False
    clc = True if "-clc" in sys.argv else False
    verbose = True if "-v" in sys.argv else False #TODO: Implement verbose output

    opt_args = {"-i": input_file, "-o": output_file, "-r": run, "-v": verbose, "-rec": rec, "-clc": clc}

    # Handle Required Arguments
    com = True if "com" in sys.argv else False 
    test = True if "test" in sys.argv else False 
    euler = True if "euler" in sys.argv else False 
    modes = [com, test, euler]
    if len(list(filter(bool, modes))) == 0: error("No execution mode specified. (com, test, euler)")
    if len(list(filter(bool, modes))) >  1: error("Multiple execution modes specified.")

    req_args = {"com": com, "test": test, "euler": euler}

    return opt_args, req_args

def com_execute(opt_args: OptArgs):
    from tox import parser

    if not opt_args["-i"]:
        error("No input file specified.")
    else:
        with open(opt_args["-i"], "r") as f:
            info_cmd(f"Compiling {opt_args['-i']}")
            content = f.read()
            parser.input = content
            output = parser.parse(content)
            if not opt_args["-o"]:
                opt_args["-o"] = os.path.splitext(opt_args["-i"])[0] + ".vms"
            with open(opt_args["-o"], "w") as f:
                f.write(output)
            if opt_args["-r"]:
                ret = echo_cmd(f"vms {opt_args['-o']}")
                if not ret[0]:
                    print(ret[1])
                    sys.exit(1)

def test_execute(opt_args: OptArgs):
    input_files = glob.glob("test/*.tox")
    output_files = [os.path.splitext(input_file)[0]+".vms" for input_file in input_files]
    num_tests = len(input_files)
    failed_tests: list[Tuple[str, str]] = []

    opt_args["-r"] = False
    if opt_args["-rec"]:
        for input_file, output_file in zip(input_files, output_files):
            print(COLOR_GREEN + "-"*80 + RESET_COLOR)
            opt_args["-i"] = input_file
            opt_args["-o"] = output_file
            echo_cmd(f"tox com -i {input_file} -o {output_file}")
            echo_cmd(f"vms {output_file} > {os.path.splitext(output_file)[0]}_com_expected.out")
    else:
        for input_file, output_file in zip(input_files, output_files):
            print(COLOR_GREEN + "-"*80 + RESET_COLOR)
            ret = echo_cmd(f"tox com -i {input_file} -o {output_file}")
            if not ret[0]:
                num_tests -= 1
                failed_tests.append((input_file, ret[1]))
                continue
            ret = echo_cmd(f"vms {output_file} > {os.path.splitext(output_file)[0]}_com.out")
            if not ret[0]:
                num_tests -= 1
                failed_tests.append((input_file, ret[1]))
                continue
            ret = echo_cmd(f"diff {os.path.splitext(output_file)[0]}_com_expected.out {os.path.splitext(output_file)[0]}_com.out")
            if not ret[0]:
                num_tests -= 1
                failed_tests.append((input_file, ret[1]))
        if opt_args['-clc']:
            print(COLOR_GREEN + "-"*80 + RESET_COLOR)
            echo_cmd("rm test/*_com.out")
            echo_cmd("rm test/*.vms")
        print(COLOR_GREEN + "-"*80 + RESET_COLOR)
        print(f"{COLOR_GREEN}Passed: {num_tests}.{RESET_COLOR}", end=" ")
        print(f"{COLOR_RED}Failed: {len(failed_tests)}.{RESET_COLOR}")
        for failed_test, error_msg in failed_tests:
            print(f"{COLOR_RED}Failed: {failed_test}.{RESET_COLOR}")
            print(f"{COLOR_RED}{error_msg}{RESET_COLOR}")

def euler_execute(opt_args: OptArgs):
    input_files = glob.glob("euler/problem*/*.tox")
    output_files = [os.path.splitext(input_file)[0]+".vms" for input_file in input_files]
    num_tests = len(input_files)
    failed_tests: list[Tuple[str, str]] = []

    for input_file, output_file in zip(input_files, output_files):
        print(COLOR_GREEN + "-"*80 + RESET_COLOR)
        ret = echo_cmd(f"tox com -i {input_file} -o {output_file}")
        if not ret[0]:
            num_tests -= 1
            failed_tests.append((input_file, ret[1]))
            continue
        ret = echo_cmd(f"vms {output_file} > {os.path.splitext(output_file)[0]}.out")
        if not ret[0]:
            num_tests -= 1
            failed_tests.append((input_file, ret[1]))
            continue
        ret = echo_cmd(f"diff {os.path.splitext(output_file)[0]}.ans {os.path.splitext(output_file)[0]}.out")
        if not ret[0]:
            num_tests -= 1
            failed_tests.append((input_file, ret[1]))
    if opt_args['-clc']:
        print(COLOR_GREEN + "-"*80 + RESET_COLOR)
        echo_cmd("rm euler/problem*/*.out")
        echo_cmd("rm euler/problem*/*.vms")
    print(COLOR_GREEN + "-"*80 + RESET_COLOR)
    print(f"{COLOR_GREEN}Passed: {num_tests}.{RESET_COLOR}", end=" ")
    print(f"{COLOR_RED}Failed: {len(failed_tests)}.{RESET_COLOR}")
    for failed_test, error_msg in failed_tests:
        print(f"{COLOR_RED}Failed: {failed_test}.{RESET_COLOR}")
        print(f"{COLOR_RED}{error_msg}{RESET_COLOR}")

def execute(opt_args: OptArgs, req_args: ReqArgs):
    if req_args["com"]: com_execute(opt_args)
    if req_args["test"]: test_execute(opt_args)
    if req_args["euler"]: euler_execute(opt_args)

def tox_cli():
    opt_args, req_args = prepare_cmd_args()
    execute(opt_args, req_args)