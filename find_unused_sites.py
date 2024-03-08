
with open('./websites.txt') as f:
    tenK = [line for line in f]

with open('./processed_ws.txt') as f:
    processed = [line for line in f]
# print(processed)
missing = [ws for ws in tenK if ws not in processed]

with open('./missing_ws.txt', "a") as of:
    for line in missing:
        of.write(line)
    of.close()