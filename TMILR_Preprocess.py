#本文件中主要保存TMILR所要用到的预处理代码，包括汇编码的处理，汇编码与反汇编码的比较

class SingleAsmIns:#single Asemble instruction
    insStr = ""
    opCode = ""
    insType = ""
    branchOrNot = bool
    branchTarget = ""
    rd = ""
    rs1 = ""
    rs2 = ""
    imm = ""
    rStr = ""
    lineNum = 0
    correspondDumpInsNum = 0
    correspondBC = []   #correspond binary code line in the dump file
    locationTag = ""
    def __init__(self,lineStr:str,lineNum:int):
        self.branchOrNot = False
        self.correspondBC = []
        self.correspondDumpInsNum = 0
        self.lineNum = lineNum
        self.insStr = lineStr
        #print("ins:",lineStr)
        if len(lineStr.split("\t"))==2:
            self.opCode = lineStr.split("\t")[1]
            #print(lineStr.split("\t")[1])
        elif len(lineStr.split("\t")) == 3:
            self.opCode = lineStr.split("\t")[1]
            self.rStr = lineStr.split("\t")[-1]
            #print(self.rStr)
        else:
            print("non rec ins!\n\n")
        #print(lineStr.split("\t")[-1])
        op = self.opCode
        if op=="j" or op=="beq" or op=="bne" or op=="blt"or op=="bge" or op=="bltu" or op=="ble" or op=="bgt" \
        or op=="bgeu":
            #self.PrintMyself()
            self.branchOrNot = True
            self.branchTarget = lineStr.split("\t")[-1].split(",")[-1]
            #print(self.branchTarget)
        if len(self.rStr.split(",")) == 1:
            self.imm = self.rStr
            #print(self.opCode.split(" "))
        elif len(self.rStr.split(",")) == 2:
            (self.rd, self.imm )= self.rStr.split(",")
        elif len(self.rStr.split(",")) == 3:
            (self.rd , self.rs1, self.imm) = self.rStr.split(",")
        elif len(self.rStr.split(",")) == 4:
            (self.rd, self.rs1, self.rs2, self.imm) = self.rStr.split(",")
        else:
            print("ERROR, non rec ins")
        #self.PrintMyself()
    def PrintMyself(self):
        print("\t",self.opCode,"\t",self.rd,self.rs1,self.rs2,self.imm)
        if len(self.correspondBC)>1:
            print("this ins has more dumpins")
            for ins in self.correspondBC:
                ins.PrintMyself()

class LocationTag:
    tagStr = ""
    pointAdd = 0x0
    lineNum = 0
    funHeadOrNot = bool
    def __init__(self,lineNum:int,lineStr:str):
        self.tagStr = lineStr
        self.pointAdd = lineNum + 1
        self.lineNum = lineNum
        self.funHeadOrNot = False
    def PrintMyself(self):
        print(self.tagStr)

#class AuxLines:#表示一段连续的不属于代码的数据，可以是数据段，也可以是表示代码段信息的数据，和每个函数在一起分布
    #auxID = 0 #表示是第几段辅助数据，辅助数据被代码段隔开并按照隔开进行分配序号
    #startLineNum = 0
    #endLineNum = 0
    #lines = []
    #def __init__(self):

class singleAsmFunction:
    asmFunctionName = ""
    asmFunctionLenth = 0
    asmFunctionStartLineNum = 0
    asmFunctionEndLineNum = 0
    asmFunctionIns = []
    asmInsNumber = 0
    def __init__(self,name:str,startNum:int):
        self.asmFunctionName = name.split("\t")[1]
        self.asmFunctionStartLineNum = startNum
        self.asmFunctionIns.clear()
        self.asmFunctionIns = []
        self.asmInsNumber = 0
        print("function init:",name," ",self.asmFunctionStartLineNum)
    def AddIns(self,ins):
        self.asmFunctionIns.append(ins)
    def EndFunction(self,endNum):
        self.asmFunctionEndLineNum = endNum
        print("function end:",self.asmFunctionEndLineNum)
    def GetIns(self,rawCodeTable:[]):
        self.asmFunctionIns.clear()
        for lineNum in range(self.asmFunctionStartLineNum+1,self.asmFunctionEndLineNum):
            if ":" in rawCodeTable[lineNum]:
                currentLocTag = LocationTag(lineNum,rawCodeTable[lineNum])
                self.asmFunctionIns.append(currentLocTag)
            else:
                currentAsmIns = SingleAsmIns(rawCodeTable[lineNum],lineNum)
                self.asmFunctionIns.append(currentAsmIns)
                self.asmInsNumber += 1
        for insNum in range(len(self.asmFunctionIns)):
            if type(self.asmFunctionIns[insNum]) == LocationTag:
                if self.asmFunctionName in self.asmFunctionIns[insNum].tagStr:#is a function start point
                    #print("funhead",self.asmFunctionName)
                    self.asmFunctionIns[insNum].funHeadOrNot = True
                self.asmFunctionIns[insNum+1].locationTag = self.asmFunctionIns[insNum].tagStr

    def PrintMyself(self):
        print("\nNow Print:", self.asmFunctionName," insnumber = ",self.asmInsNumber)
        print("Function starts at: ", self.asmFunctionStartLineNum)
        print("Function ends at: ", self.asmFunctionEndLineNum)
        for Ins in self.asmFunctionIns:
            Ins.PrintMyself()

