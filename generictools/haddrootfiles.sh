RUNTYPE=""
RUN=1

CURRDIR=$PWD

if [ $# -eq 0 ]
then
    echo "You need to enter at least run number as argument. Optional can enter type of run"
    return
else
    RUN=$1
    echo "Run number is $1"
fi

if [ $# -gt 1 ]
then
    RUNTYPE=$2
    echo "You specified that the run was about $RUNTYPE"
fi

echo $RUNTYPE

#if alias POS_OUTPUT_DIRS 2>/dev/null; then
if [  `alias | grep $POS_OUTPUT_DIRS | wc -l` != 0 ]
then
    echo "output dir is $POS_OUTPUT_DIRS"
else
    echo "You haven't set up POS, don't know the POS output dir"
    return
fi

RUNBASE=$((${RUN}-${RUN}%1000))

RUNDIR=`echo ${POS_OUTPUT_DIRS}/Run_${RUNBASE}/Run_${RUN}/`
#echo $RUNDIR

cd $RUNDIR

hadd total.root ${RUNTYPE}*.root

cd $CURRDIR