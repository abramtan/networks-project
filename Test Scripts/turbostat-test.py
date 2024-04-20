import subprocess

turbostat_command = ["sudo", "turbostat", "--Summary", "--quiet", "--interval", "1", "--num_iterations", "1"]
output = subprocess.run(turbostat_command, capture_output=True, text=True)

turbostat_output = output.stdout
print(turbostat_output)