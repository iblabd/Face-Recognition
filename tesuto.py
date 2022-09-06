import os

formatfile = ["JPG","jpg","JPEG","jpeg"]
arr = os.listdir("images/")[1:]

for string in arr:
    print(os.path.splitext(string)[0])

