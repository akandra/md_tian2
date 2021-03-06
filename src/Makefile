# Makefile for md_tian2

##############################################
# Compiler:
# Intel ifort compiler
#
# Library:
# Intel mkl library
##############################################

#############
### Settings:
#############

# Although it is possible to use GNU compiler, we strongly recommend to use the intel compiler due to performance reasons!

# INTEL compiler and MKL library - dynamic
FC     = ifort 
FFLAGS = -O3 -mkl -xhost -fp-model precise -132
LIB    =

# Comments: 
# -fp-model precise -132 was added to guerantee numerical stability (affects mostly the RuNNer subroutines)
#  instead of using the MKL library one can also include BLAS and LAPACK directly (not tested)

# check also the intel link advisor webpage under:
# https://software.intel.com/content/www/us/en/develop/articles/intel-mkl-link-line-advisor.html

# GNU Compiler and MKL library - static
#FC     = gfortran
#FFLAGS = -O3 -xhost -fp-model precise -132
#LIB    = -Wl,--start-group ${MKLROOT}/lib/intel64/libmkl_gf_lp64.a ${MKLROOT}/lib/intel64/libmkl_sequential.a ${MKLROOT}/lib/intel64/libmkl_core.a -Wl,--end-group -lpthread -lm -ldl

# GNU Compiler and MKL library - dynamic
#FC     = gfortran
#FFLAGS = -O3 -xhost -fp-model precise -132
#LIB    = -L${MKLROOT}/lib/intel64 -Wl,--no-as-needed -lmkl_gf_lp64 -lmkl_sequential -lmkl_core -lpthread -lm -ldl

###############################################
# Changes below this line developers only
###############################################

# for debug purpose just copy the wanted settings below to the FFLAGS entry!
DEBUG_FULL  = -fpe0 -O0 -mkl -g -check all -check bounds -check uninit -ftrapuv -debug all -gen-interfaces -warn interfaces -traceback -warn all -extend-source 132 -fp-stack-check -fstack-protector-all -no-ftz -std08 -standard-semantics -fpe-all=0 -heap-arrays
DEBUG  = -O0 -mkl -g -check all -traceback -fp-stack-check -fstack-protector-all -heap-arrays

RUNNER_SRC_DIR = RuNNer_src/

SUBROUTINES = 	md_tian2.o \
		abstime.o \
		addatoms.o \
		atomsymfunction1.o \
		atomsymfunction2.o \
		atomsymfunction3Andi.o \
		atomsymfunction3.o \
		atomsymfunction4.o \
		atomsymfunction5.o \
		atomsymfunction6.o \
		atomsymfunction8.o \
		atomsymfunction9.o \
		calconenn.o \
		checkelement.o \
		check_type.o \
		convert_frequencies.o \
		dia_hessian.o \
		getatomsymfunctions.o \
		getatomsymfunctions_sfg.o \
		getcutoff.o \
		getddnodes_values.o \
		getdnodes_values.o \
		getgroupcutoffvalues.o \
		getgroupneighlist.o \
		getlistdim.o \
		getneighboridxatomic_para.o \
		getneighborsatomic_para.o \
		getshortatomic.o \
		getsymfunctionderivatives.o \
		getsymfunctionsecondderivatives.o \
		getvibrationalfrequencies.o \
		getvolume.o \
		mpifitdistribution.o \
		neighbor_para_short.o \
		nuccharge.o \
		predictionshortatomic.o \
		sortelements.o \
		sortsymfunctions.o \
		translate.o \


MPI_DUMMY_SUBROUTINES = mpi_dummy_routines.o \

