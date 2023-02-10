import requests
import json
import os

tags = {"script": "sc", "python": "py", "honey": "ho"}

variables = {}
functions = {}

def honeyError(what):
     #print(f"[{tags['honey']}] {what}\n     please open a issue here:\n     github.com/giachad/honey/issues")
     print(f"[{tags['honey']}] {what}")

def readlines(where):
    f = open(where, "r")
    c = f.readlines()
    f.close()
    return c

class Script(object):
    def __init__(self, code) -> None:
        self.code = code
        variables = {}
        functions = {}

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
                functions[currentFunctionName] = {"parametres": parametres, "lines": [], "return": None}
            elif "}" in line:
                currentFunctionName = ""
            else:
                if currentFunctionName != "":
                    if line.lstrip(" ").rstrip("\n").startswith("return"):
                        print(self.getValueFromBrackets(line.lstrip(" ").rstrip("\n")))

                        functions[currentFunctionName]["return"] = self.getValueFromBrackets(line.lstrip(" ").rstrip("\n"))

                    functions[currentFunctionName]["lines"].append(line.lstrip(" ").rstrip("\n"))    
                    
    def manageVariables(self):
        for line in self.code:
            if line.startswith("local"):
                variableName = line.split(" ")[1]

                if len(line.split(" ")) >= 3 and line.split(" ")[2] == "=":
                    variableValue = self.checkValue(line.lstrip(line.split(" = ")[0] + " = ").rstrip("\n"))
                    variables[variableName] = variableValue
                else:
                    variables[variableName] = None

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

        for variable in variables:
            newWhat = newWhat.replace(variable, str(variables[variable]))

        return str(newWhat)

    def printerPrint(self, where):
        if os.path.exists(where):
            os.startfile(where, "print")

    def getValueFromBrackets(self, line):
        if "(" in line:
            line = line.split("(")[1]
            if ")" in line:
                line = line.rstrip(")\n")
                return self.checkValue(line)

    def getValuesFromBrackets(self, line):
        if "(" in line:
            line = line.split("(")[1]
            if ")" in line:
                line = line.rstrip(")\n")
                return self.checkValue(line.split(", "))

    def runCode(self, theCode):
        currentLine = 0

        for line in theCode:
            currentLine += 1

            if line.startswith("echo"):
                print(f"[{tags['script']}] "+str(self.getValueFromBrackets(line)))

            elif line.startswith("import"):
                where = self.getValueFromBrackets(line)

                if os.path.isfile(where+".honey"):
                    importedScript = Script(where+"honey")
                elif os.path.isfile(where):
                    importedScript = Script(where)
                elif self.isUrl(where):
                    importedScriptCode = str(requests.get(where).text).rstrip("\n").splitlines()
                    importedScript = Script(importedScriptCode)
                    
            elif functions.get(str(line).split("(")[0].rstrip("\n")):
                functionName = str(line).split("(")[0].rstrip("\n")

                for index, parametre in enumerate(str(line).split("(")[1].rstrip(")").split(", ")):
                    try:
                        variables[functions[functionName]["parametres"][index]] = self.checkValue(parametre)
                    except:
                        honeyError("no parametre of index "+str(index))

                self.runCode(functions[functionName]["lines"])

    def checkValue(self, what_):
        try:
            if str(what_).startswith('"'):
                return str(what_.lstrip('"').rstrip('"'))

            what_ = str(what_)

            if self.isNumberic(what_):
                return float(what_)
            elif variables.get(str(what_)):
                return variables[what_]
            elif "*" in str(what_) or "+" in str(what_) or "/" in str(what_) or "-" in str(what_):
                try:
                    newWhat = self.forVariables(what_)
                    return eval(str(newWhat))
                except:
                    pass
            elif self.isJson(what_):
                return json.loads(what_)
            elif functions.get(what_.split("(")[0]):
                print(what_.split("(")[0].rstrip("\n"))
                newnewWhat = what_.split("(")[0]
                if functions[newnewWhat]["return"] != None:
                    return functions[what_.split("(")[0]]["return"]
            else:
                return "nil"
        except Exception as err:
            honeyError(str(err))
                    
    def isNumberic(self, what):
        try:
            float(what)
            return True
        except:
            return False
    
    def isJson(self, what):
        try:
            json.loads(what)
            return True
        except:
            return False

    def isUrl(self, url):
        response = requests.get(str(url))
        try:
            _ = response.text
            return True
        except:
            return False


script = Script(readlines("script.honey"))
