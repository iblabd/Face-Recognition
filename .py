import os
import shutil

path = "C:/Users/LENOVO/Desktop/Face-Recognition/images/"
res = os.listdir(path)

nama_siswa = []
parent_dir = "C:/Users/LENOVO/Desktop/Face-Recognition/"

for each in res:
    person = os.path.splitext(each)[0]
    nama_siswa.append(person)
    
    directory = person
    temp_path = os.path.join(parent_dir+"/tfasset", directory) 
    
    os.mkdir(temp_path)
    
    source = f"{path}/{each}"
    destination = f"{parent_dir}tfasset/{person}/{each}"
    dest = shutil.move(source, destination)