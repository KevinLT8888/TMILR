#本文件中主要写TMILR的随机化算法,以每个函数为单位，将代码按照两条为一组分块其中要考虑一对多的情况
from TMILR_Preprocess import *
class BasicRandomBlock:
    #这个类表示参与随机化的一个基本块，内部的指令顺序执行是不变的
    def __init__(self,absLoc,blocksize):
        self.loc = absLoc#这个变量表示该基本随机块基于本函数所在的绝对位置，用于随后的偏移量计算
        self.size = blocksize#表示本块的大小，以机器码指令个数为准
        self.asmInsNum = 0 #这个变量表示汇编指令个数,可能小于基本块大小
        self.content = [SingleAsmIns]
        self.offset = 0 #表示本基本块与下一个基本块在随机化完成后的偏移量，用于后续的指令重写
    def InputIns(self,ins:SingleAsmIns):
        self.content.append(ins)
        self.asmInsNum += 1
    def Progress_Tag(self):
        #这个函数用于处理自身的标签，使之变成能够打印的版本
        if self.offset>0:
            self.offsetStr = str(hex(self.offset*2))
        elif self.offset < 0 :
            self.offsetStr = hex(self.offset*2+ 0xff + 0x1)
        elif self.offset == 0:
            self.offsetStr = '0'
        #print(self.offsetStr)
        return True

    def PrintMyself(self):
        print(': loc %d'%self.loc,"\t\t",self.offset)
        for ins in self.content[1:]:
            ins.PrintMyself()
    def Write_Result(self,fileObj,functionName:str):
        for ins in self.content[1:]:
            fileObj.write(ins.insStr)

import random
import copy
class RandomBasket:
    #这个类是用于进行随机化排步的篮子，向其中投入基本随机块
    def __init__(self,busketsize):
        self.size = busketsize #这个变量表示随机篮的大小
        self.content = [BasicRandomBlock]
    def InputaBlock(self,block:BasicRandomBlock):
        #print("Receive a block:")
        #block.PringMyself()
        self.content.append(block)
        #self.content[-1].PringMyself()
        return len(self.content)
    def Shuffle(self):
        print("\nBlocks in this busket:",len(self.content)-1)
        for block in self.content[1:]:
            block.PrintMyself()
        print('Print Done\n')
        result = [BasicRandomBlock]
        while len(self.content) > 1:
            randomNum = random.randint(1,len(self.content)-1)
            #self.content[randomNum].PringMyself()
            result.append(self.content[randomNum])
            del self.content[randomNum]
        #print("Random done\n")
        return result
    def Clear(self):
        self.content = [BasicRandomBlock]
    def PrintMyself(self):
        for block in self.content[1:]:
            block.PringMyself()