class SingleDumpFunction:
    dumpFunctionName = ""
    dumpFunctionLenth = 0
    dumpFunctionStartAdd = 0
    dumpFunctionEndAdd = 0
    dumpFunctionStartNum = 0
    dumpFunctionEndNum = 0
    dumpFunctionIns = []
    dumpInsNumber = 0
    def __init__(self , startNumber , lineStr:str , rawDumpTable:[]):
        self.dumpFunctionName = lineStr.split("<")[1].split(">")[0]
        print("Initial a fun in dump:", lineStr,self.dumpFunctionName)
        self.dumpFunctionStartNum = startNumber
        self.dumpFunctionStartAdd = int(lineStr.split("00000000")[1].split(" <")[0],16)
        #print("%x"%self.dumpFunctionStartAdd)
        self.dumpFunctionIns = []
        self.dumpInsNumber = 0
        currentLineNum = startNumber + 1
        while rawDumpTable[currentLineNum] != "":
            currentIns = SingleDumpIns(rawDumpTable[currentLineNum])
            self.dumpFunctionIns.append(currentIns)
            #currentIns.PrintMyself()
            currentLineNum += 1
            self.dumpInsNumber += 1

    def EndFunction(self,endNum,endAdd):
        self.dumpFunctionEndAdd = endAdd
        self.dumpFunctionEndNum = endNum
    def PrintMyself(self):
        print("NOW PRINT:", self.dumpFunctionName,"insnum=",self.dumpInsNumber)
        for ins in self.dumpFunctionIns:
            ins.PrintMyself()

class SingleDumpIns:
    binaryCode = ""
    disasmCode = ""
    address = 0x0
    annotation = ""
    insType = ""
    opCode = ""
    rStr = "" #str that dispart opcode
    rd = ""
    rs1 = ""
    rs2 = ""
    imm = ""
    scaned = False
    branchTarget = 0x0
    def __init__(self,lineStr:str):
        self.disasmCode = ""
        self.annotation = ""
        self.address = 0
        self.binaryCode = ""
        self.scaned = False
        addStr = lineStr.rstrip().split(":")[0].split("    ")[1]
        self.address = int(addStr, 16)
        if "<" not in lineStr and "#" not in lineStr:
            asmStr = lineStr.rstrip().split(" ")[-1]
        elif "#" in lineStr:
            asmStr = lineStr.rstrip().split(" # ")[0].split(" ")[-1]
            self.annotation = lineStr.rstrip().split(" # ")[1]
            #print(self.annotation)
            #print(asmStr)
        if "<" in lineStr and "#" not in lineStr:
            #print(lineStr.rstrip().split(" "))
            asmStr = lineStr.rstrip().split(" ")[-2]
            self.annotation = lineStr.rstrip().split(" ")[-1]
            #print(asmStr)
        self.disasmCode = asmStr
        self.binaryCode = lineStr.rstrip().split(" ")[4].split("\t")[1]
        #print(self.binaryCode)
        #print(lineStr.split("\t"))
        #print(self.disasmCode.split("\t"))
        self.opCode = self.disasmCode.split("\t")[1]
        if len(self.disasmCode.split("\t"))== 2:
            self.imm=""
        else:
            self.rStr = self.disasmCode.split('\t')[-1]
            if len(self.rStr.split(","))==1:
                self.imm = self.rStr
            elif len(self.rStr.split(","))==2:
                (self.rd,self.imm) = self.rStr.split(',')
            elif len(self.rStr.split(","))==3:
                (self.rd,self.rs1,self.imm) = self.rStr.split(',')
            elif len(self.rStr.split(",")) == 4:
                (self.rd, self.rs1, self.rs2,self.imm) = self.rStr.split(',')
            else:
                print("ERROR NON REC")

        #print("0x%x"%self.address)
    def PrintMyself(self):
        if self.annotation!="":
            print("0x%x"%self.address," ",self.binaryCode," ",self.opCode," ",self.rd,self.rs1,self.rs2,self.imm," # ",self.annotation)
        else:
            print("0x%x" % self.address, " ", self.binaryCode, " ", self.opCode," ", self.rd, self.rs1, self.rs2, self.imm)

def AsmFilter(rawAsmCode:[]):
    asmFilterResult = []
    for lineNum in range(len(rawAsmCode)):
        if "@function" in rawAsmCode[lineNum] and ".type" in rawAsmCode[lineNum]:
            funStartNum = lineNum
            functionName = rawAsmCode[lineNum].split(".type")[1].split("@function")[0].split(",")[0]
            currentFun = singleAsmFunction(functionName,funStartNum)
        if ".size" in rawAsmCode[lineNum] and functionName in rawAsmCode[lineNum]:
            funEndNum = lineNum
            currentFun.EndFunction(funEndNum)
            asmFilterResult.append(currentFun)
    for fun in asmFilterResult:
        fun.GetIns(rawAsmCode)
        #fun.PrintMyself()
    return asmFilterResult

