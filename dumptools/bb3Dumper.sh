#!/bin/bash

python dumpAll_bb3.py $1 --FED 1308 &
python dumpAll_bb3.py $1 --FED 1309 &
python dumpAll_bb3.py $1 --FED 1310 &
python dumpAll_bb3.py $1 --FED 1311 &
python dumpAll_bb3.py $1 --FED 1312 &
python dumpAll_bb3.py $1 --FED 1313 &
python dumpAll_bb3.py $1 --FED 1314 &

python dumpAll_bb3.py $1 --FED 1296 &
python dumpAll_bb3.py $1 --FED 1297 &
python dumpAll_bb3.py $1 --FED 1298 &
python dumpAll_bb3.py $1 --FED 1299 &
python dumpAll_bb3.py $1 --FED 1300 &
python dumpAll_bb3.py $1 --FED 1301 &
python dumpAll_bb3.py $1 --FED 1302 &

python dumpAll_bb3.py $1 --FED 1332 &
python dumpAll_bb3.py $1 --FED 1333 &
python dumpAll_bb3.py $1 --FED 1334 &
python dumpAll_bb3.py $1 --FED 1335 &
python dumpAll_bb3.py $1 --FED 1336 &
python dumpAll_bb3.py $1 --FED 1337 &
python dumpAll_bb3.py $1 --FED 1338 &

python dumpAll_bb3.py $1 --FED 1320 &
python dumpAll_bb3.py $1 --FED 1321 &
python dumpAll_bb3.py $1 --FED 1322 &
python dumpAll_bb3.py $1 --FED 1323 &
python dumpAll_bb3.py $1 --FED 1324 &
python dumpAll_bb3.py $1 --FED 1325 &
python dumpAll_bb3.py $1 --FED 1326 &

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
if [ -d ./dump_bb3 ] ; then
    echo "./dump_bb3 folder exists. Yay!"
else
    echo "./dump_bb3 not existed :( Making one now.."
    mkdir dump_bb3
fi

MODULE_MAP_SETS=""
ROC_FIT_SETS=""
DEAD_PIXEL_SETS=""
for FED in {1296..1302} {1308..1314} {1320..1326} {1332..1338}
do
    if [ -d ./dump_bb3_FED$FED ] && [ -f ./dump_bb3_FED$FED/bb3_module_maps.root ] ; then
        echo "FED $FED was used."
        MODULE_MAP_SETS=$MODULE_MAP_SETS" dump_bb3_FED$FED/bb3_module_maps.root"
    fi
    if [ -d ./dump_bb3_FED$FED ] && [ -f ./dump_bb3_FED$FED/bb3_roc_fits.root ] ; then
        ROC_FIT_SETS=$ROC_FIT_SETS" dump_bb3_FED$FED/bb3_roc_fits.root"
    fi
    if [ -d ./dump_bb3_FED$FED ] && [ -f ./dump_bb3_FED$FED/deadPixelBySigma.txt ] ; then
        DEAD_PIXEL_SETS=$DEAD_PIXEL_SETS" dump_bb3_FED$FED/deadPixelBySigma.txt"
    fi
done

echo "=> Hadding together into total.."
hadd -v 0 dump_bb3/bb3_module_maps_total.root $MODULE_MAP_SETS
hadd -v 0 dump_bb3/bb3_roc_fits_total.root $ROC_FIT_SETS

echo "=> Printing canvas in .root to PDF.."
python $cwd/printCanvasToPdf.py dump_bb3/bb3_module_maps_total.root dump_bb3/bb3_module_maps_total.pdf &
python $cwd/printCanvasToPdf.py dump_bb3/bb3_roc_fits_total.root dump_bb3/bb3_roc_fits_total.pdf &
wait

echo "$RUN_DIR/dump_bb3/bb3_module_maps_total.pdf is written."
echo "$RUN_DIR/dump_bb3/bb3_roc_fits_total.pdf is written."

echo "=> Deleting total .root files.."
rm dump_bb3/bb3_module_maps_total.root dump_bb3/bb3_roc_fits_total.root
cat $DEAD_PIXEL_SETS > dump_bb3/deadPixelBySigma_total.txt
echo "$RUN_DIR/dump_bb3/deadPixelBySigma_total.txt is written."

cd $cwd
echo
echo "Done."
