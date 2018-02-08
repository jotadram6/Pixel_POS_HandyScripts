#!/bin/bash

#~ python dumpAll_scurve.py $1 '1308' &
#~ python dumpAll_scurve.py $1 '1309' &
#~ python dumpAll_scurve.py $1 '1310' &
#~ python dumpAll_scurve.py $1 '1311' &
#~ python dumpAll_scurve.py $1 '1312' &
#~ python dumpAll_scurve.py $1 '1313' &
#~ python dumpAll_scurve.py $1 '1314' &

#python dumpAll_scurve.py $1 '1296' &
#python dumpAll_scurve.py $1 '1297' &
#python dumpAll_scurve.py $1 '1298' &
#python dumpAll_scurve.py $1 '1299' &
#python dumpAll_scurve.py $1 '1300' &
#python dumpAll_scurve.py $1 '1301' &
#python dumpAll_scurve.py $1 '1302' &

python dumpAll_scurve.py $1 '1294' &
python dumpAll_scurve.py $1 '1295' &
python dumpAll_scurve.py $1 '1296' &
python dumpAll_scurve.py $1 '1297' &
python dumpAll_scurve.py $1 '1298' &
python dumpAll_scurve.py $1 '1299' &
python dumpAll_scurve.py $1 '1300' &

#~ python dumpAll_scurve.py $1 '1332' &
#~ python dumpAll_scurve.py $1 '1333' &
#~ python dumpAll_scurve.py $1 '1334' &
#~ python dumpAll_scurve.py $1 '1335' &
#~ python dumpAll_scurve.py $1 '1336' &
#~ python dumpAll_scurve.py $1 '1337' &
#~ python dumpAll_scurve.py $1 '1338' &

#~ python dumpAll_scurve.py $1 '1320' &
#~ python dumpAll_scurve.py $1 '1321' &
#~ python dumpAll_scurve.py $1 '1322' &
#~ python dumpAll_scurve.py $1 '1323' &
#~ python dumpAll_scurve.py $1 '1324' &
#~ python dumpAll_scurve.py $1 '1325' &
#~ python dumpAll_scurve.py $1 '1326' &

wait
echo
echo "=> Canvases have been saved into root files."

POS_OUTPUT=$(eval echo \$\{POS_OUTPUT_DIRS\})

if [ -z "$POS_OUTPUT" ] ; then
    printf '\e[31mSource POS setenv.sh first! Exit..\e[0m'
    exit 0
else
    RUN_DIR_BASE="Run_"$(( $1 /1000 *1000))
    RUN_DIR_SUB="Run_"$1
    RUN_DIR=$POS_OUTPUT/$RUN_DIR_BASE/$RUN_DIR_SUB
fi

cwd=$(eval pwd)
cd $RUN_DIR
if [ -d ./dump_scurve ] ; then
    echo "./dump_scurve folder exists. Yay!"
else
    echo "./dump_scurve not existed :( Making one now.."
    mkdir dump_scurve
fi

THRESHOLD_SETS=""
WIDTH_SETS=""
for FED in {1294..1300} #{1296..1302} {1308..1314} {1320..1326} {1332..1338}
do
    if [ -d ./dump_scurve_FED$FED ] && [ -f ./dump_scurve_FED$FED/SCurve_threshold.root ] ; then
        echo "FED $FED was used."
        THRESHOLD_SETS=$THRESHOLD_SETS" dump_scurve_FED$FED/SCurve_threshold.root"
    fi
    if [ -d ./dump_scurve_FED$FED ] && [ -f ./dump_scurve_FED$FED/SCurve_widths.root ] ; then
        WIDTH_SETS=$WIDTH_SETS" dump_scurve_FED$FED/SCurve_widths.root"
    fi
done

echo "=> Hadding together into total.."
hadd -v 0 dump_scurve/SCurve_threshold_total.root $THRESHOLD_SETS
hadd -v 0 dump_scurve/SCurve_widths_total.root $WIDTH_SETS

echo "=> Printing canvas in .root to PDF.."
python $cwd/printCanvasToPdf.py dump_scurve/SCurve_threshold_total.root dump_scurve/SCurve_threshold_total.pdf &
python $cwd/printCanvasToPdf.py dump_scurve/SCurve_widths_total.root dump_scurve/SCurve_widths_total.pdf &
wait

echo "$RUN_DIR/dump_scurve/SCurve_threshold_total.pdf is written."
echo "$RUN_DIR/dump_scurve/SCurve_widths_total.pdf is written."

echo "=> Deleting total .root files.."
rm dump_scurve/SCurve_threshold_total.root dump_scurve/SCurve_widths_total.root

cd $cwd
echo
echo "Done."
