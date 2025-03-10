TEST = r"D:\Bren\Documents\backups\gmail\200919\All mail Including Spam and Trash-002.mbox"
OUTPUT_FILE = r"D:\Bren\Documents\backups\gmail\200919\summary.txt"

def find_froms():
    test = open(TEST, "r")
    # print dir(test)

    senders = []
    sender_count = {}
    line_count = 0
    failed_parse = []

    while line_count < 100000000000:
        line = test.readline()
        line_count += 1

        if line.startswith("From:"):
            sender_str = line[len("From:"):]

            toks = sender_str.split(" <")

            if toks != 2:
                failed_parse.append(sender_str)
                continue

            sender_name, sender_email = toks
            sender_email = sender_email.split(">")[0]

            if sender_email in sender_count:
                sender_count[sender_email] += 1
            else:
                sender_count[sender_email] = 1

            senders.append((sender_name, sender_email))

        if line is None:
            print "reached end of file"
            break

    test.close()

    print len(senders)

    # for i in senders:
    #     print i
    print "FAILED: ", failed_parse

    output_str = ""

    for sender, count in sender_count.iteritems():
        # print sender, count
        output_str += "{}\t{}\n".format(sender, count)

    with open(OUTPUT_FILE, "w") as f:
        f.write(output_str)

find_froms()
