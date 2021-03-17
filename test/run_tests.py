# Batch running 

import subprocess

all_groups = ["10_2_2", "10_4_2", "10_6_2", "10_8_2", "10_10_2", "12_4_2", "14_4_2", "16_4_2", "18_4_2", "20_4_2"]

for group in all_groups:
    for i in range(1,11):
        subprocess.call(["python3 ../learn.py " + group + "/" + group + "-" + str(i) + ".json"],shell=True)
