# Fresco_DSL
Based on https://ozgesurer.github.io/software/tutorials

cd /home/sun/app/content/

git clone https://github.com/LLNL/Frescox

mkdir Frescoxex

cd Frescox/source

geany makefile
MACH=linux		# linux generic f90
INST = cp  sfrescox frescox fr2nl /home/sun/app/content/Frescoxex ; chmod a+rx /home/sun/app/content/Frescoxex  /home/sun/app/content/Frescoxex

make
make install
make clean

geany ~/.bashrc
export PATH=/home/sun/app/content/Frescoxex:$PATH

cd /home/sun/app/content/Frescox/test

frescox < lane20.nin > lane20.out

On fishtank:

cd /mnt/analysis/triumf_s2193/sun/Fresco_DSL/

git clone https://github.com/LLNL/Frescox

mkdir Frescoxex

cd Frescox/source

geany makefile
MACH=linux		# linux generic f90
INST = cp  sfrescox frescox fr2nl /mnt/analysis/triumf_s2193/sun/Fresco_DSL/Frescoxex ; chmod a+rx /mnt/analysis/triumf_s2193/sun/Fresco_DSL/Frescoxex  /mnt/analysis/triumf_s2193/sun/Fresco_DSL/Frescoxex

make MACH=gfortran
make MACH=gfortran install
make clean

geany ~/.bashrc
export PATH=/mnt/analysis/triumf_s2193/sun/Fresco_DSL/Frescoxex:$PATH
source ~/.bashrc
cd /mnt/analysis/triumf_s2193/sun/Fresco_DSL/Frescox/test

frescox < lane20.nin > lane20.out
