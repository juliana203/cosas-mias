%chk=aox_tp2.chk
%nproc=2
%mem=500MB

#p PBEPBE/6-31G** POP(MK) IOP(6/33=2) scf=direct Test geom=allcheck guess=read
