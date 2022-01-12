"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge. 
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
import json
import re
import test_hard

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def is_unlocked(courses_list, target_course):
    if len(CONDITIONS[target_course]) == 0:
        return True 
    return processRequirements(CONDITIONS[target_course]).evaluate(courses_list)


  #######################################
 ###             HELPERS             ###
#######################################


def processRequirements(requirement):
    requirements = cleanRequirements(requirement)
    return doProcess(requirements)

def doProcess(req):
    if len(req) < 1:
        return CourseNode("")
    if len(req) < 2:
        if re.search(r"^[0-9]{1,3}$", req[0]):
            return NumberNode(int(req[0]), [], '0')
        return CourseNode(req[0])
    if ")" in req[0]:
        return CourseNode(req[0])

    curr = req[0]
    nodes = []
    layer = 0
    logic = "or" #TODO ??? 
    if re.search(r'[0-9]{4}', curr):
        for i in range(0,len(req)):
            if req[i].startswith("("):
                layer += req[i].count("(")
                temp = layer
                req[i] = req[i][1:]
                newReq = []
                for word in req[i:]:
                    newReq.append(word)
                    temp = temp - 1 if ")" in word else temp
                    if temp == 0:
                        break
                nodes.append(doProcess(newReq))

            elif ")" in req[i] and i != len(req) - 1:
                if layer == 0:
                    nodes.append(CourseNode(req[i:]))
                layer -= req[i].count(")")

            elif re.search(r'[0-9]{4}', req[i]) and layer <= 0:
                nodes.append(CourseNode(req[i]))

            elif re.search(r'^[0-9]{1,3}$', req[i]):
                nodes.append(doProcess(req[i:]))
            else:
                logic = req[i] if layer <= 0 else logic

        if logic == "or":
            return OrNode(nodes)
        elif logic == "and":
            return AndNode(nodes)
        else:
            return doProcess(req[1:])

    elif curr == "or":
        nodes.append(doProcess(req[1:]))
        return OrNode(nodes)

    elif curr == "and":
        nodes.append(doProcess(req[1:]))
        return AndNode(nodes)

    elif re.search(r"^[0-9]{1,3}$", curr) != None:
        return createNumberNode(req, nodes = [])

    return CourseNode(curr)

def createNumberNode(req, nodes = []):
    level = '0'
    curr = req[0]
    for i in range(len(req)):
        if re.search(r'[0-9]{4}', req[i]) != None:
            nodes.append(CourseNode(req[i]))
        if req[i] in ["and", "or"]:
            nodes.append(doProcess(req[i:]))
        if req[i] == "level":
            level = req[i+1]
        if ")" in req[i]:
            break
    return NumberNode(num = int(curr), nodes = nodes, level = str(level))


def cleanRequirements(string): # return a list of string
    string = string.lower()
    patterns = [r'[0-9]{1,4}', 'or', 'and', r'level']
    words = string.split()
        
    result = []
    for word in words:
        result.extend([word for pattern in patterns if re.search(pattern, word) != None])

    return result 



  #######################################
 ###             OBJECTS             ###
#######################################

class BaseNode:
    def __init__(self):
        pass
    def evaluate(self, courseList) -> bool:
        return True

class CourseNode(BaseNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def evaluate(self, courseList) -> bool:
        if courseList == []:
            return False 
        str = self.name.strip("(").strip(")").strip(",").upper()
        if re.search(r"^[0-9]{4}$", str):
            str = "COMP" + str
        return str in courseList

class AndNode(BaseNode):
    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes
    def evaluate(self, courseList) -> bool:
        for node in self.nodes:
            if node.evaluate(courseList) == False:
                return False 
        return True 
    
class OrNode(BaseNode):
    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes
    def evaluate(self, courseList) -> bool:
        for node in self.nodes:
            if node.evaluate(courseList):
                return True
        return False

class NumberNode(BaseNode):
    def __init__(self, num, nodes, level):
        super().__init__()
        self.num = int(num)
        self.nodes = nodes
        self.level = level
    def evaluate(self, courseList):
        if self.level == '0':
            if len(self.nodes) == 0:
                return len(courseList)*6 >= self.num
            return len([n for n in self.nodes if n.evaluate(courseList)])*6 >= self.num
        else:
            return len([c for c in courseList if c[4] == str(self.level)])*6 >= self.num


  #######################################
 ###             MAIN                ###
#######################################
if __name__ == "__main__":
    assert is_unlocked([], "COMP1511") == True
    assert is_unlocked([], "COMP9301") == False

    assert is_unlocked(["MATH1081"], "COMP3153") == True
    assert is_unlocked(["ELEC2141"], "COMP3211") == True
    assert is_unlocked(["COMP1511", "COMP1521", "COMP1531"], "COMP3153") == False

    assert is_unlocked(["MATH1081", "COMP1511"], "COMP2111") == True
    assert is_unlocked(["COMP1521", "COMP2521"], "COMP3151") == True
    assert is_unlocked(["COMP1917", "DPST1092"], "COMP3151") == False

    assert is_unlocked(["COMP1511", "COMP1521", "COMP1531", "COMP2521"], "COMP4161") == True
    assert is_unlocked(["COMP1511", "COMP1521"], "COMP4161") == False

    assert is_unlocked(["COMP9417", "COMP9418", "COMP9447"], "COMP9491") == True
    assert is_unlocked(["COMP6441"], "COMP9302") == False
    assert is_unlocked(["COMP6441", "COMP64443", "COMP6843", "COMP6445"], "COMP9302") == True
    assert is_unlocked(["COMP1234", "COMP5634", "COMP4834"], "COMP9491") == False
    assert is_unlocked(["COMP3901"], "COMP3902") == False
    assert is_unlocked(["COMP3901", "COMP6441", "COMP6443"], "COMP3902") == False
    assert is_unlocked(["COMP3901", "COMP3441", "COMP3443"], "COMP3902") == True
    assert is_unlocked(["COMP1911", "MTRN2500"], "COMP2121") == True
    assert is_unlocked(["COMP1521"], "COMP2121") == True