class Outer:
    def __init__(self):
        pass
    def outer_method(self):
        print("this is outer method")
    class Inner:
        def __init(self):
            pass
        def main(self):
            outer = Outer().outer_method()

Outer().Inner().main()
        