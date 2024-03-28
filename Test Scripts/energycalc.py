from pyJoules.energy_meter import measure_energy
from pyJoules.device.rapl_device import RaplPackageDomain
from pyJoules.device.rapl_device import RaplUncoreDomain

@measure_energy(domains=[RaplPackageDomain(1)])
def recursive_fib(n):
    if (n <= 2): return 1
    else: return recursive_fib(n-1)
 
print(recursive_fib(40))   
#energyusage.evaluate(recursive_fib, 40)