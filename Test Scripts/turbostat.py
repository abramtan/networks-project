import subprocess

def recursive_fib(n):
    if (n <= 2): return 1
    else: return recursive_fib(n-1)
recursive_fib(1000)
turbostat_command = ["sudo", "turbostat", "--Summary", "--quiet", "--interval", "1", "--num_iterations", "1"]
output = subprocess.run(turbostat_command, capture_output=True, text=True)

turbostat_output = output.stdout
print(turbostat_output)