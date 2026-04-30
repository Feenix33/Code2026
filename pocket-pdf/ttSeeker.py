# tests the seek function to rewind a file. assumes input.txt has 4+ lines

n = 0
with open('input.txt', 'r') as f:
    last_pos = f.tell()
    line = f.readline()
    print (line.strip())
    n += 1
    if n == 2:
        f.seek(last_pos)  # Rewind to the last position before reading the line
        print ("Breaking and rewinding")
        break
    
    while True:
        line = f.readline()
        if not line:
            break
        print (line.strip())

print ("Fini")