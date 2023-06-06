import subprocess
from multiprocessing import Pool, current_process

prompts = ["What is your name?", "How old are you?", "Where do you live?"]


def run_tax(prompt):
    print(f"Processing {prompt} in {current_process().name}")
    cmd = f"tax '{prompt}'"
    result = subprocess.check_output(cmd, shell=True)
    return result.decode()


if __name__ == "__main__":
    with Pool(processes=len(prompts)) as pool:
        results = pool.map(run_tax, prompts)
    for r in results:
        print(r)
