# Fresco_DSL
Based on https://ozgesurer.github.io/software/tutorials

cd /home/sun/app/content/

git clone https://github.com/bandframework/bandframework/

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
