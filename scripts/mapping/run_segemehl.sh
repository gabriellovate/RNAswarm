#!/bin/sh

RESULTS_DIR="/home/ru27wav/Projects/gl_iav-splash_freiburg/results/dadonaite_2019"
READS_DIR="/home/ru27wav/Projects/gl_iav-splash_freiburg/results/dadonaite_2019/01-trimmed_reads"
GENOME_DIR="/home/ru27wav/Projects/gl_iav-splash_freiburg/data/dadonaite_2019/genomes"

mkdir $RESULTS_DIR/02-mappings
INDEXES_DIR="$RESULTS_DIR/02-mappings/segmehl_indexes"
MAPPINGS_DIR="$RESULTS_DIR/02-mappings/segemehl"

mkdir $MAPPINGS_DIR
mkdir $INDEXES_DIR

# Generate indexes for genomes of interest
for GENOME in $GENOME_DIR/*.fasta; do
    segemehl.x -x $INDEXES_DIR/$(basename $GENOME .fasta).idx -d $GENOME 2> $INDEXES_DIR/$(basename $GENOME .fasta).log
done

# Run segemehl with split read mapping enabled
segemehl.x -i $INDEXES_DIR/pr8_dadonaite.idx\
           -d $GENOME_DIR/pr8_dadonaite.fasta\
           -q $READS_DIR/SRR7350059_trimmed.fastq\
           -t 72 -S $MAPPINGS_DIR/SRR7350059\
           > $MAPPINGS_DIR/SRR7350059.sam\
           2> $MAPPINGS_DIR/SRR7350059.log

segemehl.x -i $INDEXES_DIR/pr8_dadonaite.idx\
           -d $GENOME_DIR/pr8_dadonaite.fasta\
           -q $READS_DIR/SRR9637504_trimmed.fastq\
           -t 72 -S $MAPPINGS_DIR/SRR9637504\
            > $MAPPINGS_DIR/SRR9637504.sam\
            2> $MAPPINGS_DIR/SRR9637504.log

segemehl.x -i $INDEXES_DIR/udorn_dadonaite.idx\
           -d $GENOME_DIR/udorn_dadonaite.fasta\
           -q $READS_DIR/SRR7350060_trimmed.fastq\
           -t 72 -S $MAPPINGS_DIR/SRR7350060\
           > $MAPPINGS_DIR/SRR7350060.sam\
           2> $MAPPINGS_DIR/SRR7350060.log

segemehl.x -i $INDEXES_DIR/udorn_dadonaite.idx\
           -d $GENOME_DIR/udorn_dadonaite.fasta\
           -q $READS_DIR/SRR9637509_trimmed.fastq\
           -t 72 -S $MAPPINGS_DIR/SRR9637509\
           > $MAPPINGS_DIR/SRR9637509.sam\
           2> $MAPPINGS_DIR/SRR9637509.log

segemehl.x -i $INDEXES_DIR/wsn_dadonaite.idx\
           -d $GENOME_DIR/wsn_dadonaite.fasta\
           -q $READS_DIR/SRR6388155_trimmed.fastq\
           -t 72 -S $MAPPINGS_DIR/SRR6388155\
           > $MAPPINGS_DIR/SRR6388155.sam\
           2> $MAPPINGS_DIR/SRR6388155.log

segemehl.x -i $INDEXES_DIR/wsn_dadonaite.idx\
           -d $GENOME_DIR/wsn_dadonaite.fasta\
           -q $READS_DIR/SRR6388157_trimmed.fastq\
           -t 72 -S $MAPPINGS_DIR/SRR6388157\
           > $MAPPINGS_DIR/SRR6388157.sam\
           2> $MAPPINGS_DIR/SRR6388157.log