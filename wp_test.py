#!/usr/bin/env python3
# Testing Class variables and inheritence

class ClassA:
    def __init__(self,):
        self.username = 'vladmint'
        self.password= 'vladmint_password'
    
        
        
class ClassB():
    def __init__(self,password,username):
        self.password = password
        self.username = username
        
    





if __name__ == "__main__":
    something_main = ClassA()
    
    something_main_b = ClassB(something_main.username,something_main.password)
    print(something_main_b.username,something_main_b.password)