class TMILR_Randomizer:
    #以单个函数为单位进行随机化排步，最后输出一个随机化排步之后的函数,在建立之后会对传入的函数复制一个缓存，并针对缓存进行操作，输出随机化后的该函数
    randomWindowVal = 0
    PreRandomIns   = [SingleAsmIns]
    AfterRandomIns = [BasicRandomBlock]

    randomgrain = int

    def __init__(self,targetfun:singleAsmFunction,windowval,randomgrain):
        print('\nNow malloc the target fun:',targetfun.asmFunctionName)
        self.randomWindowVal = windowval
        self.randomgrain = randomgrain
        self.PreRandomIns = [SingleAsmIns]
        self.AfterRandomIns = [BasicRandomBlock]#这个列表保存随机化完成之后的指令基本块
        self.funcName = targetfun.asmFunctionName
        for targetins in targetfun.asmFunctionIns:
            if type(targetins) == SingleAsmIns:
                #targetins.PrintMyself()
                #newins = SingleAsmIns()
                newins = SingleAsmIns(targetins.insStr,targetins.lineNum)
                newins.correspondBC = targetins.correspondBC
                newins.locationTag = targetins.locationTag
                newins.correspondDumpInsNum = len(newins.correspondBC)
                newins.PrintMyself = targetins.PrintMyself
                self.PreRandomIns.append(newins)

    def PrintMyself(self):
        for ins in self.PreRandomIns:
            if ins.locationTag != '':
                print(ins.locationTag)
            print("\t", ins.opCode, "\t", ins.rd, ins.rs1, ins.rs2, ins.imm)
            if len(ins.correspondBC) > 1:
                print("this ins has more dumpins")
                for dumpins in ins.correspondBC:
                    dumpins.PrintMyself()

    def Do_The_Randomization(self,randomGrain):
        #进行随机化的主函数，主要思想是建立一个大小可设定的随机缓存，在这个缓存中进行随机化排步，而后返回

        #randomGrain表示多少条指令粒度的随机化排步
        #先对第一条指令进行规约，如果下一条指令有两条对应机器码，则添加一条空指令占位．
        abs_loc = 0 #这个变量表示在当前函数内的各个指令在机器码中的在本函数体内的绝对位置，用于计算随机化后的偏移量
        randomBasket = RandomBasket(8)
        currentBBlock = BasicRandomBlock(abs_loc,2)#现在构造第一个基本随机块，第一个不参与随机化
        #currentBBlock.InputIns(self.PreRandomIns[1])
        if self.PreRandomIns[1].correspondDumpInsNum ==1:
            currentBBlock.InputIns(self.PreRandomIns[1])
            del self.PreRandomIns[1]
            if self.PreRandomIns[1].correspondDumpInsNum >1 or 'call' in self.PreRandomIns[1].insStr:
            #针对第一条指令来说，如果后面的指令对应机器码长度大于１，则用空指令占位当前基本随机块
                NOP_ins = SingleAsmIns("\tnop",self.PreRandomIns[1].lineNum)
                currentBBlock.InputIns(NOP_ins)
            #print(self.PreRandomIns[1].originalLocation)
            else:#两条指令的机器指令数都是１，则将两条指令插进当前随机基本块
                currentBBlock.InputIns(self.PreRandomIns[1])
                del self.PreRandomIns[1]
        elif self.PreRandomIns[1].correspondDumpInsNum ==2:#本条指令就有２条对应机器指令，因此直接用此构造基本块
            currentBBlock.InputIns(self.PreRandomIns[1])
            del self.PreRandomIns[1]
        elif self.PreRandomIns[1].correspondDumpInsNum > 2 :#多于２条对应机器指令，需要特别处理
            print("ERROR!!!\n\n")
            return False

        #第一个基本块构造完成，将其插入结束指令列表
        self.AfterRandomIns.append(currentBBlock)
        abs_loc += 2
        #currentBBlock.PringMyself()
        #开始构造后续的基本块
        blockNum = 0
        busketsize = 0
        randomResult = [BasicRandomBlock]
        while len(self.PreRandomIns)> 2:
            while busketsize < 9 and len(self.PreRandomIns)> 2:
                #当随机篮没满的时候，不断构造基本随机块投入随机篮
                currentBBlock = BasicRandomBlock(abs_loc, 2)
                if self.PreRandomIns[1].correspondDumpInsNum == 1:
                    currentBBlock.InputIns(self.PreRandomIns[1])
                    abs_loc += 1
                    del self.PreRandomIns[1]
                    if self.PreRandomIns[1].correspondDumpInsNum == 1 \
                            and 'call' not in self.PreRandomIns[1].insStr:
                        currentBBlock.InputIns(self.PreRandomIns[1])
                        abs_loc += 1
                        del self.PreRandomIns[1]
                    elif self.PreRandomIns[1].correspondDumpInsNum > 1 or 'call' in self.PreRandomIns[1].insStr:
                        NOP_ins = SingleAsmIns("\tnop", self.PreRandomIns[1].lineNum)
                        currentBBlock.InputIns(NOP_ins)
                        abs_loc += 1
                elif self.PreRandomIns[1].correspondDumpInsNum == 2:
                    currentBBlock.InputIns(self.PreRandomIns[1])
                    del self.PreRandomIns[1]
                    abs_loc += 2
                else:
                    print('large asm_ins!!\n\n')
                #currentBBlock.PringMyself()
                busketsize = randomBasket.InputaBlock(currentBBlock)
                #print(busketsize)
                #print(len(self.PreRandomIns))
            randomResult = randomBasket.Shuffle()
            randomBasket.Clear()
            busketsize = 0
            for block in randomResult[1:]:
                #block.PringMyself()
                self.AfterRandomIns.append(block)
        afternum = 0
        #print('AFTER:\n\n')
        #for block in self.AfterRandomIns[1:]:
        #    print('block',block.content.__len__(),block.loc)
        #    afternum += block.content.__len__()-1
        #    block.PringMyself()
        print('LAST:')
        #收尾工作，继续将这些指令写进一个基本块内
        currentBBlock = BasicRandomBlock(abs_loc, 2)
        if self.PreRandomIns[1].correspondDumpInsNum == 1:
            currentBBlock.InputIns(self.PreRandomIns[1])

            NOP_ins = SingleAsmIns("\tnop", self.PreRandomIns[1].lineNum)
            currentBBlock.InputIns(NOP_ins)
            del self.PreRandomIns[1]

        elif self.PreRandomIns[1].correspondDumpInsNum == 2:
            currentBBlock.InputIns(self.PreRandomIns[1])
            del self.PreRandomIns[1]
        self.AfterRandomIns.append(currentBBlock)
        if len(self.PreRandomIns) == 1:
            print("Randomization Done!\n")
        #for block in self.AfterRandomIns[1:]:
            #block.PrintMyself()
    def Caculate_Offsets(self):
        for num in range(1,len(self.AfterRandomIns)):
            #print(num,self.AfterRandomIns[num].loc)
            nextNum = 1
            while self.AfterRandomIns[nextNum].loc != self.AfterRandomIns[num].loc + 2:
                nextNum += 1
                if nextNum == len(self.AfterRandomIns):
                    break
                #print(nextNum)
            self.AfterRandomIns[num].offset = nextNum - num - 1
            #print(self.AfterRandomIns[num].loc,self.AfterRandomIns[nextNum].loc)
        print("\nDone\n")
        for num in range(1, len(self.AfterRandomIns)):
            #print(num, self.AfterRandomIns[num].loc,self.AfterRandomIns[num].offset)
            #print("%s"%bin(self.AfterRandomIns[num].offset))
            self.AfterRandomIns[num].Progress_Tag()
        return True






