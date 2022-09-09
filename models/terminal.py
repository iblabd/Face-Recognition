from Face import Face
from termcolor import colored

def main():
    faces = Face()
    
    while True:
        options = input(colored(">>> ", "cyan"))
        if options == "encode":
            face_encode = faces.encode(path="images/")
            faces.JSON().write(face_encode)
        if options == "update":
            faces.JSON().update()
        elif options == "clear" or options == "truncate":
            faces.JSON().clear()
        elif options == "q":
            print("Exitting...")
            break

main()