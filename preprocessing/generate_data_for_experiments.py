import argparse
import json
import os
from functools import reduce
import random


def all_intents(path):
    all_intents = [x[0].replace(path, "") for x in os.walk(path) if len(x[0].replace(path, "")) > 0
                   and x[0].replace(path, "")[0] != "."]
    return all_intents


def get_slots(line):
    label = line.split("\t")[1]
    slot_type = [token[2:] for token in label.split()
                 if token[0] != "O" and token[0] != "I"]
    return slot_type


def get_all_slots(lines):
    all_slots = [get_slots(line) for line in lines]
    all_slots = reduce(lambda x, y: x + y, all_slots)
    return list(set(all_slots))


def gen_positive(sentence, label, slots, slot2desc, others, step1_labels=False):
    if step1_labels:
        iob = " ".join([token[0] for token in label.split()])
    pos = []
    for slot in slots:
        new_label = ["B" if token[0] == "B" and token[2:] == slot
                     else ("I" if token[0] == "I" and token[2:] == slot else "O")
                     for token in label.split()]
        if step1_labels:
            if slot2desc is not None:
                if slot in slot2desc:
                    pos.append(sentence + "\t" + iob + "\t" + slot2desc[slot] + "\t" + " ".join(new_label))
                elif others is not None and slot in others:
                    pos.append(sentence + "\t" + iob + "\t" + others[slot] + "\t" + " ".join(new_label))
            else:
                pos.append(sentence + "\t" + iob + "\t" + slot.replace("_", " ").replace(".", " ") + "\t" + " ".join(
                    new_label))
        else:
            if slot2desc is not None:
                if slot in slot2desc:
                    pos.append(sentence + "\t" + slot2desc[slot] + "\t" + " ".join(new_label))
                elif others is not None and slot in others:
                    pos.append(sentence + "\t" + others[slot] + "\t" + " ".join(new_label))
            else:
                pos.append(sentence + "\t" + slot.replace("_", " ").replace(".", " ") + "\t" + " ".join(new_label))
    return pos


def gen_neg(sentence, true_label, slots, neg_ratio, slot2desc, others, step1_labels=False):
    if step1_labels:
        iob = " ".join([token[0] for token in true_label.split()])

    label = " ".join(["O"] * len(sentence.split()))
    neg_slots = random.sample(set(slots), neg_ratio) if len(slots) > neg_ratio else slots
    neg = []
    for slot in neg_slots:
        if step1_labels:
            if slot2desc is not None:
                if slot in slot2desc:
                    neg.append(sentence + "\t" + iob + "\t" + slot2desc[slot] + "\t" + label)
                elif others is not None and slot in others:
                    neg.append(sentence + "\t" + iob + "\t" + others[slot] + "\t" + label)
            else:
                neg.append(sentence + "\t" + iob + "\t" + slot.replace("_", " ").replace(".", " ") + "\t" + label)
        else:
            if slot2desc is not None:
                if slot in slot2desc:
                    neg.append(sentence + "\t" + slot2desc[slot] + "\t" + label)
                elif others is not None and slot in others:
                    neg.append(sentence + "\t" + others[slot] + "\t" + label)
            else:
                neg.append(sentence + "\t" + slot.replace("_", " ").replace(".", " ") + "\t" + label)
    return neg


def get_example(line, slots, slot2desc, others=None, neg_ratio=2):
    ex_slots = get_slots(line)
    neg_slots = list(set(slots) - set(ex_slots))

    sen, label = line.split("\t")
    sen = sen.strip()
    if "B" in label:
        pos_ex = gen_positive(sen, label, ex_slots, slot2desc, others, True)
        neg_ex = gen_neg(sen, label, neg_slots, neg_ratio, slot2desc, others, True)

        return pos_ex + neg_ex
    else:
        neg = random.sample(set(slots), 1)[0]
        return [sen + "\t" + label + "\t" + neg.replace("-", " ") + "\t" + label]


def read_data(path):
    in_lines = open(path, "r", encoding='utf-8').readlines()
    return [line.strip() for line in in_lines if len(line) > 0]


def write_out(path, all_examples):
    f = open(path, "w", encoding='utf-8')
    for line in all_examples:
        f.write(line + "\n")
    f.close()


if __name__ == '__main__':
    input_path = "../raw_data/"
    out_path = "../data/"
    dataset = "snips"

    intents = all_intents(out_path + dataset + "/")
    slot2desc, rest = None, None

    for domain in intents:
        in_lines = read_data(out_path + dataset + "/" + domain + "/" + domain + ".txt")

        all_slots = get_all_slots(in_lines)
        all_examples = [get_example(line, all_slots, slot2desc, rest) for line in in_lines]
        all_examples = reduce(lambda x, y: x + y, all_examples)

        f_name = out_path + dataset + "/" + domain + "/" + domain + "_neg.txt"
        write_out(f_name, all_examples)
        print("file written to:", f_name)
