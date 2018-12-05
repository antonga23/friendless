import numpy as np
import operator
import csv


def multiset(file_loc, list_col):
    with open(file_loc, "r") as csv_reader:
        reader = csv.reader(csv_reader)

        d = {}
        for row in reader:
            parsed_list = parse_list(row[list_col], convert_to_lower=False)
            for item in parsed_list:
                if item in d:
                    d[item] += 1
                else:
                    d[item] = 1
    return d


def most_grossed_content(file_loc, list_col, hashed_donors):
    with open(file_loc, "r") as csv_reader:
        reader = csv.reader(csv_reader)
        d_ = {}
        for row in reader:
            ls = parse_list(row[list_col])
            link = row[8]
            d_[link] = len(set(ls).intersection(set(hashed_donors)))
        if "event_link" in d_:
            del d_["event_link"]
        d_ = dict(sorted(d_.items(), key=lambda x: -x[1]))
        for link in d_:
            print(d_[link], "->", link)
        return d_


def evaluate_hashtags(file_loc, threshold=0):
    with open(file_loc, "r") as csv_reader:
        reader = csv.reader(csv_reader)
        next(reader)
        hashtags = []
        for row in reader:
            hashtags.extend(parse_list(row[9], convert_to_lower=True))
        hashtags = list(set(hashtags))
        hashtags = sorted(hashtags, key=lambda x: x)

    with open(file_loc, "r") as csv_reader:
        reader = csv.reader(csv_reader)
        next(reader)

        aug = []
        output = []
        for row in reader:
            temp = []
            parsed_list = parse_list(row[9], convert_to_lower=True)
            for main_hashtag in hashtags:
                if main_hashtag in parsed_list:
                    temp.append(1)
                else:
                    temp.append(0)
            aug.append(len(parse_list(row[10])))
            output.append(temp)

        output = list(zip(*output))
        array, tags, aug_col = [], [], []
        for row in range(0, len(output)):
            row_sum = 0
            for element in output[row]:
                row_sum = row_sum + element
            if row_sum > threshold:
                array.append(output[row])
                tags.append(hashtags[row])
                aug_col.append(aug[row])

        d = {}
        solution = np.linalg.lstsq(np.array(array), np.array(aug_col), rcond=None)[0]
        for i in range(len(tags)):
            d[tags[i]] = solution[i]
        return dict(sorted(d.items(), key=lambda x: -x[1]))


def parse_list(string, convert_to_lower=True):
    if string == "[]":
        return []
    string = string.replace("['", "").replace("']", "") \
        .replace("!", "").replace(".", "").replace("?", "") \
        .replace(",", "").replace("'", "").replace("🐾", "") \
        .replace(":", "").replace("[\"", "").replace("\"", "")
    if convert_to_lower:
        string = string.lower()
    return sorted(string.split(" "))


def parse_log(read_loc="friendless_log.txt", write_loc="output.txt"):
    log_file = open(read_loc, "r").readlines()
    df = []
    text = ""
    for line in log_file:
        line = line.replace("\n", "")
        # print(line)
        if ".post text: | " in line:
            text = text + line.replace(".post text: | ", "").strip().strip("\"")
        elif ".num_likes: | " in line:
            likes = line.replace(".num_likes: | ", "").strip()
        elif ".num_loves: | " in line:
            loves = line.replace(".num_loves: | ", "").strip()
        elif ".num_hahas: | " in line:
            hahas = line.replace(".num_hahas: | ", "").strip()
        elif "..num_wows: | " in line:
            wows = line.replace("..num_wows: | ", "").strip()
        elif "..num_sads: | " in line:
            sads = line.replace("..num_sads: | ", "").strip()
        elif "num_angrys: | " in line:
            angrys = line.replace("num_angrys: | ", "").strip()
        elif "num_reacts: | " in line:
            reacts = line.replace("num_reacts: | ", "").strip()
        elif "event_link: | " in line:
            link = line.replace("event_link: | ", "").strip()
        elif "hashtags_used: " in line:
            hashers = line.replace("hashtags_used: ", "").strip()
        elif "who_reacted:" in line:
            who = line.replace("who_reacted:", "").strip()
            df.append([text, likes, loves, hahas, wows, sads, angrys, reacts, link, hashers, who])
            print([text, likes, loves, hahas, wows, sads, angrys, reacts, link, hashers, who])
            text = ""
        else:
            text = text + line.strip().rstrip("\"")

    # Replaces links printed with the column titles
    df[0] = ["post text", "num_likes", "num_loves",
             "num_hahas", "num_wows", "num_sads",
             "num_angrys", "num_reacts", "event_link",
             "hashtags_used", "who_reacted"]

    with open(write_loc, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(df)


def cloudprep_hashtags_reacts(read_loc, reaction_col=7, has_column_header=True):
    with open(read_loc, "r") as csv_reader:
        reader = csv.reader(csv_reader)
        if has_column_header:
            next(reader)
        for row in reader:
            x = parse_list(row[9])
            if len(x) > 0:
                for hashtag in x:
                    scale_by_k(hashtag, int(row[reaction_col]))


def cloudprep_hashtags_frequency(read_loc, has_column_header=True):
    with open(read_loc, "r") as csv_reader:
        reader = csv.reader(csv_reader)
        if has_column_header:
            next(reader)
        k = []
        for row in reader:
            k.extend((parse_list(row[9])))
        print(sorted(set(k)), len(set(k)))


def cloud_prep_posts_reacts(read_loc, reaction_column=7, has_column_header=True):
    with open(read_loc, "r") as csv_reader:
        reader = csv.reader(csv_reader)
        if has_column_header:
            next(reader)
        for row in reader:
            scale_by_k(row[0], int(row[reaction_column]))


def scale_by_k(string, k):
    for x in range(k):
        open("cloud_prep.txt", "a").write(string + "\n")


# cloud_prep_posts_reacts("final.csv")

d = multiset("final.csv", 10)
del d["who_reacted"]
s = ""
d = dict(sorted(d.items(), key=lambda x: -x[1]))
one_hit_wonders, inbetweeners, button_happy = [], [], []
stats = {}
for k in d:
    # print(k, " -> ", d[k])
    # s = s + str(d[k]) + ", "
    if d[k] == 1:
        one_hit_wonders.append(k)
    elif 127 > d[k] > 1:
        inbetweeners.append(k)
    elif 127 <= d[k]:
        button_happy.append(button_happy)
    if d[k] in stats:
        stats[d[k]] += 1
    else:
        stats[d[k]] = 1
# print(s)
# print(len(d))

# Top-Grossing Content
# one_hit_wonders_set = most_grossed_content("final.csv", 10, one_hit_wonders)
# inbetweeners_set = most_grossed_content("final.csv", 10, inbetweeners)
# button_happy_set = most_grossed_content("final.csv", 10, button_happy)

for x in range(1, 16):
    print("\n")
    d = evaluate_hashtags("final.csv", threshold=x)
    print("Threshold value:", x)
    for k in d:
        print(k, "->", d[k])

