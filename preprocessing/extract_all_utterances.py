import os


def get_service(service):
    return service.split("_")[0]


def get_utterances(path):
    data_types = ["train", "valid", "test"]

    in_lines, out_lines, intents = [], [], []
    for data in data_types:
        lines = open(path + data + "/seq.in", "r", encoding='utf-8').readlines()
        in_lines.extend([line.strip() for line in lines if len(line) > 0])

        lines = open(path + data + "/seq.out", "r", encoding='utf-8').readlines()
        out_lines.extend([line.strip() for line in lines if len(line) > 0])

        lines = open(path + data + "/label", "r", encoding='utf-8').readlines()
        intents.extend([line.strip() for line in lines if len(line) > 0])

    all_lines = {}
    for index in range(len(in_lines)):
        if intents[index] not in all_lines:
            all_lines[intents[index]] = list()

        all_lines[intents[index]].append(in_lines[index] + "\t" + out_lines[index])

    return all_lines


def write_lines(path, lines, limit=None):
    others, to_pop = [], []
    for k, v in lines.items():
        if len(v) < limit:
            others.extend(v)
            to_pop.append(k)

    if len(others) > 0:
        lines["others"] = others

    for item in to_pop:
        lines.pop(item)

    for k, v in lines.items():
        if not os.path.exists(path + k):
            os.makedirs(path + k)

        f = open(path + k + "/" + k + ".txt", "w", encoding='utf-8')
        for item in v:
            f.write(item + "\n")
        f.close()


if __name__ == '__main__':
    input_path = "../raw_data/"
    out_path = "../data/"
    dataset = "snips"

    hack_map = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
                "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten",
                "11": "eleven", "12": "twelve", "13": "thirteen", "14": "fourteen", "15": "fifteen",
                "20": "twenty"}

    all_sentences = get_utterances(input_path + dataset + "/")
    limit = 100

    write_lines(out_path + dataset + "/", all_sentences, limit)
    print("results written to:", out_path + dataset)