MODULES      =	constants.o \
		open_file.o \
		useful_things.o \
		universe_mod.o \
		run_config.o \
		pes_non_mod.o \
		pes_ho_mod.o \
		pes_lj_mod.o \
		pes_emt_mod.o \
		pes_rebo_mod.o \
		fileunits.o \
		predictionoptions.o \
	       	nnflags.o \
               	nnconstants.o \
               	globaloptions.o \
	       	mode1options.o \
	       	nnshort_atomic.o \
	       	nnewald.o \
		saturation.o \
		structures.o \
		symfunctions.o \
		symfunctiongroups.o \
		timings.o \
		fittingoptions.o \
	        pes_nene_mod.o \
	        rpmd.o \
	        force.o \
	        md_init.o \
	        md_algo.o \
	        trajectory_info.o \
	        output_mod.o \
	        fit.o \
	        geometry_opt.o \

MODULES_MPI_DUMMY = mpi_dummy.o


# begin make

all:
	cat compile.msg

# compile modules
constants.o: constants.f90
	rm constants.mod ; \
	$(FC) $(FFLAGS) -c constants.f90

open_file.o: open_file.f90
	rm open_file.mod ; \
        $(FC) $(FFLAGS) -c open_file.f90

useful_things.o: useful_things.f90
	rm useful_things.mod ; \
        $(FC) $(FFLAGS) -c useful_things.f90

universe_mod.o: universe_mod.f90
	rm universe_mod.mod ; \
        $(FC) $(FFLAGS) -c universe_mod.f90

run_config.o: run_config.f90
	rm run_config.mod ; \
        $(FC) $(FFLAGS) -c run_config.f90

pes_non_mod.o: pes_non_mod.f90
	rm pes_non_mod.mod ; \
        $(FC) $(FFLAGS) -c pes_non_mod.f90

pes_ho_mod.o: pes_ho_mod.f90
	rm pes_ho_mod.mod ; \
        $(FC) $(FFLAGS) -c pes_ho_mod.f90

pes_lj_mod.o: pes_lj_mod.f90
	rm pes_lj_mod.mod ; \
        $(FC) $(FFLAGS) -c pes_lj_mod.f90

pes_emt_mod.o: pes_emt_mod.f90
	rm pes_emt_mod.mod ; \
        $(FC) $(FFLAGS) -c pes_emt_mod.f90

pes_rebo_mod.o: pes_rebo_mod.f90
	rm pes_rebo_mod.mod ; \
        $(FC) $(FFLAGS) -c pes_rebo_mod.f90

fileunits.o: $(RUNNER_SRC_DIR)fileunits.f90
	rm $(RUNNER_SRC_DIR)fileunits.mod ; \
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)fileunits.f90

fittingoptions.o: $(RUNNER_SRC_DIR)fittingoptions.f90
	rm $(RUNNER_SRC_DIR)fittingoptions.mod ; \
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)fittingoptions.f90

nnflags.o: $(RUNNER_SRC_DIR)nnflags.f90
	rm $(RUNNER_SRC_DIR)nnflags.mod ; \
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)nnflags.f90

nnconstants.o: $(RUNNER_SRC_DIR)nnconstants.f90
	rm $(RUNNER_SRC_DIR)nnconstants.mod ; \
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)nnconstants.f90

globaloptions.o: $(RUNNER_SRC_DIR)globaloptions.f90
	rm $(RUNNER_SRC_DIR)globaloptions.mod ; \
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)globaloptions.f90

mode1options.o: $(RUNNER_SRC_DIR)mode1options.f90
	rm $(RUNNER_SRC_DIR)mode1options.mod ; \
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)mode1options.f90

nnshort_atomic.o: $(RUNNER_SRC_DIR)nnshort_atomic.f90
	rm $(RUNNER_SRC_DIR)nnshort_atomic.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)nnshort_atomic.f90

nnewald.o: $(RUNNER_SRC_DIR)nnewald.f90
	rm $(RUNNER_SRC_DIR)nnewald.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)nnewald.f90

saturation.o: $(RUNNER_SRC_DIR)saturation.f90
	rm $(RUNNER_SRC_DIR)saturation.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)saturation.f90

