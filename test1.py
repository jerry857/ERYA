import traceback
class A():
    def __init__(self,name):
        print("A初始化")
        self.name=name
    def get(self):
        print(self.name)

class B(A):
    def __init__(self):
        super(B,self).__init__("Bname")
        print("B初始化")

    def get(self):
        super(B,self).get()

if __name__ == '__main__':
    class YZM(Exception):
        pass
    try:
        for i in range(10):
            raise YZM
    except Exception as e:
        traceback.print_exc()
        print("except1")