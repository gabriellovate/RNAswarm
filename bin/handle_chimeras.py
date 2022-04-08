import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import itertools
import sys


def parse_genome(genome_file):
    """
    """
    genome_dict = {}

    header = ""
    seq = ""

    with open(genome_file) as f:  # read genome file
        for line in f:  # parse genome file
            if line.startswith(">"):  # parse header
            #* if there is a header already, we store the current sequence
            #* to this header.
                if header:
                    genome_dict[header] = seq
                    #* then we flush the sequence
                    seq = ""
                #* and parse the new header
                header = line.strip().split(" ")[0][1:]  # remove '>' and ' '
            #elif line != "\n":  # parse sequence and skips newlines
            else:
                #* if no header is detected, we append the new line
                #* to the current sequence
                seq += line.strip()
                #genome_dict[name] = line.strip()  # append sequence to entry
        #* after the last line, we have to store
        #* the last sequence as well. Since no new line with ">" occurs, we
        #* do this manually
        genome_dict[header] = seq
    return genome_dict


def make_combination_array(genome_dict):
    """
    Creates a dictionarry of numpy array of all possible genome segement combinations.
    Use parse_genome() to create genome_dict.
    """
    combination_arrays = {}
    segments = list(genome_dict.keys())

    # segment_combinations = [
    #     segment_combination
    #     for segment_combination in itertools.combinations_with_replacement(segments, 2)
    # ]
    # * while I usually appreciate the usage of list comprehensions, you can directly transform
    # * the iterator to a list. Actually, we also could just put the iterator in the for loop.
    # * should work as well. Is a tad more memory efficient.
    segment_combinations = list(itertools.combinations_with_replacement(segments,2))

    for segment_combination in segment_combinations:
    # for segment_combination in itertools.combinations_with_replacement(segments,2): # * this should work as well
        combination_arrays[segment_combination] = np.zeros(
            (
                len(genome_dict[segment_combination[0]]),
                len(genome_dict[segment_combination[1]]),
            )
        )
    return combination_arrays


def parse_trns_file(trns_file):
    """
    Parse segemehl .trns.txt file and return a dictionary with mappings and values.
    """
    trns_dict = {}
    with open(trns_file) as f:
        for line in f:
            line = line.strip().split("\t")
            line = line[0].split(",") + line[1].split(",") + line[2].split(",")
            trns_dict[line[-1]] = {
                "mapping01": {
                    "ref-chr": line[0],
                    "ref-pos": int(line[1]),
                    "ref-strand": line[2],
                    "start-in-read": int(line[3]),
                    "align-length": int(line[4]),
                    "align-edist": int(line[5]),
                    "score": int(line[6]),
                },
                "mapping02": {
                    "ref-chr": line[7],
                    "ref-pos": int(line[8]),
                    "ref-strand": line[9],
                    "start-in-read": int(line[10]),
                    "align-length": int(line[11]),
                    "align-edist": int(line[12]),
                    "score": int(line[13]),
                },
            }
    return trns_dict