structures.o: $(RUNNER_SRC_DIR)structures.f90
	rm $(RUNNER_SRC_DIR)structures.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)structures.f90

symfunctions.o: $(RUNNER_SRC_DIR)symfunctions.f90
	rm $(RUNNER_SRC_DIR)symfunctions.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)symfunctions.f90

symfunctiongroups.o: $(RUNNER_SRC_DIR)symfunctiongroups.f90
	rm $(RUNNER_SRC_DIR)symfunctiongroups.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)symfunctiongroups.f90

timings.o: $(RUNNER_SRC_DIR)timings.f90
	rm $(RUNNER_SRC_DIR)timings.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)timings.f90

predictionoptions.o: $(RUNNER_SRC_DIR)predictionoptions.f90
	rm $(RUNNER_SRC_DIR)predicitonoptions.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)predictionoptions.f90

mpi_dummy.o: $(RUNNER_SRC_DIR)mpi_dummy.f90
	rm $(RUNNER_SRC_DIR)mpi_dummy.mod ; \
        $(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)mpi_dummy.f90

pes_nene_mod.o: pes_nene_mod.f90
	rm pes_nene_mod.mod ; \
        $(FC) $(FFLAGS) -c pes_nene_mod.f90

force.o: force.f90
	rm force.mod ; \
	$(FC) $(FFLAGS) -c force.f90

rpmd.o: rpmd.f90
	rm rpmd.mod ; \
	$(FC) $(FFLAGS) -c rpmd.f90

md_init.o: md_init.f90
	rm md_init.mod ; \
	$(FC) $(FFLAGS) -c md_init.f90

md_algo.o: md_algo.f90
	rm md_algo.mod ; \
	$(FC) $(FFLAGS) -c md_algo.f90

trajectory_info.o: trajectory_info.f90
	rm trajectory_info.mod ; \
	$(FC) $(FFLAGS) -c trajectory_info.f90

output_mod.o: output_mod.f90
	rm output_mod.mod ; \
	$(FC) $(FFLAGS) -c output_mod.f90

fit.o: fit.f90
	rm fit.mod ; \
	$(FC) $(FFLAGS) -c fit.f90

geometry_opt.o: geometry_opt.f90
	rm geometry_opt.mod ; \
	$(FC) $(FFLAGS) -c geometry_opt.f90



# compile subroutines in alphabetical order

md_tian2.o: md_tian2.f90
	$(FC) $(FFLAGS) -c md_tian2.f90

abstime.o: $(RUNNER_SRC_DIR)abstime.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)abstime.f90

addatoms.o: $(RUNNER_SRC_DIR)addatoms.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)addatoms.f90

atomsymfunction1.o: $(RUNNER_SRC_DIR)atomsymfunction1.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction1.f90

atomsymfunction2.o: $(RUNNER_SRC_DIR)atomsymfunction2.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction2.f90

atomsymfunction3Andi.o: $(RUNNER_SRC_DIR)atomsymfunction3Andi.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction3Andi.f90

atomsymfunction3.o: $(RUNNER_SRC_DIR)atomsymfunction3.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction3.f90

atomsymfunction4.o: $(RUNNER_SRC_DIR)atomsymfunction4.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction4.f90

atomsymfunction5.o: $(RUNNER_SRC_DIR)atomsymfunction5.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction5.f90

atomsymfunction6.o: $(RUNNER_SRC_DIR)atomsymfunction6.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction6.f90

atomsymfunction8.o: $(RUNNER_SRC_DIR)atomsymfunction8.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction8.f90

atomsymfunction9.o: $(RUNNER_SRC_DIR)atomsymfunction9.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)atomsymfunction9.f90

calconenn.o: $(RUNNER_SRC_DIR)calconenn.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)calconenn.f90

checkelement.o: $(RUNNER_SRC_DIR)checkelement.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)checkelement.f90

