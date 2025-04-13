insert_line = "username=wiener&password=peter"

with open('carlosBrute.txt', 'r') as file:
    wordlist = file.readlines()

with open('carlosBruteModified.txt', 'w') as file:
    for i in range(len(wordlist)):
        file.write(wordlist[i].strip() + '\n')

        if (i + 1) % 2 == 0:
            file.write(insert_line + '\n')

print("modified wordlist saved to 'carlosBruteModified.txt'")