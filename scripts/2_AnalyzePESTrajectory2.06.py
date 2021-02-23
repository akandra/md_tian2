#!/usr/bin/env python

# intention: create all necessary output files for plotting with next script

import os, sys, math, copy, numpy, time


### edit here ###
METAL_TYPE = "C"
SHOT_THRU_LIMIT = 0.0    # yes, this should be a negative number
SPECULAR_RADIUS = 1.5

# set names for output and log file
inpname     = "MXT2Summary.txt"
logfilename = "CreateMXTSummary.log"


### do not edit anything below this line ###

VERSION_ID = 2.06



class Point3D:
	def __init__(self,x,y,z):
		self.x = x
		self.y = y
		self.z = z

	def add(self,other):
		self.x += other.x
		self.y += other.y
		self.z += other.z
	
	def minus(self,other):
                self.x -= other.x
                self.y -= other.y
                self.z -= other.z
	
	def multiply(self, factor):
		self.x *= factor
		self.y *= factor
		self.z *= factor

	def distance(self, other):
		return math.sqrt( (self.x-other.x)**2 + \
			(self.y-other.y)**2 +(self.z-other.z)**2 )

	def normalize(self):
                l = self.length()
                self.x = self.x / l
                self.y = self.y / l
                self.z = self.z / l
	
	def project_onto_plane(self, plane):
    		d = self.dot_product(plane) / plane.length()
		plane.normalize()
    		plane.multiply(d)
    		self.minus(plane)


	def rotate_about_z(self, angle):
		rangle = math.radians(float(angle))
		self.x, self.y = math.cos(rangle)*self.x - math.sin(rangle)*self.y, math.sin(rangle)*self.x + math.cos(rangle)*self.y

	def rotate_about_y(self, angle):
                rangle = math.radians(float(angle))
                self.x, self.z = math.cos(rangle)*self.x + math.sin(rangle)*self.z, -math.sin(rangle)*self.x + math.cos(rangle)*self.z

	def dot_product(self, other):
                return self.x*other.x + self.y*other.y + self.z*other.z

	def cross_product(self, other):
		return [self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x]

	def cross_product2(self, other):
		cp = self.cross_product(other)
		return Point3D(cp[0], cp[1], cp[2])

	def length(self):
		return math.sqrt( self.x**2 + self.y**2 + self.z**2)
	
	def __str__(self):
		return str(self.x) + '  ' + str(self.y) + '  ' + str(self.z)

class Traj:


	def __init__(self, ekin_p_i, ekin_l_i, epot_i, etotal_i,\
			r_p_i, v_p_i, polar_i, azi_i, ekin_p_f, ekin_l_f, epot_f,   \
                        etotal_f, r_p_f, v_p_f, polar_f, azi_f, time, turn_pnts,    \
			cl_appr, cl_appr_t, r_p_min, traj_id):
		self.ekin_p_i = ekin_p_i
		self.ekin_l_i = ekin_l_i
		self.epot_i   = epot_i
		self.etotal_i = etotal_i
		self.r_p_i    = r_p_i
                self.v_p_i    = v_p_i
		self.polar_i  = polar_i
		self.azi_i    = azi_i
		self.ekin_p_f = ekin_p_f
		self.ekin_l_f = ekin_l_f
		self.epot_f   = epot_f
		self.etotal_f = etotal_f
		self.r_p_f    = r_p_f
		self.v_p_f    = v_p_f
		self.polar_f  = polar_f
		self.azi_f    = azi_f
		self.time     = time
		self.turn_pnts = turn_pnts
		self.cl_appr  = cl_appr
		self.cl_appr_t  = cl_appr_t
		self.r_p_min  = r_p_min
                self.traj_id  = traj_id
		self.eloss    = ekin_p_i - ekin_p_f    # energy loss
		self.vloss    = distance(v_p_f, v_p_i) # velocity loss
		self.has_scattered = r_p_f.z > r_p_i.z
		self.has_transmitted = r_p_f.z < SHOT_THRU_LIMIT
		self.has_adsorbed = not (self.has_scattered or self.has_scattered)
		self.in_spec = math.sqrt( (polar_f-polar_i)**2 + (azi_f-azi_i)**2 ) < SPECULAR_RADIUS
		self.in_plane = abs(azi_f-azi_i) % 360 < SPECULAR_RADIUS

	def spec_scattering_vector(self):
		inc = copy.deepcopy(self.v_p_i)
                inc.z *= -1.
                inc.normalize()
		return inc

	def angle_with_spec_scattering_vector(self):
		inc = self.spec_scattering_vector()
		out = copy.deepcopy(self.v_p_f)
		out.normalize()
		dp = inc.dot_product(out)
		angle_in_rad = math.acos(dp)
		return math.degrees( angle_in_rad )

	def angle_with_vector(self, vec):
                out = copy.deepcopy(self.v_p_f)
                out.normalize()
		vec = Point3D(vec[0], vec[1], vec[2])
		vec.normalize()
                dp = out.dot_product(vec)
                angle_in_rad = math.acos(dp)
                return math.degrees( angle_in_rad )


def angle_between(fv, sv):
        fv1 = Point3D(fv[0], fv[1], fv[2])
	sv1 = Point3D(sv[0], sv[1], sv[2])
        fv1.normalize()
	sv1.normalize()
        dp = fv1.dot_product(sv1)
        angle_in_rad = math.acos(dp)
        return math.degrees( angle_in_rad )

def convert_index_to_float(line, idx):
	l = line.strip(' \n\t\r').split()
	return float(l[idx])

