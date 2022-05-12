#!/usr/bin/env python3

"""table maker.

Usage:
  art_templater.py -i <interaction_reads> -g <genomic_reads> -t <trans_file> -b <bam_file>
  art_templater.py -i <interaction_reads> -g <genomic_reads> -c <chim_file> -b <bam_file>

Options:
  -h --help                              Show this screen.
  -i --interactions=<interaction_reads>  fastq file with interaction reads 
  -g --genome=<genomic_reads>             fastq file with genomic reads
  -t --trans=<trans_file>                trans file with trans spliced reads (generated by segemehl)
  -c --chim=<chim_file>                  chim file from bwa-mem mappings (generated by custom script)
  -b --bam=<bam_file>                    mapped reads in bam format
"""
from docopt import docopt
import pysam


def get_ids(fastq_file):
    """
    get the ids of the reads in the fastq file
    """
    id_list = []
    with open(fastq_file, "r") as fastq:
        for line in fastq:
            if line.startswith("@"):
                id_list.append(line.split()[0][1:])
    return id_list


def get_yz_flags(bam_file):
    """
    get the YZ:Z: flags of the reads in the bam file
    Args:
        bam_file (str): Path to BAM file.

    Returns:
        dict: Dictionary of flags, with read id as key and YZ:Z: flag as value.
    """
    yz_tags_dict = {}
    with pysam.AlignmentFile(bam_file, "rb") as bam:
        for read in bam:
            for tag in read.tags:
                if tag[0] == "YZ":
                    yz_tags_dict[read.query_name] = int(tag[1])
    return yz_tags_dict


def get_unmapped_reads(bam_file):
    """
    get the ids of the unmapped reads in the bam file
    """
    unmapped_reads = set()
    with pysam.AlignmentFile(bam_file, "rb") as bam:
        for read in bam:
            if read.is_unmapped:
                unmapped_reads.add(read.query_name)
    return unmapped_reads


def get_chim_ids(chim_file):
    """
    get the ids of the chimeric reads in the chim file
    """
    chim_ids = set()
    with open(chim_file, "r") as chim_file:
        for line in chim_file:
            chim_ids.add(line.strip().split("\t")[0])
    return chim_ids


def make_confusion_matrix_segemehl(genome_fastq, interactions_fastq, bam_file):
    """
    make a confusion matrix from the ids and flags
    """
    confusion_matrix = {
        "true_negative": 0,
        "false_positive": 0,
        "false_negative": 0,
        "true_positive": 0,
        "unmapped_genome": 0,
        "unmapped_interaction": 0,
        "total": 0,
    }

    ids_genome = get_ids(genome_fastq)
    ids_interactions = get_ids(interactions_fastq)
    flags_dict = get_yz_flags(bam_file)

    for id in ids_genome:
        if id not in flags_dict.keys():
            confusion_matrix["unmapped_genome"] += 1
        elif flags_dict[id] != 8:
            confusion_matrix["true_negative"] += 1
        elif flags_dict[id] == 8:
            confusion_matrix["false_positive"] += 1
    for id in ids_interactions:
        if id not in flags_dict.keys():
            confusion_matrix["unmapped_interaction"] += 1
        elif flags_dict[id] != 8:
            confusion_matrix["false_negative"] += 1
        elif flags_dict[id] == 8:
            confusion_matrix["true_positive"] += 1
    confusion_matrix["total"] = (
        confusion_matrix["true_negative"]
        + confusion_matrix["false_positive"]
        + confusion_matrix["false_negative"]
        + confusion_matrix["true_positive"]
        + confusion_matrix["unmapped"]
    )
    return confusion_matrix


def make_confusion_matrix_bwa(genome_fastq, interactions_fastq, chim_file, bam_file):
    """
    make a confusion matrix from the ids and flags
    """
    confusion_matrix = {
        "true_negative": 0,
        "false_positive": 0,
        "false_negative": 0,
        "true_positive": 0,
        "unmapped_genome": 0,
        "unmapped_interaction": 0,
        "total": 0,
    }

    unmapped = get_unmapped_reads(bam_file)
    ids_genome = get_ids(genome_fastq)
    ids_interactions = get_ids(interactions_fastq)
    chim_ids = get_chim_ids(chim_file)

    for id in ids_genome:
        if id in unmapped:
            confusion_matrix["unmapped_genome"] += 1
        elif id not in chim_ids:
            confusion_matrix["true_negative"] += 1
        elif id in chim_ids:
            confusion_matrix["false_positive"] += 1
    for id in ids_interactions:
        if id in unmapped:
            confusion_matrix["unmapped_interaction"] += 1
        elif id in chim_ids:
            confusion_matrix["true_positive"] += 1
        elif id not in chim_ids and id in mapped:
            confusion_matrix["false_negative"] += 1

    confusion_matrix["total"] = (
        confusion_matrix["true_negative"]
        + confusion_matrix["false_positive"]
        + confusion_matrix["false_negative"]
        + confusion_matrix["true_positive"]
        + confusion_matrix["unmapped_interaction"]
        + confusion_matrix["unmapped_genome"]
    )
    return confusion_matrix


def main():
    arguments = docopt(__doc__)
    if arguments["--chim"]:
        confusion_matrix = make_confusion_matrix_bwa(
            arguments["--genome"],
            arguments["--interactions"],
            arguments["--chim"],
            arguments["--bam"],
        )
    elif arguments["--segemehl"]:
        confusion_matrix = make_confusion_matrix_segemehl(
            arguments["--genome"], arguments["--interactions"], arguments["--bam"]
        )
    print(
        "| | interaction | genome |\n"
        + "|----------------------|-------------|---------|\n"
        + f"| chimeric mapping | {confusion_matrix['true_positive']} | {confusion_matrix['false_positive']} |\n"
        + f"| non-chimeric mapping | {confusion_matrix['false_negative']} | {confusion_matrix['true_negative']} |\n"
        + f"| unmapped | {confusion_matrix['unmapped_interaction']} | {confusion_matrix['unmapped_genome']} |"
    )


if __name__ == "__main__":
    main()
