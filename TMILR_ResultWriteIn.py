#本文件中主要包含对随机化结果的.s文件生成与改写的过程代码，收尾
#main函数开始后，进行标签写入操作，而后开启随机化执行开关开始随机化执行
from TMILR_Preprocess import *
from TMILR_Randomization import *
from TMILR_ResultWriteIn import *
#写入写入策略：在main函数开始时，开启标签写入模式，将随机化排步完成后的各个基本块标签写入，在每个函数进行打标签写入时，以函数起始名为
#基准
class TMILR_Result_Writer:
    def __init__(self,benchmarkName):
        self.randomizerPile = [TMILR_Randomizer]
        self.fileObj = open(benchmarkName+'_Result.s','w')
        #for block in self.randomizer.AfterRandomIns[1:]:
        #    for ins in block.content[1:]:
        #        self.fileObj.write(ins.insStr+'\n')
    def Receive_Randomized_Fun(self,randomizer:TMILR_Randomizer):
        self.randomizerPile.append(randomizer)
        return True

    def Tag_Assign(self,funName):#这个函数用于标签的分配指令，在遇到main函数之后进行
        return True

    def Actual_Ins_Write(self):#这个函数用于实际的随机化完成后的代码的写入
        return True

    def Do_The_Writing(self):

        for randomizer in self.randomizerPile[1:]:
            if 'main' in randomizer.funcName:#发现main函数，执行打印打标签操作的代码
                print('handle main')
                self.TMILR_Total_Init()
                for subRadomizer in self.randomizerPile[1:]:
                    self.Tag_Init_For_Nomal_Fun(subRadomizer)

                self.Turn_On_ILR_Mode()
                self.fileObj.write('\nILR_start:\n')
                self.Write_Normal_Fun(randomizer)

            else:#此处为其他函数
                self.Write_Normal_Fun(randomizer)

    def TMILR_Total_Init(self):
        self.fileObj.write('main:\n')
        self.fileObj.write('\tli\tx28, 0x000000000000ff00\n')
        self.fileObj.write('\tcsrw\tutagctrl, x28\n')
        self.fileObj.write('\tli\tx28, 0x00000000ff000000\n')
        self.fileObj.write('\tcsrs\tutagctrl, x28\n')
        self.fileObj.write('\tfence.i\n')
        return True
    def Write_Normal_Fun(self,randomizer:TMILR_Randomizer):
        for block in randomizer.AfterRandomIns[1:]:
            self.fileObj.write('\t\t\t\t#Next Block Offset:'+str(block.offset*2)+'\n')
            for ins in block.content[1:]:
                if ins.locationTag != "" and 'main' not in ins.locationTag:
                    self.fileObj.write(ins.locationTag+'\n')
                self.fileObj.write(ins.insStr+'\n')
    def Tag_Init_For_Nomal_Fun(self,randomizer:TMILR_Randomizer):
        if 'main' in randomizer.funcName:
            self.fileObj.write('\tla\tx28, ILR_start\n')
        else:
            self.fileObj.write('\tla\tx28, '+ randomizer.funcName+'\n')
        location = 0
        for block in randomizer.AfterRandomIns[1:]:
            if block.offset != 0:
                self.Tag_Init_For_Single_BLock(block,location)
            location += 8

    def Tag_Init_For_Single_BLock(self,block:BasicRandomBlock,loc):
        self.fileObj.write("\n\tli\tx30, "+block.offsetStr+'\n')
        self.fileObj.write("\tlw\tx29, "+str(loc)+'(x28)\n')
        self.fileObj.write("\ttagw\tx29, x30\n")
        self.fileObj.write("\tsw\tx29, "+str(loc)+'(x28)\n')

        return True

    def Turn_On_ILR_Mode(self):
        self.fileObj.write('\n\tli\tx28, 0x1\n')
        self.fileObj.write('\tslli\tx28,x28, 44\n')
        self.fileObj.write('\tcsrs\tutagctrl, x28\n')
        self.fileObj.write('\tli\tx28, 0x1\n')
        self.fileObj.write('\tslli\tx28,x28, 45\n')
        self.fileObj.write('\tcsrs\tutagctrl, x28\n')