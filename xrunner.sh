#!/usr/bin/env bash

ROOT="absolute path to experimental root folder"

ALGO="csim"
N=500

TEST=$ROOT"/sample.json"
OUT=$ROOT"/out"

SERIES=$ROOT"/series.txt"
DICTIONARY=$ROOT"/model/apc.dict"
LSI=$ROOT"/model/apc.lsi"
INDEX=$ROOT"/model/apc.index"


SIMILARITIES=( at99 at98 at97 at96 at95 at94 at93 at92 at91 at90 t99 t98 t97 t96 t95 t94 t93 t92 t91 t90 n10 n9 n8 n7 n6 n5 n4 n3 n2 n1 )
SELECTIONS=( rawtf wtf maxwtf rawtfidf )


for similarity in "${SIMILARITIES[@]}"
do
    for selection in "${SELECTIONS[@]}"
    do
        result=$OUT"/"$similarity"-"$selection".csv"
        python conduct_experiment.py $ALGO $TEST $N $result --series $SERIES --dictionary $DICTIONARY --lsi $LSI --index $INDEX --sim_opt $similarity --rank_opt $selection
    done
done
