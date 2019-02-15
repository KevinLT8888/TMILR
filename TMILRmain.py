from TMILR_Preprocess import *
from TMILR_Randomization import *
from TMILR_ResultWriteIn import *
import  copy
testName = 'multiply'
AsmFile = open("multiply_main.s", "r")
randomwindow = 16
randomgrain = 2 #指令进行随机化排步的粒度
rawAsmCode = []
for line in AsmFile:
    rawAsmCode.append(line.rstrip())
print(len(rawAsmCode))
DumpFile = open("multiply.riscv.dump", "r")
rawDumpCodes = []
for line in DumpFile:
    rawDumpCodes.append(line.rstrip())
refinedAsmCode = AsmFilter(rawAsmCode)

refinedDumpCode = DumpFilter(rawDumpCodes,refinedAsmCode)

AsmDumpFileAnalysis(refinedAsmCode,refinedDumpCode)
consultAsmCode = copy.deepcopy(refinedAsmCode)
ResultWriter = TMILR_Result_Writer(testName)
for fun in refinedAsmCode:
    Randomizer = TMILR_Randomizer(fun,randomwindow,randomgrain)#新建一个针对当前函数的随机器
    Randomizer.PrintMyself()
    target = open("targetfile",'w')
    print("\n Now do the randomization\n\n")
    Randomizer.Do_The_Randomization(randomgrain)
    Randomizer.Caculate_Offsets()
    ResultWriter.Receive_Randomized_Fun(Randomizer)#将随机化排步完成后的函数送到结果打印器中．
ResultWriter.Do_The_Writing()
#refinedAsmCode[0].PrintMyself()
#consultAsmCode[0].PrintMyself()
#总体设计思路：
#对编译和反汇编的文件进行处理，识别汇编码和机器码多对一的问题，
#对汇编码进行随机化排步
#计算偏移量
#插入运行时写入偏移量的代码
#生成处理完成的汇编码