check_type.o: $(RUNNER_SRC_DIR)check_type.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)check_type.f90

convert_frequencies.o: $(RUNNER_SRC_DIR)convert_frequencies.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)convert_frequencies.f90

dia_hessian.o: $(RUNNER_SRC_DIR)dia_hessian.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)dia_hessian.f90

getatomsymfunctions.o: $(RUNNER_SRC_DIR)getatomsymfunctions.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getatomsymfunctions.f90

getatomsymfunctions_sfg.o: $(RUNNER_SRC_DIR)getatomsymfunctions_sfg.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getatomsymfunctions_sfg.f90

getcutoff.o: $(RUNNER_SRC_DIR)getcutoff.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getcutoff.f90

getddnodes_values.o: $(RUNNER_SRC_DIR)getddnodes_values.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getddnodes_values.f90

getdnodes_values.o: $(RUNNER_SRC_DIR)getdnodes_values.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getdnodes_values.f90

getgroupcutoffvalues.o: $(RUNNER_SRC_DIR)getgroupcutoffvalues.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getgroupcutoffvalues.f90

getgroupneighlist.o: $(RUNNER_SRC_DIR)getgroupneighlist.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getgroupneighlist.f90

getlistdim.o: $(RUNNER_SRC_DIR)getlistdim.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getlistdim.f90

getneighboridxatomic_para.o: $(RUNNER_SRC_DIR)getneighboridxatomic_para.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getneighboridxatomic_para.f90

getneighborsatomic_para.o: $(RUNNER_SRC_DIR)getneighborsatomic_para.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getneighborsatomic_para.f90

getshortatomic.o: $(RUNNER_SRC_DIR)getshortatomic.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getshortatomic.f90

getsymfunctionderivatives.o: $(RUNNER_SRC_DIR)getsymfunctionderivatives.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getsymfunctionderivatives.f90

getsymfunctionsecondderivatives.o: $(RUNNER_SRC_DIR)getsymfunctionsecondderivatives.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getsymfunctionsecondderivatives.f90

getvibrationalfrequencies.o: $(RUNNER_SRC_DIR)getvibrationalfrequencies.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getvibrationalfrequencies.f90

getvolume.o: $(RUNNER_SRC_DIR)getvolume.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)getvolume.f90

mpi_dummy_routines.o: $(RUNNER_SRC_DIR)mpi_dummy_routines.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)mpi_dummy_routines.f90

mpifitdistribution.o: $(RUNNER_SRC_DIR)mpifitdistribution.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)mpifitdistribution.f90

neighbor_para_short.o: $(RUNNER_SRC_DIR)neighbor_para_short.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)neighbor_para_short.f90

nuccharge.o: $(RUNNER_SRC_DIR)nuccharge.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)nuccharge.f90

predictionshortatomic.o: $(RUNNER_SRC_DIR)predictionshortatomic.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)predictionshortatomic.f90

sortelements.o: $(RUNNER_SRC_DIR)sortelements.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)sortelements.f90

sortsymfunctions.o: $(RUNNER_SRC_DIR)sortsymfunctions.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)sortsymfunctions.f90

translate.o: $(RUNNER_SRC_DIR)translate.f90
	$(FC) $(FFLAGS) -c $(RUNNER_SRC_DIR)translate.f90


serial: ./md_tian2.serial.x
./md_tian2.serial.x: $(MODULES_MPI_DUMMY) $(MODULES) $(SUBROUTINES) $(MPI_DUMMY_SUBROUTINES)
	$(FC) $(FFLAGS) -o $@ \
		$(SUBROUTINES) $(MODULES_MPI_DUMMY) $(MODULES) $(MPI_DUMMY_SUBROUTINES) $(LIB)

clean:
	rm -f *.o *.mod *.x

help:
	@echo ''
	@echo 'make serial		serial version, default'
	@echo 'make clean		delete all object, module and binary files'
	@echo ''
