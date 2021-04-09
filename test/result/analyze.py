import statistics
import json
import matplotlib.pyplot as plt

all_groups = ["20_", "40_", "60_", "80_", "100_", "150_"]

avg_location_num_list = []
min_mq_list = []
avg_mq_list = []
max_mq_list = []
min_eq_list = []
avg_eq_list = []
max_eq_list = []
for group in all_groups:
    file_name = group + "rational_result.txt"
    with open(file_name, 'r') as f:
        lines = f.readlines()
        run_times = []
        locations_num = []
        S_num = []
        R_num = []
        E_num = []
        table_num = []
        mq_num = []
        eq_num = []
        for line in lines:
            line_contents = line.split(" ")
            run_times.append(float(line_contents[1]))
            locations_num.append(int(line_contents[2]))
            S_num.append(int(line_contents[2]))
            R_num.append(int(line_contents[3]))
            E_num.append(int(line_contents[4])+1)
            table_num.append(int(line_contents[5]))
            mq_num.append(int(line_contents[6]))
            eq_num.append(int(line_contents[7]))
        avg_run_time = statistics.mean(run_times)
        avg_location_num = statistics.mean(locations_num)
        avg_location_num_list.append(avg_location_num)
        avg_S_num = statistics.mean(S_num)
        avg_R_num = statistics.mean(R_num)
        avg_E_num = statistics.mean(E_num)
        avg_table_num = statistics.mean(table_num)
        avg_mq_num = statistics.mean(mq_num)
        avg_eq_num = statistics.mean(eq_num)
        print("**********************************************************")
        print("Group " + group + " results: (Min, Mean, Max)")
        print("run_time:", min(run_times), avg_run_time, max(run_times))
        print("location_num:", min(locations_num), avg_location_num, max(locations_num))
        print("S_num:", min(S_num), avg_S_num, max(S_num))
        print("R_num:", min(R_num), avg_R_num, max(R_num))
        print("E_num:", min(E_num), avg_E_num, max(E_num))
        print("table_num:", min(table_num), avg_table_num, max(table_num))
        print("mq_num:", min(mq_num), avg_mq_num, max(mq_num))
        min_mq_list.append(min(mq_num))
        avg_mq_list.append(avg_mq_num)
        max_mq_list.append(max(mq_num))
        print("eq_num:", min(eq_num), avg_eq_num, max(eq_num))
        min_eq_list.append(min(eq_num))
        avg_eq_list.append(avg_eq_num)
        max_eq_list.append(max(eq_num))
        print("**********************************************************")


# for group in all_groups:
#     tran_num = []
#     for i in range(1,11):
#         jsonfile = group + "/" + group + "-" + str(i) + ".json"
#         with open(jsonfile,'r') as f:
#             data = json.load(f)
#             trans_set = data["tran"]
#             tran_num.append(len(trans_set))
#     print("Group " + group + " tran_num (Min, Mean, Max):", min(tran_num), statistics.mean(tran_num), max(tran_num))

with open("../../../rational_result.txt", 'w') as f:
    f.write("".join([str(n) + " " for n in avg_location_num_list]+["\n"]))
    f.write("".join([str(n) + " " for n in min_mq_list]+["\n"]))
    f.write("".join([str(n) + " " for n in avg_mq_list]+["\n"]))
    f.write("".join([str(n) + " " for n in max_mq_list]+["\n"]))
    f.write("\n")
