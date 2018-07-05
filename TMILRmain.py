from TMILR_Preprocess import *
from TMILR_Randomization import *
from TMILR_ResultWriteIn import *
AsmFile = open("../median_main.s", "r")

rawAsmCode = []
for line in AsmFile:
    rawAsmCode.append(line.rstrip())
print(len(rawAsmCode))
DumpFile = open("../median.riscv.dump", "r")
rawDumpCodes = []
for line in DumpFile:
    rawDumpCodes.append(line.rstrip())
refinedAsmCode = AsmFilter(rawAsmCode)
refinedDumpCode = DumpFilter(rawDumpCodes,refinedAsmCode)
AsmDumpFileAnalysis(refinedAsmCode,refinedDumpCode)

s = "4000000"
n = int(s,16)
n += 0x15
print("%x"%n)
#总体设计思路：
#对编译和反汇编的文件进行处理，识别汇编码和机器码多对一的问题，
#对汇编码进行随机化排步
#计算偏移量
#插入运行时写入偏移量的代码
#生成处理完成的汇编码