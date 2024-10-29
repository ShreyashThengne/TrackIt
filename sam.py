c = r"."
import os
# for (root,dirs,files) in os.walk('.', topdown=True):
#     print (root)
#     print (dirs)
#     print (files)
#     print("\n\n\n")
for i in os.scandir('.'):
    print(type(i))