#!/bin/sh

nohup mpirun -np 20 ./MohidWater_mpi.exe > Mohid.log
nohup ./MohidDDC.exe
