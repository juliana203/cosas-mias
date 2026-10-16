%chk=../tiol/tiol_dft_3.chk
%nproc=2
%mem=500mb

#P OPT B3LYP 6-31G** Freq pop=NPA guess=read geom=allcheck
