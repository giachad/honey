import json
import os

tags = {"script": "sc", "python": "py", "honey": "ho"}

def honeyError(what):
     #print(f"[{tags['honey']}] {what}\n     please open a issue here:\n     github.com/giachad/honey/issues")
     print(f"[{tags['honey']}] {what}")

def checkValue(self, what_):
    print(what_)
    if str(what_).startswith('"'):
        return str(what_.lstrip('"').rstrip('"'))
    what_ = str(what_)
    if isNumberic(what_):
        return float(what_)
    elif self.variables.get(str(what_)):
        return self.variables[what_]
    elif "*" in str(what_) or "+" in str(what_) or "/" in str(what_) or "-" in str(what_):
        try:
            newWhat = self.forVariables(what_)
            return eval(str(newWhat))
        except:
            pass
    elif isJson(what_):
        return json.loads(what_)
    else:
        directory = self.valuePathToFilePath(str(what_).split("[")[0])
        if directory != None:
            if what_.endswith("]"):
                indexed = checkValue(self, what_.split("[")[1].rstrip("]"))
                tempFile = HoneyFile(directory)

                for variable in tempFile.variables:
                    if variable == tempFile:
                        return tempFile.variables[variable]
        else:
            return "nil"
                
def isNumberic(what):
    try:
        float(what)
        return True
    except:
        return False

def isJson(what):
    try:
        json.loads(what)
        return True
    except:
        return False

class Script(object):
    def __init__(self, location) -> None:
        self.location = location
        self.code = ""
        self.variables = {}
        self.functions = {}

        self.file = open(self.location, "r")
        self.code = self.file.readlines()
        self.file.close()

        self.manageFunctions()
        self.manageVariables()

        self.runCode(self.code)

    def manageFunctions(self):
        currentFunctionName = ""

        for line in self.code:
            if "function" in line:
                parametresString = line.rstrip("\n").split("(")[1].rstrip(") {")
                parametres = parametresString.split(", ")
                currentFunctionName = line.split(" ")[1].rstrip(") {").rstrip(parametresString).rstrip("(")
                self.functions[currentFunctionName] = {"parametres": parametres, "lines": []}
            elif "}" in line:
                currentFunctionName = ""
            else:
                if currentFunctionName != "":
                    self.functions[currentFunctionName]["lines"].append(line.lstrip(" ").rstrip("\n"))

    def manageVariables(self):
        for line in self.code:
            if line.startswith("local"):
                variableName = line.split(" ")[1]

                if len(line.split(" ")) >= 3 and line.split(" ")[2] == "=":
                    variableValue = checkValue(self, line.lstrip(line.split(" = ")[0] + " = ").rstrip("\n"))
                    self.variables[variableName] = variableValue
                else:
                    self.variables[variableName] = None

    def valuePathToFilePath(self, what):
        returnString = ""

        for index, thing in enumerate(str(what).split(".")):
            if index != (len(str(what).split(".")) - 1):
                returnString += "/" +str(thing)
            else:
                returnString += "." + thing

        returnString = returnString.lstrip("/")

        if os.path.exists(returnString):
            return returnString
        else:
            honeyError("file does not exist")
            return None

    def forVariables(self, what):
        newWhat = str(what)

        for variable in self.variables:
            newWhat = newWhat.replace(variable, str(self.variables[variable]))

        return str(newWhat)

    def printerPrint(self, where):
        if os.path.exists(where):
            os.startfile(where, "print")

    def getValuesFromBrackets(self, line):
        if "(" in line:
            line = line.split("(")[1]
            if ")" in line:
                line = line.rstrip(")\n")
                return checkValue(self, line)

    def runCode(self, theCode):
        currentLine = 0

        for line in theCode:
            currentLine += 1

            if line.startswith("echo"):
                print(f"[{tags['script']}] "+str(self.getValuesFromBrackets(line)))
            elif self.functions.get(str(line).split("(")[0].rstrip("\n")):
                functionName = str(line).split("(")[0].rstrip("\n")
                
                for index, parametre in enumerate(str(line).split("(")[1].rstrip(")").split(", ")):
                    try:
                        self.variables[self.functions[functionName]["parametres"][index]] = checkValue(self, parametre)
                    except:
                        honeyError("no parametre of index "+str(index))

                self.runCode(self.functions[functionName]["lines"])

