#!/usr/bin/python
# File: sum_primes.py
# Author: VItalii Vanovschi
# Desc: This program demonstrates parallel computations with pp module
# It calculates the sum of prime numbers below a given integer in parallel
# Parallel Python Software: http://www.parallelpython.com
 
import math, sys, time
import pp,psutil,os
 
def isprime(n):
    """Returns True if n is prime and False otherwise"""
    if not isinstance(n, int):
        raise TypeError("argument passed to is_prime is not of 'int' type")
    if n < 2:
        return False
    if n == 2:
        return True
    max = int(math.ceil(math.sqrt(n)))
    i = 2
    while i <= max:
        if n % i == 0:
            return False
        i += 1
    return True
 
def sum_primes(n):
    """Calculates sum of all primes below given integer n"""
    return sum([x for x in xrange(2,n) if isprime(x)])
 
print """Usage: python sum_primes.py [ncpus]
    [ncpus] - the number of workers to run in parallel,
    if omitted it will be set to the number of processors in the system
"""
def psutil_a():
	cpu_stats=psutil.cpu_stats()
	cpu_1=psutil.cpu_count()
	print cpu_stats
	ISOTIMEFORMAT='%Y-%m-%d %X'
	print  time.strftime(ISOTIMEFORMAT, time.localtime( time.time() ) )
	#print os.popen('top -bi -n 2 -d 0.02').read().split('\n\n\n')[1].split('\n')[2]
	cpu_load=os.popen('top -bi -n 2 -d 0.02').read().split("\n")[0].split(": ")[1].split(", ")
	cpu_now=cpu_load[0]
	cpu_pre=cpu_load[1]
	print cpu_now,cpu_pre
	if float(cpu_now)<=0.50 and float(cpu_pre<0.9):
		return 1
	else:
		return 0
# tuple of all parallel python servers to connect with
ppservers = ("10.10.10.8","x1","x2")
#ppservers = ("10.0.0.1",)
 
if len(sys.argv) > 1:
    ncpus = int(sys.argv[1])
    # Creates jobserver with ncpus workers
    job_server = pp.Server(ncpus, ppservers=ppservers)
else:
    # Creates jobserver with automatically detected number of workers
    job_server = pp.Server(ppservers=ppservers)
 
print "Starting pp with", job_server.get_ncpus(), "workers"
 
# Submit a job of calulating sum_primes(100) for execution.
# sum_primes - the function
# (100,) - tuple with arguments for sum_primes
# (isprime,) - tuple with functions on which function sum_primes depends
# ("math",) - tuple with module names which must be imported before sum_primes execution
# Execution starts as soon as one of the workers will become available
job1 = job_server.submit(sum_primes, (100,), (isprime,), ("math",))
 
# Retrieves the result calculated by job1
# The value of job1() is the same as sum_primes(100)
# If the job has not been finished yet, execution will wait here until result is available
result = job1()
 
print "Sum of primes below 100 is", result
 
start_time = time.time()
 
# The following submits 8 jobs and then retrieves the results
inputs = (100000, 100100, 100200, 100300, 100400, 100500, 100600, 100700)
jobs = [(input, job_server.submit(sum_primes,(input,), (isprime,), ("math",))) for input in inputs]
for input, job in jobs:
	while 1:
		condition=psutil_a()
		if condition==1:
			print "Sum of primes below", input, "is", job()
			break
		else:
			pass
 
print "Time elapsed: ", time.time() - start_time, "s"
job_server.print_stats()

# Parallel Python Software: http://www.parallelpython.com
# 