def convert_line_to_point3d(line):
	l = line.strip(' \n\t\r').split()
	return Point3D(float(l[0]), float(l[1]), float(l[2]))

def obtain_rot_mat(vec, angle):
	# vec describes line thru origin around which the rotation is performed
	# rotation angle needs to be given in degrees
        # normalize rotation vector
        vec.normalize()

        rangle = math.radians(float(angle))

        rot = [[None,None,None], [None,None,None], [None,None,None]]
        rot[0][0] = vec.x*vec.x*(1.-math.cos(rangle)) +        math.cos(rangle)
        rot[1][0] = vec.x*vec.y*(1.-math.cos(rangle)) - vec.z*math.sin(rangle)
        rot[2][0] = vec.x*vec.z*(1.-math.cos(rangle)) + vec.y*math.sin(rangle)

        rot[0][1] = vec.y*vec.x*(1.-math.cos(rangle)) + vec.z*math.sin(rangle)
        rot[1][1] = vec.y*vec.y*(1.-math.cos(rangle)) +        math.cos(rangle)
        rot[2][1] = vec.y*vec.z*(1.-math.cos(rangle)) - vec.x*math.sin(rangle)

        rot[0][2] = vec.z*vec.x*(1.-math.cos(rangle)) - vec.y*math.sin(rangle)
        rot[1][2] = vec.z*vec.y*(1.-math.cos(rangle)) + vec.x*math.sin(rangle)
        rot[2][2] = vec.z*vec.z*(1.-math.cos(rangle)) +        math.cos(rangle)
        return rot

def matmul(mat, vec):
	v1 = mat[0][0]*vec[0] + mat[0][1]*vec[1] + mat[0][2]*vec[2]
	v2 = mat[1][0]*vec[0] + mat[1][1]*vec[1] + mat[1][2]*vec[2]
	v3 = mat[2][0]*vec[0] + mat[2][1]*vec[1] + mat[2][2]*vec[2]
	return [v1, v2, v3]

def initialize(inpname,logfile):
	ntrajs = sum(1 for line in open(inpname, "r")) -1 	# first line is commment
	print "Reading %d trajectories" % ntrajs
	traj_list = []					# init list
	inp_file = open(inpname, "r")
	counter = 0
        counter_to_total = 0
        cl_appr_count = 0
        r_p_min_count = 0
        adsorb_count = 0
	scattered = 0
	absorbed = 0
	transmitted = 0
	for linenum,line in enumerate(inp_file):
		if line.startswith("#"):				# is comment line
			continue
		if (counter % (ntrajs/10) == 0):
                        print (100*counter+1)/ntrajs, "%"
		sl = line.strip("\n\t\r ").split()
                traj_id  = str(sl[0])                                           #       traj_id   = 00000001
		ekin_p_i = float(sl[1])						#	e_kin_p_i = 3.33000
		ekin_l_i = float(sl[2])						#	e_kin_l_i = 4.07264
		epot_i   = float(sl[3])						#	epot_i    = 30.09554
		etotal_i = float(sl[4])						#       e_total_i = 37.49818
		r_p_i    = Point3D(float(sl[5]), float(sl[6]), float(sl[7]))	#	r_i       = 14.88455  -2.57611  6.00000
		v_p_i    = Point3D(float(sl[8]), float(sl[9]), float(sl[10]))	#	v_i       = 0.0000000 0.0000000 -0.1934888
		polar_i  = float(sl[11])                                         #       polar_i   = 50.00000
		azi_i    = float(sl[12])                                         #       azi_i     = 0.000000

		ekin_p_f = float(sl[13])					#	ekin_p_f  = 0.05978
		ekin_l_f = float(sl[14])					#	ekin_l_f  = 5.26957
		epot_f   = float(sl[15])					#	epot_f    = 28.73945
		etotal_f = float(sl[16])					#	etotal_f  = 34.06880
		r_p_f    = Point3D(float(sl[17]), float(sl[18]), float(sl[19]))	#	r_f       = 13.70619  1.33464  -1.07431
		v_p_f    = Point3D(float(sl[20]), float(sl[21]), float(sl[22]))	#	v_f       = 0.0026410 0.0117354 0.1513796
		polar_f  = float(sl[23])                                        #       polar_f   = 27.23457
                azi_f    = float(sl[24])                                        # 	azi_f     = 4.23478	
		
		time     = float(sl[25])					#	time      = 978.70000
		turn_pnts = int(sl[26])						#       turn_pnts = 14
		cl_appr  = float(sl[27])					#	cl_appr  =      0.9846501
                cl_appr_t = int(sl[28])                                         #       cl_appr_t = 128
		r_p_min  = Point3D(float(sl[29]), float(sl[30]), float(sl[31])) #	r_min_p  = 33.4630699  31.9529501  0.9322836
	
		this_traj = Traj(ekin_p_i, ekin_l_i, epot_i, etotal_i, r_p_i, v_p_i, polar_i, azi_i, ekin_p_f, \
					ekin_l_f, epot_f, etotal_f, r_p_f, v_p_f, polar_f, azi_f, time, turn_pnts, \
					cl_appr, cl_appr_t, r_p_min, traj_id)

		if this_traj.ekin_p_f < 1.1*this_traj.ekin_p_i:
			traj_list.append(this_traj)
                        if this_traj.has_transmitted is True:
                            print "Particle was transmitted in traj with id {}".format(this_traj.traj_id)
                        counter += 1

                else:
                        counter_to_total += 1
			print "Neglecting traj with id {} with final ekin of {}".format(this_traj.traj_id, this_traj.ekin_p_f)

                if this_traj.r_p_f.z > 3.6 and this_traj.cl_appr < 1.4:
                        print("Analyze slow component in traj id {}".format(this_traj.traj_id))
                        cl_appr_count += 1

                if this_traj.r_p_f.z < 3.5:
                        adsorb_count += 1

                #if this_traj.r_p_f.z > 3.6 and this_traj.r_p_min.z < 1.4:
                #        r_p_min_count += 1
                #        print("Analyze slow component (r_p_min.z) in traj {}".format(linenum))

        print("# traj with scattering after barrier: {} out of {} ({}%)".format(cl_appr_count,ntrajs,float(cl_appr_count)*100/float(ntrajs)))
        #print("Scattering after barrier (r_min_p) {}".format(float(r_p_min_count)/float(ntrajs)))
        #print("Final Pos number {}".format(r_p_min_count))
        print("# traj with adsorption: {} out of {} ({}%)".format(adsorb_count,ntrajs,float(adsorb_count)*float(100)/float(ntrajs)))
	mxt_file.close()

	if not os.path.exists("analysis"):
    		os.makedirs("analysis")

	for traj in traj_list:
		if traj.has_scattered:
			scattered += 1
		elif traj.has_transmitted:
			transmitted += 1
		else:
			absorbed += 1

	return traj_list, scattered, absorbed, transmitted

