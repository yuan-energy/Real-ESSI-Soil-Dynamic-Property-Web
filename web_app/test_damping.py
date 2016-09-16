from subprocess import call
import shlex as sh
from numpy import loadtxt, linspace, pi, insert
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



# max_strain = float(form.MaxPureShearStrain)
max_strain = float(0.03)
Nstep_ = 10
strain_step = linspace(max_strain/Nstep_, max_strain, Nstep_)

damping_ratio = []
stepss = 1E2
argv_part = [stepss  , 1E5  , 1.2  , 1E5  , 900  , 0.0  , 1E7  , 0.3  , 2000 , 1000 , 0.0  , 0.0]
for x in xrange(0, Nstep_):
	this_strain = strain_step[x] 
	arg_part = ' '.join([str(x) for x in argv_part])
	arg = str(this_strain) + ' '+ arg_part
	command = "script -c './test_dpaf " + arg + " ' log" 
	call(sh.split(command))
	# read data
	strain_stress = loadtxt('strain_stress.txt')
	strain = strain_stress[:,0]
	stress = strain_stress[:,1]
	max_y = max(stress)
	# calc Ws
	Ws = 0.5 * max_y * this_strain 
	# calc Wd
	loop_area = 0 
	strain_step_len = strain[1] - strain[0]
	min_y = min(stress)
	stepss = int(stepss)
	for x in xrange(stepss, 3*stepss):
		loop_area = loop_area - strain_step_len * (stress[x] - min_y)
	for x in xrange(3*stepss, 5*stepss):
		loop_area = loop_area + strain_step_len * (stress[x] - min_y)
	Wd = loop_area
	print Wd
	# calc damping
	this_damping = Wd / 4.0 / pi / Ws
	damping_ratio.append(this_damping)


pl_strain = insert(strain_step, 0, 0 )
pl_damping = insert(damping_ratio, 0, 0 )
plt.plot(pl_strain, pl_damping)
plt.xlabel("strain (unitless) ")
plt.ylabel("Damping ratio (unitless)")
plt.savefig("DPAF_damping_ratio.png", bbox_inches='tight')