def DumpFilter(rawDumpCode:[],filterAsmCode:[]):#handle the elf dumpcode find every function
    dumpFilterResult = []
    for lineNum in range(len(rawDumpCode)):
        #if rawDumpCode[lineNum] == "":
        if "00000000400" in rawDumpCode[lineNum] and "<" in rawDumpCode[lineNum]:
            funName = rawDumpCode[lineNum].split("<")[1].split(">")[0]

            for fun in filterAsmCode:
                if funName in fun.asmFunctionName:
                    print("found a ",funName)
                    currentFunInDump = SingleDumpFunction(lineNum,rawDumpCode[lineNum],rawDumpCode)
                    dumpFilterResult.append(currentFunInDump)
        #print(rawDumpCode[lineNum])
        #if " 4000" in rawDumpCode[lineNum]:
            #currentIns = SingleDumpIns(rawDumpCode[lineNum])
            #dumpFilterResult.append(currentIns)
            #print(rawDumpCode[lineNum])
    #for dumpFun in dumpFilterResult:
    #    dumpFun.PrintMyself()
    return dumpFilterResult
def AsmDumpFileAnalysis(AsmCode:[], DumpCode: []):
    for asmfun in AsmCode:
        #print('now handle ',asmfun.asmFunctionName)
        for dumpFun in DumpCode:
            if dumpFun.dumpFunctionName == asmfun.asmFunctionName:
                currentDumpFun = dumpFun
                break
        #if currentDumpFun.dumpInsNumber = asmfun.asmInsNumber:

        #print('found the fun', currentDumpFun.dumpFunctionName)
        for asmInsNum in range(len(asmfun.asmFunctionIns)):#开始扫描当前汇编函数中的每一条指令
            currentAsmIns = asmfun.asmFunctionIns[asmInsNum]
            currentAsmInsNum = asmInsNum
            if type(currentAsmIns) == SingleAsmIns:#是一条指令　才开始分析
                #print('found a ins')
                #currentAsmIns.PrintMyself()
                currentDumpIns = currentDumpFun.dumpFunctionIns[0]#在机器码中取第一条
                if CompareAsmInsAndDumpIns(currentAsmIns,currentDumpIns):
                    #print('match:',asmInsNum)
                    #currentAsmIns.PrintMyself()
                    asmfun.asmFunctionIns[currentAsmInsNum].correspondBC.append(currentDumpIns)
                    del currentDumpFun.dumpFunctionIns[0]
                else:#可能出现误判，这种情况下如果两者的第一后继符合，则判定本条符合
                    asmfun.asmFunctionIns[currentAsmInsNum].correspondBC.append(currentDumpIns)
                    del currentDumpFun.dumpFunctionIns[0]
                    if len(currentDumpFun.dumpFunctionIns) > 0:
                        nextDumpIns = currentDumpFun.dumpFunctionIns[0]
                    if  currentAsmInsNum < len(asmfun.asmFunctionIns):
                        nextAsmInsNum = currentAsmInsNum + 1
                        nextAsmIns = asmfun.asmFunctionIns[nextAsmInsNum]
                        while(type(nextAsmIns)==LocationTag):
                            nextAsmInsNum += 1
                            nextAsmIns = asmfun.asmFunctionIns[nextAsmInsNum]
                    while(CompareAsmInsAndDumpIns(nextAsmIns,nextDumpIns)==False):
                        asmfun.asmFunctionIns[currentAsmInsNum].correspondBC.append(nextDumpIns)
                        del currentDumpFun.dumpFunctionIns[0]
                        if len(currentDumpFun.dumpFunctionIns) > 0:
                            nextDumpIns = currentDumpFun.dumpFunctionIns[0]
                        else:
                            print("error!")
                    #currentAsmIns.PrintMyself()
            else:
                #print('found a tag\n')
                continue
        #print("fff",asmfun.asmFunctionName)
        #for asmNum in range(len(asmfun.asmFunctionIns)):
        #asmfun.PrintMyself()
    return 0
def CompareAsmInsAndDumpIns(asmins:SingleAsmIns,dumpins:SingleDumpIns):#用于判断两条指令是否是对应的
    if dumpins.opCode != "li" and dumpins.opCode!='auipc' and "i" in dumpins.opCode:
        #localDumpopCode = ''.join(dumpins.opCode.split('i'))
        dumpins.opCode = ''.join(dumpins.opCode.split('i'))
        #print(dumpins.opCode)
        #print(dumpins.opCode)
    if asmins.opCode in dumpins.opCode \
        and dumpins.rd == asmins.rd \
        and dumpins.rs1 == asmins.rs1 \
        and dumpins.rs2 == asmins.rs2:
        return True
    if (dumpins.opCode=='jal' or dumpins.opCode=='jalr') and asmins.opCode == 'call':
        return True
    else:
        #print("not match",asmins.lineNum)
        #asmins.PrintMyself()
        return False