def trns_dict_to_combination_array(combination_arrays, trns_dict):
    """
    Fill combination arrays with values from trns_dict.
    """
    for read_id in trns_dict.keys():
        segment01_segment02 = tuple( # ? are those tuples with length 1?  Do we need the tuple? Or could be a list in the first place?
        # ? e.g. segment01_segment02 = [trns_dict[read_id][mapping][ref-chr], trns_dict[read_id][mapping02][ref-chr]] ?
            [
                trns_dict[read_id]["mapping01"]["ref-chr"],
                trns_dict[read_id]["mapping02"]["ref-chr"],
            ]
        )
        segment02_segment01 = tuple(
            [
                trns_dict[read_id]["mapping02"]["ref-chr"],
                trns_dict[read_id]["mapping01"]["ref-chr"],
            ]
        )
        read01_direction = trns_dict[read_id]["mapping01"]["ref-strand"]
        read02_direction = trns_dict[read_id]["mapping02"]["ref-strand"]
        if segment01_segment02 in combination_arrays.keys():
            if read01_direction == "+" and read02_direction == "+":
                combination_arrays[segment01_segment02][
                    trns_dict[read_id]["mapping01"]["ref-pos"] : trns_dict[read_id][
                        "mapping01"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping01"]["align-length"],
                    trns_dict[read_id]["mapping02"]["ref-pos"] : trns_dict[read_id][
                        "mapping02"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping02"]["align-length"],
                ] += 1  # ? was bin ich lesend?
            elif read01_direction == "-" and read02_direction == "-":
                combination_arrays[segment01_segment02][
                    trns_dict[read_id]["mapping01"]["ref-pos"]
                    - trns_dict[read_id]["mapping01"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping01"]["ref-pos"],
                    trns_dict[read_id]["mapping02"]["ref-pos"]
                    - trns_dict[read_id]["mapping02"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping02"]["ref-pos"],
                ] += 1
            elif read01_direction == "-" and read02_direction == "+":
                combination_arrays[segment01_segment02][
                    trns_dict[read_id]["mapping01"]["ref-pos"]
                    - trns_dict[read_id]["mapping01"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping01"]["ref-pos"],
                    trns_dict[read_id]["mapping02"]["ref-pos"] : trns_dict[read_id][
                        "mapping02"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping02"]["align-length"],
                ] += 1
            elif read01_direction == "+" and read02_direction == "-":
                combination_arrays[segment01_segment02][
                    trns_dict[read_id]["mapping01"]["ref-pos"] : trns_dict[read_id][
                        "mapping01"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping01"]["align-length"],
                    trns_dict[read_id]["mapping02"]["ref-pos"]
                    - trns_dict[read_id]["mapping02"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping02"]["ref-pos"],
                ] += 1
        elif segment02_segment01 in combination_arrays.keys():
            if read01_direction == "+" and read02_direction == "+":
                combination_arrays[segment02_segment01][
                    trns_dict[read_id]["mapping02"]["ref-pos"] : trns_dict[read_id][
                        "mapping02"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping02"]["align-length"],
                    trns_dict[read_id]["mapping01"]["ref-pos"] : trns_dict[read_id][
                        "mapping01"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping01"]["align-length"],
                ] += 1
            elif read01_direction == "-" and read02_direction == "-":
                combination_arrays[segment02_segment01][
                    trns_dict[read_id]["mapping02"]["ref-pos"]
                    - trns_dict[read_id]["mapping02"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping02"]["ref-pos"],
                    trns_dict[read_id]["mapping01"]["ref-pos"]
                    - trns_dict[read_id]["mapping01"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping01"]["ref-pos"],
                ] += 1
            elif read01_direction == "-" and read02_direction == "+":
                combination_arrays[segment02_segment01][
                    trns_dict[read_id]["mapping02"]["ref-pos"]
                    - trns_dict[read_id]["mapping02"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping02"]["ref-pos"],
                    trns_dict[read_id]["mapping01"]["ref-pos"] : trns_dict[read_id][
                        "mapping01"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping01"]["align-length"],
                ] += 1
            elif read01_direction == "+" and read02_direction == "-":
                combination_arrays[segment02_segment01][
                    trns_dict[read_id]["mapping02"]["ref-pos"] : trns_dict[read_id][
                        "mapping02"
                    ]["ref-pos"]
                    + trns_dict[read_id]["mapping02"]["align-length"],
                    trns_dict[read_id]["mapping01"]["ref-pos"]
                    - trns_dict[read_id]["mapping01"]["align-length"] : trns_dict[
                        read_id
                    ]["mapping01"]["ref-pos"],
                ] += 1
            else:
                print("exception caught")


def parse_chim_file(chim_file):
    chim_dict = {}
    line_number = 0
    with open(chim_file) as f:
        for line in f:
            line = line.strip().split("\t")
            chim_dict[line_number] = {
                "mapping01": {
                    "ref-chr": line[0],
                    "ref_start_position": int(line[1]),
                    "ref_end_position": int(line[2]),
                },
                "mapping02": {
                    "ref-chr": line[3],
                    "ref_start_position": int(line[4]),
                    "ref_end_position": int(line[5]),
                },
            }
            line_number += 1
    return chim_dict


def __convert_to_int(element):
    if element.isdigit():
        return int(element)
    else:
        return element

def bwaChimera2heatmap(chimFile,interaction_arrays):
    """
    """
    with open(chimFile) as inputStream:
        for idx, line in enumerate(inputStream):
            currentRow = line.strip().split("\t")
            currentRow = list(map(__convert_to_int, currentRow))
            interaction = []
            if currentRow[1] > currentRow[2]:
                interaction += currentRow[0] + currentRow[2] + currentRow[1]
            else:
                interaction += currentRow[:3]
           
            if currentRow[4] > currentRow[5]:
                interaction += [currentRow[3]] + [currentRow[5]] + [currentRow[4]]
            else:
                interaction += currentRow[3:]

            if (interaction[0],interaction[3]) not in interaction_arrays:
                interaction = interaction[3:] + interaction[0:3]
            fill_heatmap(interaction,interaction_arrays)


def fill_heatmap(interaction, interaction_arrays):
    """
    """
    firstSegment = interaction[0]
    secondSegment = interaction[3]
    interaction_arrays[(firstSegment,secondSegment)][interaction[1] : interaction[2], interaction[4] : interaction[5]] += 1


def chim_dict_to_combination_array(combination_arrays, chim_dict):
    """
    Fill combination arrays with values from chim_dict.
    """
    for line_number in chim_dict.keys():
        segment01_segment02 = tuple(
            [
                chim_dict[line_number]["mapping01"]["ref-chr"],
                chim_dict[line_number]["mapping02"]["ref-chr"],
            ]
        )
        segment02_segment01 = tuple(
            [
                chim_dict[line_number]["mapping02"]["ref-chr"],
                chim_dict[line_number]["mapping01"]["ref-chr"],
            ]
        )
        read01_direction = ""
        read02_direction = ""
        if (
            chim_dict[line_number]["mapping01"]["ref_start_position"]
            < chim_dict[line_number]["mapping01"]["ref_end_position"]
        ):
            read01_direction = "+"
        elif (
            chim_dict[line_number]["mapping01"]["ref_start_position"]
            > chim_dict[line_number]["mapping01"]["ref_end_position"]
        ):
            read01_direction = "-"
        else:
            print("Error in read01 direction")
        if (
            chim_dict[line_number]["mapping02"]["ref_start_position"]
            < chim_dict[line_number]["mapping02"]["ref_end_position"]
        ):
            read02_direction = "+"
        elif (
            chim_dict[line_number]["mapping02"]["ref_start_position"]
            > chim_dict[line_number]["mapping02"]["ref_end_position"]
        ):
            read02_direction = "-"
        else:
            print("Error in read02 direction")
        if segment01_segment02 in combination_arrays.keys():
            if read01_direction == "+" and read02_direction == "+":
                combination_arrays[segment01_segment02][
                    chim_dict[line_number]["mapping01"][
                        "ref_start_position"
                    ] : chim_dict[line_number]["mapping01"]["ref_end_position"],
                    chim_dict[line_number]["mapping02"][
                        "ref_start_position"
                    ] : chim_dict[line_number]["mapping02"]["ref_end_position"],
                ] += 1
            elif read01_direction == "-" and read02_direction == "-":
                combination_arrays[segment01_segment02][
                    chim_dict[line_number]["mapping01"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping01"]["ref_start_position"],
                    chim_dict[line_number]["mapping02"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping02"]["ref_start_position"],
                ] += 1
            elif read01_direction == "-" and read02_direction == "+":
                combination_arrays[segment01_segment02][
                    chim_dict[line_number]["mapping01"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping01"]["ref_start_position"],
                    chim_dict[line_number]["mapping02"][
                        "ref_start_position"
                    ] : chim_dict[line_number]["mapping02"]["ref_end_position"],
                ] += 1
            elif read01_direction == "+" and read02_direction == "-":
                combination_arrays[segment01_segment02][
                    chim_dict[line_number]["mapping01"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping01"]["ref_start_position"],
                    chim_dict[line_number]["mapping02"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping02"]["ref_start_position"],
                ] += 1
        elif segment02_segment01 in combination_arrays.keys():
            if read01_direction == "+" and read02_direction == "+":
                combination_arrays[segment02_segment01][
                    chim_dict[line_number]["mapping02"][
                        "ref_start_position"
                    ] : chim_dict[line_number]["mapping02"]["ref_end_position"],
                    chim_dict[line_number]["mapping01"][
                        "ref_start_position"
                    ] : chim_dict[line_number]["mapping01"]["ref_end_position"],
                ] += 1
            elif read01_direction == "-" and read02_direction == "-":
                combination_arrays[segment02_segment01][
                    chim_dict[line_number]["mapping02"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping02"]["ref_start_position"],
                    chim_dict[line_number]["mapping01"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping01"]["ref_start_position"],
                ] += 1
            elif read01_direction == "-" and read02_direction == "+":
                combination_arrays[segment02_segment01][
                    chim_dict[line_number]["mapping02"][
                        "ref_start_position"
                    ] : chim_dict[line_number]["mapping02"]["ref_end_position"],
                    chim_dict[line_number]["mapping01"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping01"]["ref_start_position"],
                ] += 1
            elif read01_direction == "+" and read02_direction == "-":
                combination_arrays[segment02_segment01][
                    chim_dict[line_number]["mapping02"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping02"]["ref_start_position"],
                    chim_dict[line_number]["mapping01"]["ref_end_position"] : chim_dict[
                        line_number
                    ]["mapping01"]["ref_start_position"],
                ] += 1
            else:
                print("exception caught")


def plot_heatmap(array, output_dir, filename, combination_0, combination_1):
    heatmap = sns.heatmap(array, square=True, cmap="YlGnBu_r")
    heatmap.set(xlabel=str(combination_1), ylabel=str(combination_0))
    plt.figure()
    heatmap.figure.savefig(f"{output_dir}/{filename}", bbox_inches="tight")
    plt.close("all")


def main():
    # * see below. I put these lines here as they do not
    # * change, no matter the if result.
    genome_file_path = sys.argv[1]
    genome_dict = parse_genome(genome_file_path)
    interaction_arrays = make_combination_array(genome_dict)
    readsOfInterest = sys.argv[2]

    # ! We can use argparse (or docopt, but thats an extra library)
    # ! to handle the input parsing and optional parameter better
    if sys.argv[4] == "--segemehl_mode":
        # ! This is redundant. It does not matter whether
        # ! argv[4] is segemehl oder bwa, you are reading the genome anyway.
        #! I moved it in front of the if condition
        trns_dict = parse_trns_file(readsOfInterest)
        trns_dict_to_combination_array(interaction_arrays, trns_dict)
    elif sys.argv[4] == "--bwa_mode":
        bwaChimera2heatmap(readsOfInterest,interaction_arrays)
        #chim_dict = parse_chim_file(readsOfInterest)
        #chim_dict_to_combination_array(interaction_arrays, chim_dict)

    # * same as above. the for loop is the same
    # * for both if conditions. So, it can be outside the if clause
    for combination, array in interaction_arrays.items():
     plot_heatmap(
         array,
         sys.argv[3],
         f"{combination[0]}_{combination[1]}",
         combination[0],
         combination[1],
     )


if __name__ == "__main__":
    main()

# * general remark / notes:
# * It feels like we are doing way to much parsing here.
# * In the end, we just need to know which reads maps to what segment
# * and where it mapped. The alignment length and everything can be calculated that way.
# * By parsing every field from the trns.splice.txt and chimera.txt respectively, 
# * your dictionaries are bloated as hell which, in turn, leads to the spaghetti code.