class File:
    def __init__(self, location) -> None:
        self.location = str(location)
        self.data = {}

        if self.location.endswith(".honey"):
            try:
                self.__class__ = HoneyFile
                self.__init__(location)
            except:
                honeyError("problem registering a honey script")
        elif self.location.endswith(".json"):
            f = open(self.location, "r")
            self.data = json.loads(f.read())
            f.close()
            print(self.data)

class HoneyFile(object):
    def __init__(self, location) -> None:
        self.location = location
        self.code = ""
        self.variables = {}
        self.functions = {}

        self.file = open(self.location, "r")
        self.code = self.file.readlines()
        self.file.close()

        self.manageFunctions()
        self.manageVariables()

    def manageFunctions(self):
        currentFunctionName = ""

        for line in self.code:
            if "function" in line:
                parametresString = line.rstrip("\n").split("(")[1].rstrip(") {")
                parametres = parametresString.split(", ")
                currentFunctionName = line.split(" ")[1].rstrip(") {").rstrip(parametresString).rstrip("(")
                self.functions[currentFunctionName] = {"parametres": parametres, "lines": []}
            elif "}" in line:
                currentFunctionName = ""
            else:
                if currentFunctionName != "":
                    self.functions[currentFunctionName]["lines"].append(line.lstrip(" ").rstrip("\n"))

    def manageVariables(self):
        for line in self.code:
            if line.startswith("local"):
                variableName = line.split(" ")[1]

                if len(line.split(" ")) >= 3 and line.split(" ")[2] == "=":
                    variableValue = checkValue(self, line.lstrip(line.split(" = ")[0] + " = ").rstrip("\n"))
                    self.variables[variableName] = variableValue
                else:
                    self.variables[variableName] = None
                
    def isNumberic(self, what):
        try:
            float(what)
            return True
        except:
            return False

    def valuePathToFilePath(self, what):
        returnString = ""

        for index, thing in enumerate(str(what).split(".")):
            if index != (len(str(what).split(".")) - 1):
                returnString += "/" +str(thing)
            else:
                returnString += "." + thing

        returnString = returnString.lstrip("/")

        if os.path.exists(returnString):
            return returnString
        else:
            honeyError("file does not exist")
            return None

    def forVariables(self, what):
        newWhat = str(what)

        for variable in self.variables:
            newWhat = newWhat.replace(variable, str(self.variables[variable]))

        return str(newWhat)

    def printerPrint(self, where):
        if os.path.exists(where):
            os.startfile(where, "print")

    def getValuesFromBrackets(self, line):
        if "(" in line:
            line = line.split("(")[1]
            if ")" in line:
                line = line.rstrip(")\n")
                return checkValue(self, line)

    def runCode(self, theCode):
        currentLine = 0

        for line in theCode:
            currentLine += 1

            if line.startswith("echo"):
                print(f"[{tags['script']}] "+str(self.getValuesFromBrackets(line)))
            elif self.functions.get(str(line).split("(")[0].rstrip("\n")):
                functionName = str(line).split("(")[0].rstrip("\n")
                
                for index, parametre in enumerate(str(line).split("(")[1].rstrip(")").split(", ")):
                    try:
                        self.variables[self.functions[functionName]["parametres"][index]] = checkValue(self, parametre)
                    except:
                        honeyError("no parametre of index "+str(index))

                self.runCode(self.functions[functionName]["lines"])

    def isJson(self, what):
        try:
            json.loads(what)
            return True
        except:
            return False

script = Script("script")
