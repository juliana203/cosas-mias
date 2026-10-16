%chk=../tiol/tiol_dft_2.chk
%nproc=2
%mem=500mb

#P FREQ PBEPBE 3-21G pop=NPA guess=read geom=allcheck
