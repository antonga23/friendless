import csv


def parse_log(read_loc, write_loc):
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