def numbins(inp):
	if isinstance(inp, list):
		return int(3*(len(inp)**(1./3)))
	elif isinstance(inp, int):
		return int(3*((inp)**(1./3)))
	elif isinstance(inp, float):
		return int(3*((inp)**(1./3)))
	else:
		sys.exit("Unknown type from which to compute number of bins in histogram")

def analyze(trajs):

	### BOUNCES ###
	print "Calculating bounces."

	# LOOP 
	all_bounces    = [traj.turn_pnts for traj in trajs]
	scat_bounces   = [traj.turn_pnts for traj in trajs if traj.has_scattered]
	abso_bounces   = [traj.turn_pnts for traj in trajs if traj.has_adsorbed]
	transm_bounces = [traj.turn_pnts for traj in trajs if traj.has_transmitted]
	
	# ANALYSIS
	all_bounce_hist,    all_bounce_edges    = numpy.histogram(all_bounces,    bins=max(all_bounces), range=(0,max(all_bounces)), density=True)
	scat_bounce_hist,   scat_bounce_edges   = numpy.histogram(scat_bounces,   bins=max(all_bounces), range=(0,max(all_bounces)), density=True)
	abso_bounce_hist,   abso_bounce_edges   = numpy.histogram(abso_bounces,   bins=max(all_bounces), range=(0,max(all_bounces)), density=True)
	transm_bounce_hist, transm_bounce_edges = numpy.histogram(transm_bounces, bins=max(all_bounces), range=(0,max(all_bounces)), density=True)

	# OUTPUT
	bounce_file = open("analysis/bounces.txt", "w")
	bounce_file.write("# bounces  all  scattered  absorbed  transmitted\n")
	for i in range(len(all_bounce_hist)):
		bounce_file.write("%d %f %f %f %f\n" % ( 0.5*(all_bounce_edges[i]+all_bounce_edges[i+1]), all_bounce_hist[i], FRAC_SCATTERED*scat_bounce_hist[i], FRAC_ABSORBED*abso_bounce_hist[i], FRAC_TRANSMITTED*transm_bounce_hist[i]))
	bounce_file.close()


	### TOTAL ENERGY LOSS ###
	print "Calculating total energy loss."
	# LOOP 
	all_eloss = [traj.eloss for traj in trajs if traj.has_scattered] 
	one_b     = [traj.eloss for traj in trajs if traj.has_scattered and traj.turn_pnts == 1]
	two_b     = [traj.eloss for traj in trajs if traj.has_scattered and traj.turn_pnts == 3]
	mul_b     = [traj.eloss for traj in trajs if traj.has_scattered and traj.turn_pnts >= 5]
	
	absorbed_eloss = [traj.eloss for traj in trajs if traj.has_adsorbed]

	# ANALYSIS
	all_eloss_hist, all_eloss_edges = numpy.histogram(all_eloss, bins=numbins(SCATTERED), range=(min(all_eloss), max(all_eloss)), density=True)
	one_b_hist,     one_b_edges     = numpy.histogram(one_b,     bins=numbins(SCATTERED), range=(min(all_eloss), max(all_eloss)), density=True)
	two_b_hist,     two_b_edges     = numpy.histogram(two_b,     bins=numbins(SCATTERED), range=(min(all_eloss), max(all_eloss)), density=True)
	mul_b_hist,     mul_b_edges     = numpy.histogram(mul_b,     bins=numbins(SCATTERED), range=(min(all_eloss), max(all_eloss)), density=True)
	frac_one_b = float(len(one_b))/SCATTERED
	frac_two_b = float(len(two_b))/SCATTERED
	frac_mul_b = float(len(mul_b))/SCATTERED

	# OUTPUT 
	eloss_file = open("analysis/eloss.txt", "w")
	eloss_file.write("# eloss/eV  all  single bounce  double bounce  multi bounce\n")
	for i in range(len(all_eloss_hist)):
		eloss_file.write("%f %f %f %f %f\n" % (0.5*(all_eloss_edges[i]+all_eloss_edges[i+1]), all_eloss_hist[i], frac_one_b*one_b_hist[i], frac_two_b*two_b_hist[i], frac_mul_b*mul_b_hist[i]))
	eloss_file.close()


	### SPECULAR ENERGY LOSS ###
	print "Calculating specular energy loss."

	# INIT
	spec_all_eloss = []
	spec_one_b     = []
	spec_two_b     = []
	spec_mul_b     = []

	# LOOP
	for traj in trajs:	# List comprehension simply need too much time. This is ugly, but fast.
		if traj.in_spec and traj.has_scattered:
			spec_all_eloss.append(traj.eloss)
			if traj.turn_pnts == 1:
				spec_one_b.append(traj.eloss)
			elif traj.turn_pnts == 3:
				spec_two_b.append(traj.eloss)
			else:
				spec_mul_b.append(traj.eloss)

	spec_eloss_file = open("analysis/spec_eloss.txt", "w")
        spec_eloss_file.write("# eloss/eV  all  single bounce  double bounce  multi bounce\n")
	if len(spec_all_eloss) > 0:	
	        # ANALYSIS 
		spec_all_eloss_hist, spec_all_eloss_edges = numpy.histogram(spec_all_eloss, bins=numbins(spec_all_eloss), range=(min(spec_all_eloss), max(spec_all_eloss)), density=True)
	        spec_one_b_hist,     spec_one_b_edges     = numpy.histogram(spec_one_b,     bins=numbins(spec_all_eloss), range=(min(spec_all_eloss), max(spec_all_eloss)), density=True)
	        spec_two_b_hist,     spec_two_b_edges     = numpy.histogram(spec_two_b,     bins=numbins(spec_all_eloss), range=(min(spec_all_eloss), max(spec_all_eloss)), density=True)
	        spec_mul_b_hist,     spec_mul_b_edges     = numpy.histogram(spec_mul_b,     bins=numbins(spec_all_eloss), range=(min(spec_all_eloss), max(spec_all_eloss)), density=True)
	        spec_frac_one_b = float(len(spec_one_b))/len(spec_all_eloss)
	        spec_frac_two_b = float(len(spec_two_b))/len(spec_all_eloss)
	        spec_frac_mul_b = float(len(spec_mul_b))/len(spec_all_eloss)

		# OUTPUT 
	        spec_eloss_file = open("analysis/spec_eloss.txt", "w")
	        spec_eloss_file.write("# eloss/eV  all  single bounce  double bounce  multi bounce\n")
	        for i in range(len(spec_all_eloss_hist)):
	                spec_eloss_file.write("%f %f %f %f %f\n" % (0.5*(spec_all_eloss_edges[i]+spec_all_eloss_edges[i+1]), spec_all_eloss_hist[i], spec_frac_one_b*spec_one_b_hist[i], spec_frac_two_b*spec_two_b_hist[i], spec_frac_mul_b*spec_mul_b_hist[i]))
	else:
		spec_eloss_file.write("%f %f %f %f %f\n" % ( 0.0, 0.0, 0.0, 0.0, 0.0))
	spec_eloss_file.close()


	### IN PLANE ENERGY LOSS ###
	print "Calculating in-plane energy loss."

	# INIT
	in_plane_all_eloss = []
	in_plane_one_b     = []
	in_plane_two_b     = []
	in_plane_mul_b     = []

	# LOOP
	for traj in trajs:	# List comprehension simply need too much time. This is ugly, but fast.
		if traj.in_plane and traj.has_scattered:
			in_plane_all_eloss.append(traj.eloss)
			if traj.turn_pnts == 1:
				in_plane_one_b.append(traj.eloss)
			elif traj.turn_pnts == 3:
				in_plane_two_b.append(traj.eloss)
			else:
				in_plane_mul_b.append(traj.eloss)

	in_plane_eloss_file = open("analysis/in_plane_eloss.txt", "w")
        in_plane_eloss_file.write("# eloss/eV  all  single bounce  double bounce  multi bounce\n")
	if len(in_plane_all_eloss) > 0:	
	        # ANALYSIS 
		in_plane_all_eloss_hist, in_plane_all_eloss_edges = numpy.histogram(in_plane_all_eloss, bins=numbins(in_plane_all_eloss), range=(min(in_plane_all_eloss), max(in_plane_all_eloss)), density=True)
	        in_plane_one_b_hist,     in_plane_one_b_edges     = numpy.histogram(in_plane_one_b,     bins=numbins(in_plane_all_eloss), range=(min(in_plane_all_eloss), max(in_plane_all_eloss)), density=True)
	        in_plane_two_b_hist,     in_plane_two_b_edges     = numpy.histogram(in_plane_two_b,     bins=numbins(in_plane_all_eloss), range=(min(in_plane_all_eloss), max(in_plane_all_eloss)), density=True)
	        in_plane_mul_b_hist,     in_plane_mul_b_edges     = numpy.histogram(in_plane_mul_b,     bins=numbins(in_plane_all_eloss), range=(min(in_plane_all_eloss), max(in_plane_all_eloss)), density=True)
	        in_plane_frac_one_b = float(len(in_plane_one_b))/len(in_plane_all_eloss)
	        in_plane_frac_two_b = float(len(in_plane_two_b))/len(in_plane_all_eloss)
	        in_plane_frac_mul_b = float(len(in_plane_mul_b))/len(in_plane_all_eloss)

		# OUTPUT 
	        in_plane_eloss_file = open("analysis/in_plane_eloss.txt", "w")
	        in_plane_eloss_file.write("# eloss/eV  all  single bounce  double bounce  multi bounce\n")
	        for i in range(len(in_plane_all_eloss_hist)):
	                in_plane_eloss_file.write("%f %f %f %f %f\n" % (0.5*(in_plane_all_eloss_edges[i]+in_plane_all_eloss_edges[i+1]), in_plane_all_eloss_hist[i], in_plane_frac_one_b*in_plane_one_b_hist[i], in_plane_frac_two_b*in_plane_two_b_hist[i], in_plane_frac_mul_b*in_plane_mul_b_hist[i]))
	else:
		in_plane_eloss_file.write("%f %f %f %f %f\n" % ( 0.0, 0.0, 0.0, 0.0, 0.0))
	in_plane_eloss_file.close()



	### Z-POSITION ###
	print "Calculating final z positions."
	# LOOP
	final_z = [traj.r_p_f.z for traj in trajs if traj.has_adsorbed]

	if (len(final_z) > 0):
		# ANALYSIS
		final_z_hist, final_z_edges = numpy.histogram(final_z, bins=numbins(final_z), range=(min(final_z), max(final_z)), density=True)

		# OUTPUT
		final_z_file = open("analysis/final_z.txt", "w")
		final_z_file.write("# z/A  probability density\n")
		for i in range(len(final_z_hist)):
			final_z_file.write("%f %f\n" % (0.5*(final_z_edges[i]+final_z_edges[i+1]), final_z_hist[i]))
		final_z_file.close()
		

	### BOUNCES VS ELOSS ###
	print "Calculating bounces/energy loss correlation."
	# ANALYSIS
	bounce_vs_eloss_hist, xegdes, yedges = numpy.histogram2d(scat_bounces, all_eloss, bins=(max(scat_bounces),numbins(all_eloss)), range=[[0,max(scat_bounces)],[min(all_eloss),max(all_eloss)]], normed=False)

	# OUTPUT
	out = open("analysis/bounces_vs_eloss.txt", "w")
	out.write("# bounces  eloss/eV  counts\n")
	for i in range(len(bounce_vs_eloss_hist)):
		for j in range(len(bounce_vs_eloss_hist[i])):
			out.write("%d %f %d\n" % (0.5*(xegdes[i]+xegdes[i+1]), 0.5*(yedges[j]+yedges[j+1]), bounce_vs_eloss_hist[i][j]))
		out.write("\n")
	out.close()


        ### ANGULAR DISTRIBUTION ###
	print "Calculating angular energy loss"
	# get trajectories that are within specular radius in azimuth direction
	energy_collect  = []
	angle_collect   = []
	ps_dist_collect = []
	polar_scatt_azi_int_energy = []
	polar_scatt_azi_int_angle  = []
	for traj in trajs:
		if traj.has_scattered:
			polar_scatt_azi_int_energy.append(traj.eloss)
			polar_scatt_azi_int_angle.append(traj.polar_f)

			if traj.in_plane:
				energy_collect.append(traj.eloss)
				angle_collect.append(traj.polar_f)
				ps_dist_collect.append(traj.cl_appr)

	ang_dist_file = open("analysis/ang_res_eloss.txt", "w")
	if len(energy_collect) != 0:
		angle_eloss_hist, xedges, yedges = numpy.histogram2d(energy_collect, angle_collect,  bins=(numbins(energy_collect)), normed=False)
			
		# OUTPUT
		for i in range(len(angle_eloss_hist)):
			for j in range(len(angle_eloss_hist[i])):
				ang_dist_file.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), 0.5*(yedges[j]+yedges[j+1]), angle_eloss_hist[i][j]))
			ang_dist_file.write("\n")
	else:
		ang_dist_file.write("%f %f %d\n"   % (0.1, 0.5, 0))
                ang_dist_file.write("%f %f %d\n\n" % (0.1, 1.0, 1))
		ang_dist_file.write("%f %f %d\n"   % (0.2, 1.0, 1))
		ang_dist_file.write("%f %f %d\n"   % (0.2, 0.5, 2))
		
	ang_dist_file.close()

	# INTERGRATED OVER ALL AZIMUTH ANGLES #
	polar_scatt_azi_file = open("analysis/polar_scatt_azi_int.txt", "w")
	if len(polar_scatt_azi_int_energy) != 0:
		polar_scatt_azi_int_hist, xedges, yedges = numpy.histogram2d(polar_scatt_azi_int_energy, polar_scatt_azi_int_angle, bins=(numbins(polar_scatt_azi_int_energy)), normed=False)
		
		for i in range(len(polar_scatt_azi_int_hist)):
			for j in range(len(polar_scatt_azi_int_hist[i])):
				polar_scatt_azi_file.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), 0.5*(yedges[j]+yedges[j+1]), polar_scatt_azi_int_hist[i][j]))
			polar_scatt_azi_file.write("\n")
	else:
		polar_scatt_azi_file.write("%f %f %d\n"   % (0.1, 0.5, 0))
		polar_scatt_azi_file.write("%f %f %d\n\n" % (0.1, 1.0, 1))
		polar_scatt_azi_file.write("%f %f %d\n"   % (0.2, 1.0, 1))
		polar_scatt_azi_file.write("%f %f %d\n"   % (0.2, 0.5, 2))

	polar_scatt_azi_file.close()


	### LOSS TO EHP AND PHONONS ###
	print "Calculating loss to ehps and phonons"
	# LOOP
	loss_to_ehps = [ traj.etotal_i - traj.etotal_f for traj in trajs if traj.has_scattered ]
	loss_to_ehps_spec = [ traj.etotal_i - traj.etotal_f for traj in trajs if traj.has_scattered and traj.in_spec ]
	
	# ANALYSIS
	loss_to_ehps_hist, loss_to_ehps_edges = numpy.histogram(loss_to_ehps, bins=numbins(loss_to_ehps), range=(min(loss_to_ehps), max(loss_to_ehps)), density=True)
	if len(loss_to_ehps_spec) > 0:
		loss_to_ehps_spec_hist, loss_to_ehps_spec_edges = numpy.histogram(loss_to_ehps_spec, bins=numbins(loss_to_ehps_spec), range=(min(loss_to_ehps_spec), max(loss_to_ehps_spec)), density=True)

	# OUTPUT
	loss_to_ehps_file = open("analysis/eloss_to_ehps.txt", "w")
	for i in range(len(loss_to_ehps_hist)):
		loss_to_ehps_file.write("%f %f\n" % (0.5*(loss_to_ehps_edges[i]+loss_to_ehps_edges[i+1]), loss_to_ehps_hist[i]))
	loss_to_ehps_file.close()

	
	loss_to_ehps_spec_file = open("analysis/eloss_to_ehps_spec.txt", "w")
	if len(loss_to_ehps_spec) > 0:
	        for i in range(len(loss_to_ehps_spec_hist)):
	                loss_to_ehps_spec_file.write("%f %f\n" % (0.5*(loss_to_ehps_spec_edges[i]+loss_to_ehps_spec_edges[i+1]), loss_to_ehps_spec_hist[i]))
	else:
		loss_to_ehps_spec_file.write("%f %f\n" % (0.0, 0.0))
        loss_to_ehps_spec_file.close()


	### SPHERICAL SYMMETRY ###
	# LOOP
	print "Calculating spherical symmetry"
	xvals = []
	yvals = []
	for traj in trajs:
		if traj.has_scattered:
			xvals.append(traj.azi_f)
			yvals.append(traj.polar_f)

	# ANALYSIS
	spherical_hist, xedges, yedges = numpy.histogram2d(xvals, yvals, bins=numbins(xvals), normed=False)

	# OUTPUT
	spherical_file = open("analysis/spherical_symmetry.txt", "w")
	for i in range(len(spherical_hist)):
		for j in range(len(spherical_hist[i])):
			spherical_file.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), -0.5*(yedges[j]+yedges[j+1]), spherical_hist[i][j]))
		spherical_file.write("\n")
	spherical_file.close()



	### Projectile-Surface distance ###
	print "Calculating projectile-surface distance"
	# LOOP
	ps_dist = [traj.cl_appr for traj in trajs if traj.has_scattered]

	# ANALYSIS
	ps_hist, xedges = numpy.histogram(ps_dist, bins=numbins(ps_dist), range=(min(ps_dist), max(ps_dist)), density=True)
	
	# OUTPUT
	ps_file = open("analysis/ps_dist.txt", "w")
        for i in range(len(ps_hist)):
                ps_file.write("%f %f\n" % (0.5*(xedges[i]+xedges[i+1]), ps_hist[i]))
        ps_file.close()



	### Eloss vs Projectile-Surface distance ###
	print "Calculating energy loss projectile-surface distance relationship"
	# ANALYSIS
	eloss_psd_hist, xedges, yedges = numpy.histogram2d(all_eloss, ps_dist, bins=numbins(all_eloss), normed=False)
	
	# OUTPUT
	eloss_psd_file = open("analysis/eloss_psd.txt", "w")
	for i in range(len(eloss_psd_hist)):
                for j in range(len(eloss_psd_hist[i])):
                        eloss_psd_file.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), 0.5*(yedges[j]+yedges[j+1]), eloss_psd_hist[i][j]))
                eloss_psd_file.write("\n")
        eloss_psd_file.close()



	### Scattering polar angle vs Projectile-Surface distance in-plane ###
	print "Calculating scattering angle projectile-surface distance relationship"
	# ANALYSIS
	polar_psd_file = open("analysis/polar_psd.txt", "w")
	if len(ps_dist_collect) > 0:
		polar_psd_hist, xedges, yedges = numpy.histogram2d(ps_dist_collect, angle_collect, bins=numbins(ps_dist_collect), normed=False)

		# OUTPUT
		for i in range(len(polar_psd_hist)):
	                for j in range(len(polar_psd_hist[i])):
	                        polar_psd_file.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), 0.5*(yedges[j]+yedges[j+1]), polar_psd_hist[i][j]))
			polar_psd_file.write("\n")
	else:
		polar_psd_file.write("%f %f %d\n"   % (0.1, 0.5, 0))
                polar_psd_file.write("%f %f %d\n\n" % (0.1, 1.0, 1))
                polar_psd_file.write("%f %f %d\n"   % (0.2, 1.0, 1))
                polar_psd_file.write("%f %f %d\n"   % (0.2, 0.5, 2))
	polar_psd_file.close()


	### Eloss vs Projectile-Surface distance in plane ###
	print "Calculating in-plane energy loss projectile-surface distance relationship"
	# ANALYSIS
	eloss_psd_in_plane_file = open("analysis/eloss_psd_in_plane.txt", "w")
	if len(ps_dist_collect) > 0:
		eloss_psd_in_plane_hist, xedges, yedges = numpy.histogram2d(energy_collect, ps_dist_collect, bins=numbins(ps_dist_collect), normed=False)

		# OUTPUT
		for i in range(len(eloss_psd_in_plane_hist)):
	                for j in range(len(eloss_psd_in_plane_hist[i])):
	                        eloss_psd_in_plane_file.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), 0.5*(yedges[j]+yedges[j+1]), eloss_psd_in_plane_hist[i][j]))
	                eloss_psd_in_plane_file.write("\n")
	else:
		eloss_psd_in_plane_file.write("%f %f %d\n"   % (0.1, 0.5, 0))
                eloss_psd_in_plane_file.write("%f %f %d\n\n" % (0.1, 1.0, 1))
                eloss_psd_in_plane_file.write("%f %f %d\n"   % (0.2, 1.0, 1))
                eloss_psd_in_plane_file.write("%f %f %d\n"   % (0.2, 0.5, 2))
        eloss_psd_in_plane_file.close()
	

	### TOTAL VELOCITY LOSS ###
	print("Calculating total velocity loss.")
        logfile.write("Calculating total velocity loss.")
	# LOOP 
	all_vloss = [traj.vloss for traj in trajs if traj.has_scattered] 
	one_vb     = [traj.vloss for traj in trajs if traj.has_scattered and traj.turn_pnts == 1]
	two_vb     = [traj.vloss for traj in trajs if traj.has_scattered and traj.turn_pnts == 3]
	mul_vb     = [traj.vloss for traj in trajs if traj.has_scattered and traj.turn_pnts >= 5]
	
	absorbed_vloss = [traj.vloss for traj in trajs if traj.has_adsorbed]

	# ANALYSIS
	all_vloss_hist, all_vloss_edges = numpy.histogram(all_vloss, bins=numbins(SCATTERED), range=(min(all_vloss), max(all_vloss)), density=True)
	one_vb_hist,     one_vb_edges     = numpy.histogram(one_vb,     bins=numbins(SCATTERED), range=(min(all_vloss), max(all_vloss)), density=True)
	two_vb_hist,     two_vb_edges     = numpy.histogram(two_vb,     bins=numbins(SCATTERED), range=(min(all_vloss), max(all_vloss)), density=True)
	mul_vb_hist,     mul_vb_edges     = numpy.histogram(mul_vb,     bins=numbins(SCATTERED), range=(min(all_vloss), max(all_vloss)), density=True)
	frac_one_vb = float(len(one_vb))/SCATTERED
	frac_two_vb = float(len(two_vb))/SCATTERED
	frac_mul_vb = float(len(mul_vb))/SCATTERED

	# OUTPUT 
	vloss_file = open("analysis/vloss.txt", "w")
	vloss_file.write("# vloss/eV  all  single bounce  double bounce  multi bounce\n")
	for i in range(len(all_vloss_hist)):
		vloss_file.write("%f %f %f %f %f\n" % (0.5*(all_vloss_edges[i]+all_vloss_edges[i+1]), all_vloss_hist[i], frac_one_vb*one_vb_hist[i], frac_two_vb*two_vb_hist[i], frac_mul_vb*mul_vb_hist[i]))
	vloss_file.close()


        ### ANGULAR DISTRIBUTION ###
	print("Calculating angular velocity loss")
        logfile.write("Calculating angular velocity loss")
	# get trajectories that are within specular radius in azimuth direction
	velocity_collect  = []
	angle_collect   = []
	ps_dist_collect = []
	polar_scatt_azi_int_velocity = []
	polar_scatt_azi_int_angle  = []
	for traj in trajs:
		if traj.has_scattered:
			polar_scatt_azi_int_velocity.append(traj.vloss)
			polar_scatt_azi_int_angle.append(traj.polar_f)

			if traj.in_plane:
				velocity_collect.append(traj.vloss)
				angle_collect.append(traj.polar_f)
				ps_dist_collect.append(traj.cl_appr)

	ang_dist_file_v = open("analysis/ang_res_vloss.txt", "w")
	if len(velocity_collect) != 0:
		angle_vloss_hist, xedges, yedges = numpy.histogram2d(velocity_collect, angle_collect,  bins=(numbins(velocity_collect)), normed=False)
			
		# OUTPUT
		for i in range(len(angle_vloss_hist)):
			for j in range(len(angle_vloss_hist[i])):
				ang_dist_v_file.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), 0.5*(yedges[j]+yedges[j+1]), angle_vloss_hist[i][j]))
			ang_dist_file_v.write("\n")
	else:
		ang_dist_file_v.write("%f %f %d\n"   % (0.1, 0.5, 0))
                ang_dist_file_v.write("%f %f %d\n\n" % (0.1, 1.0, 1))
		ang_dist_file_v.write("%f %f %d\n"   % (0.2, 1.0, 1))
		ang_dist_file_v.write("%f %f %d\n"   % (0.2, 0.5, 2))
		
	ang_dist_file_v.close()

	# INTERGRATED OVER ALL AZIMUTH ANGLES #
	polar_scatt_azi_file_v = open("analysis/polar_scatt_azi_int_v.txt", "w")
	if len(polar_scatt_azi_int_velocity) != 0:
		polar_scatt_azi_int_hist_v, xedges, yedges = numpy.histogram2d(polar_scatt_azi_int_velocity, polar_scatt_azi_int_angle, bins=(numbins(polar_scatt_azi_int_velocity)), normed=False)
		
		for i in range(len(polar_scatt_azi_int_hist_v)):
			for j in range(len(polar_scatt_azi_int_hist_v[i])):
				polar_scatt_azi_file_v.write("%f %f %d\n" % (0.5*(xedges[i]+xedges[i+1]), 0.5*(yedges[j]+yedges[j+1]), polar_scatt_azi_int_hist_v[i][j]))
			polar_scatt_azi_file_v.write("\n")
	else:
		polar_scatt_azi_file_v.write("%f %f %d\n"   % (0.1, 0.5, 0))
		polar_scatt_azi_file_v.write("%f %f %d\n\n" % (0.1, 1.0, 1))
		polar_scatt_azi_file.write("%f %f %d\n"   % (0.2, 1.0, 1))
		polar_scatt_azi_file.write("%f %f %d\n"   % (0.2, 0.5, 2))

	polar_scatt_azi_file_v.close()


	

	### SUMMARY ###
	# ANALYSIS
	energy_won = sum( [1 for e_final in all_eloss if e_final < 0] )

	# OUTPUT 
	out = open("analysis/Summary.txt", "w")
	out.write("Created by version %4.2f\n" % VERSION_ID)
	out.write("Scattered:   %d (%f%%)\n" % (SCATTERED,   100.*FRAC_SCATTERED))
	out.write("Absorbed:    %d (%f%%)\n" % (ABSORBED,    100.*FRAC_ABSORBED))
	out.write("Transmitted: %d (%f%%)\n\n" % (TRANSMITTED, 100.*FRAC_TRANSMITTED))

	out.write("%d (%f%%) of the scattered projectiles won kinetic energy.\n" % (energy_won, 100.*energy_won/SCATTERED))
	out.write("%f%% of scattered trajectories were within +-%f degrees in plane.\n" % (100.*len(in_plane_all_eloss)/SCATTERED, SPECULAR_RADIUS))
	out.write("%f%% of scattered trajectories were within +-%f degrees to specular scattering angle.\n\n" % (100.*len(spec_all_eloss)/SCATTERED, SPECULAR_RADIUS))

	out.write("Average energy loss of H-atoms in specular scattering angle %f eV.\n"   % numpy.mean(spec_all_eloss))
	try:
		out.write("Peak energy loss of H-atoms in specular scattering angle    %f eV.\n\n" % spec_all_eloss_edges[numpy.argmax(spec_all_eloss_hist)])
	except(UnboundLocalError):
		out.write("Peak energy loss of H-atoms in specular scattering angle    %s eV.\n\n" % "No atoms in specular scattering angle")
	out.write("Average energy loss of H-atoms reflected %f eV.\n"     % numpy.mean(all_eloss))
	out.write("Peak energy loss of H-atoms reflected    %f eV.\n\n"   % all_eloss_edges[numpy.argmax(all_eloss_hist)])
	out.write("Average energy loss of H-atoms in bulk   %f eV.\n" % numpy.mean(absorbed_eloss))
	out.write("Average energy loss of reflected H-atoms to ehps %f eV.\n" % numpy.mean(loss_to_ehps))
	out.write("Average energy loss of specularly reflected H-atoms to ehps %f eV.\n\n" % numpy.mean(loss_to_ehps_spec))
	
	out.write("%refl  %in bulk  %shot_thru  %E_won  %in_spec  avg_E_in_spec  peak_E_in_spec  avg_E_in_bulk  avg_E_refl  peak_E_refl  avg_ehp_loss  avg_ehp_loss_spec Trajs\n")
	try:
		out.write("%f %f %f %f %f %f %f %f %f %f %f %f %d\n" % (100.*FRAC_SCATTERED, 100.*FRAC_ABSORBED, 100.*FRAC_TRANSMITTED, 100.*energy_won/SCATTERED, 100.*len(spec_all_eloss)/SCATTERED, trajs[0].ekin_p_i-numpy.mean(spec_all_eloss), trajs[0].ekin_p_i-spec_all_eloss_edges[numpy.argmax(spec_all_eloss_hist)], trajs[0].ekin_p_i-numpy.mean(absorbed_eloss), trajs[0].ekin_p_i-numpy.mean(all_eloss), trajs[0].ekin_p_i-all_eloss_edges[numpy.argmax(all_eloss_hist)], numpy.mean(loss_to_ehps), numpy.mean(loss_to_ehps_spec), len(trajs)))
	except(UnboundLocalError):
		out.write("%f %f %f %f %f %f %f %f %f %f %f %d\n" % (100.*FRAC_SCATTERED, 100.*FRAC_ABSORBED, 100.*FRAC_TRANSMITTED, 100.*energy_won/SCATTERED, 100.*len(spec_all_eloss)/SCATTERED, trajs[0].ekin_p_i-numpy.mean(spec_all_eloss), trajs[0].ekin_p_i-numpy.mean(absorbed_eloss), trajs[0].ekin_p_i-numpy.mean(all_eloss), trajs[0].ekin_p_i-all_eloss_edges[numpy.argmax(all_eloss_hist)], numpy.mean(loss_to_ehps), numpy.mean(loss_to_ehps_spec), len(trajs)))
	out.close()

	
	
	

# Average energy of H-atoms in bulk 0.03969474585 eV.
# Average energy of H-atoms reflected 1.93905890836 eV.
# Peak energy of H-atoms reflected 2.770000 eV
#


###### SCRIPT ######

# open logfile
logfile = open(logfilename, 'w')

print("Screen output will be automatically written to {}!".format(logfilename))

print("Created by version %4.2f" % VERSION_ID)
logfile.write("Created by version %4.2f\n" % VERSION_ID)




### READ IN TRAJS ###
traj_collection, SCATTERED, ABSORBED, TRANSMITTED = initialize(inpname,logfile)

### CALCULATE USEFUL CONSTANTS ###
NTRAJS = len(traj_collection)
FRAC_SCATTERED = float(SCATTERED)/NTRAJS
FRAC_ABSORBED = float(ABSORBED)/NTRAJS
FRAC_TRANSMITTED = float(TRANSMITTED)/NTRAJS

### OUTPUT ###
analyze(traj_collection)

logfile.close()

