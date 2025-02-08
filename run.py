import locale
import os.path
import subprocess
import sys
import time

folder = os.curdir
datasets = [
  "dblp_graph.txt",
  # "coauth-DBLP",
  # "coauth-MAG-Geology",
  # "coauth-MAG-History",
  # "coauth-DBLP-full",
  # "coauth-MAG-Geology-full",
  # "coauth-MAG-History-full",
  # "contact-high-school",
  # "contact-primary-school",
  # "email-Enron",
  # "email-Eu",
  # "email-Enron-full",
  # "email-Eu-full",
  # "NDC-classes",
  # "NDC-substances",
  # "NDC-classes-full",
  # "NDC-substances-full",
  # "tags-ask-ubuntu",
  # "tags-math-sx",
  # "threads-ask-ubuntu",
  # "threads-math-sx",
]
big_datasets = [
  # "congress-bills",
  "congress-bills-full",
  "DAWN",
  "tags-stack-overflow",
  "threads-stack-overflow",
]
argslist = [
    ("GraphInfo", None),
    ("Baseline", None),
    ("PushForward", None),
    ("PushForward", ["SKIP_INTERSECT_VERTEX"]),
    ("PrefixForest", None),
    ("PrefixForest", ["PROGRESSIVE_COUNTING"]),
    ("PrefixForest", ["PROGRESSIVE_COUNTING", "USING_BITMAP"]),
]


def generate_singlefile_compile_command(filename, compile_flags=None, ):
    def generate_str_compile_flags():
        if not compile_flags:
            return ''
        return ' '.join(f"-D{flag}" for flag in compile_flags)
    if sys.platform.startswith('darwin'):
        return (f"g++-14 -std=c++17 -O3 -Iinclude {generate_str_compile_flags()}"
                f" {os.path.join(os.curdir, 'src', filename + '.cpp')}"
                f" -o {os.path.join(os.curdir, filename + '.exe')}")
    else:
        return (f"g++ -std=c++17 -O3 -Iinclude {generate_str_compile_flags()}"
            f" {os.path.join(os.curdir, 'src', filename + '.cpp')}"
            f" -o {os.path.join(os.curdir, filename + '.exe')}")


def generate_run_command(filename, dataset):
    path = os.path.join(folder, dataset)
    return f"{os.path.join(os.curdir, filename + '.exe')} {path}"


def run_one_command(cmd, encoding=locale.getpreferredencoding()):
    process = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding=encoding)
    for stdout_line in process.stdout:
        print(stdout_line, end='')  # 打印标准输出
    for stderr_line in process.stderr:
        print(stderr_line, end='', file=sys.stderr)  # 打印标准错误

    process.wait()  # 等待命令执行完成，并获取返回码
    if process.returncode != 0:  # 可以不要
        print(f"Command {cmd} failed with return code {process.returncode}")


def run_one_command_with_timeout(cmd, timeout=25*60*60, encoding=locale.getpreferredencoding()):  # 25h
    process = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding=encoding)
    def stream_output(proc):
        for stdout_line in iter(proc.stdout.readline, ""):
            print(stdout_line, end="")  # 打印标准输出
        for stderr_line in iter(proc.stderr.readline, ""):
            print(stderr_line, end="")  # 打印标准错误

    # 等待进程完成，或超时
    start_time = time.time()
    while process.poll() is None:  # 判断进程是否已完成
        if time.time() - start_time >= timeout:
            process.kill()  # 超时后杀死进程
            print(f"Process timed out and was killed after {timeout / 3600} hours.")
            break
        stream_output(process)  # 实时打印输出

    if process.poll() is not None:  # 如果进程已完成
        if process.returncode == 0:
            print("Process completed successfully.")
        else:
            print(f"Process ended with errors (Return code: {process.returncode}).")


def compile_and_run(filename, compile_flags, dataset, run_func):
    cpl_cmd = generate_singlefile_compile_command(filename, compile_flags)
    print("+ " + cpl_cmd, file=sys.stderr)
    run_one_command(cpl_cmd, encoding='utf-8')

    run_cmd = generate_run_command(filename, dataset)
    print("+ " + run_cmd, file=sys.stderr)
    run_func(run_cmd)


def compile_and_run_twice(filename, compile_flags, dataset, run_func):
    cpl_cmd = generate_singlefile_compile_command(filename, compile_flags)
    print("+ " + cpl_cmd, file=sys.stderr)
    run_one_command(cpl_cmd, encoding='utf-8')

    run_cmd = generate_run_command(filename, dataset)
    print("+ " + run_cmd, file=sys.stderr)
    run_func(run_cmd)
    print("+ " + run_cmd, file=sys.stderr)
    run_func(run_cmd)


def run_datasets():
    print("NORMAL DATASETS")
    for dataset in datasets:
        for filename, compile_flags in argslist:
            print('================================================================================')
            compile_and_run(filename, compile_flags, dataset,
                            run_one_command)

    for dataset in datasets:
        for filename, compile_flags in argslist[1:]:
            print('================================================================================')
            compile_and_run_twice(filename, compile_flags, dataset,
                                  run_one_command)


def run_big_datasets():
    print("BIG DATASETS")
    for dataset in big_datasets:
        print('================================================================================')
        compile_and_run(*argslist[0], dataset,
                        run_one_command)
        for filename, compile_flags in argslist[1:]:
            print('================================================================================')
            compile_and_run(filename, compile_flags, dataset,
                            run_one_command_with_timeout)

    for dataset in big_datasets:
        for filename, compile_flags in argslist[1:]:
            print('================================================================================')
            compile_and_run_twice(filename, compile_flags, dataset,
                                  run_one_command_with_timeout)


if __name__ == '__main__':
    run_datasets()
    # run_big_datasets()
