import web
from subprocess import call
import shlex as sh
from numpy import loadtxt, linspace, pi, insert
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

render = web.template.render('templates/', base="layout")
class VMLH(object):
	def __init__(self):
		self.outfileNum = 0

	def GET(self):
	    return render.VMLH_default()

	def POST(self):
		form = web.input()
		mylog = open('log.txt','w')
		for key in form.keys():
			mylog.write(key)
			mylog.write('\n')
		for value in form.values():
			mylog.write(value)
			mylog.write('\n')
        
		argv = []
		argv.append(float(form.MaxPureShearStrain))
		argv.append(float(form.Num_Of_Subincrement_monotonic_loading))
		argv.append(float(form.Max_Num_Of_Subincrement))
		argv.append(float(form.vonMises_radius))
		argv.append(float(form.kinematic_hardening_rate))
		argv.append(float(form.isotropic_hardening_rate))
		argv.append(float(form.elastic_modulus))
		argv.append(float(form.poisson_ratio))
		argv.append(float(form.mass_density))

        # Call the executable to run Gauss point
		mylog.write("Start calculation! ")
		arg = ' '.join([str(x) for x in argv])
		command = "script -c './test_vmlh " + arg + " ' log" 
		call(sh.split(command))

		# ============================================
		# Figure 1
		# Plot the stress-strain curves
		# ============================================
		inFilename = 'VMLH_strain_stress.txt'
		strain_stress = loadtxt(inFilename)
		strain = strain_stress[:,0]
		stress = strain_stress[:,1]
		plt.clf()
		plt.plot(strain, stress)
		plt.xlabel("strain (unitless) ")
		plt.ylabel("stress (Pa)")
		plt.savefig("VMLH_strain_stress.png", bbox_inches='tight')

		# ============================================
		# Figure 2
		# Plot the G/Gmax curves
		# ============================================
		E_ = float(form.elastic_modulus)
		nu_ = float(form.poisson_ratio)
		Gmax = E_/2.0 / (1+nu_)
		mylog.write("Gmax = " + str(Gmax))
		Num_increase_step = int(float(form.Num_Of_Subincrement_monotonic_loading))
		G_over_Gmax = []
		G_over_Gmax.append(1)
		gamma = []
		for epsilon in strain:
			gamma.append(epsilon*2.0)
		for x in xrange(1,Num_increase_step+1):
			G_ = (stress[x]-stress[0]) / (gamma[x]-gamma[0])
			G_Gmax = G_ / Gmax
			G_over_Gmax.append(G_Gmax)
		mylog.write("information for Gmax: ")
		mylog.write("size(G_over_Gmax)       = " + str(len(G_over_Gmax)))
		mylog.write("size(Num_increase_step) = " + str(Num_increase_step))

		plt.clf()
		plt.plot(strain[0:Num_increase_step+1] , G_over_Gmax )
		plt.xlabel("strain (unitless) ")
		plt.ylabel("G/Gmax (unitless)")
		minY = 0
		maxY = max(G_over_Gmax)*1.05
		plt.ylim([minY, maxY])
		plt.xscale('log')
		plt.savefig("VMLH_G_Gmax.png", bbox_inches='tight')

		# ============================================
		# Figure 3
		# Plot the damping ratio curves
		# ============================================
		max_strain = float(form.MaxPureShearStrain)
		Nstep_ = 10
		strain_step = linspace(max_strain/Nstep_, max_strain, Nstep_)
		damping_ratio = []
		argv_part = argv[1:] 
		for x in xrange(0, Nstep_):
			this_strain = strain_step[x] 
			arg_part = ' '.join([str(x) for x in argv_part])
			arg = str(this_strain) + ' '+ arg_part
			command = "script -c './test_vmlh " + arg + " ' log" 
			call(sh.split(command))
			# read data
			strain_stress = loadtxt(inFilename)
			strain = strain_stress[:,0]
			stress = strain_stress[:,1]
			max_y = max(stress)
			# calc Ws
			Ws = 0.5 * max_y * this_strain 
			# calc Wd
			loop_area = 0 
			strain_step_len = strain[1] - strain[0]
			min_y = min(stress)
			Nstep_monotonic = int(float(form.Num_Of_Subincrement_monotonic_loading))
			for x in xrange(Nstep_monotonic, 3*Nstep_monotonic):
				loop_area = loop_area - strain_step_len * (stress[x] - min_y)
			for x in xrange(3*Nstep_monotonic, 5*Nstep_monotonic):
				loop_area = loop_area + strain_step_len * (stress[x] - min_y)
			Wd = loop_area
			# calc damping
			this_damping = Wd / 4.0 / pi / Ws
			damping_ratio.append(this_damping)


		pl_strain = insert(strain_step, 0, 0 )
		pl_damping = insert(damping_ratio, 0, 0 )
		plt.clf()
		plt.plot(pl_strain, pl_damping)
		plt.xlabel("strain (unitless) ")
		plt.ylabel("Damping ratio (unitless)")
		plt.xscale('log')
		plt.savefig("VMLH_damping_ratio.png", bbox_inches='tight')



		mylog.close()
		test =1 
		return render.VMLH_refresh(argv)