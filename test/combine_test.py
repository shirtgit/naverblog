list1 = [["송파동", "설비업체"], ["방이동", ""], ["", ""]]
list2 = [["송파동", "설비업체"], ["방이동", "건설업체"], ["금천동", ""], ["", ""]]

result = []

for i in range(0, len(list1)):
    if list1[i][0] == "":
        break
    for j in range(0, len(list1)):
        if list1[j][1] == "":
            continue
        result.append([list1[i][0], list1[j][1]])

print(result)
result.clear()

for i in range(0, len(list2)):
    if list2[i][0] == "":
        break
    for j in range(0, len(list2)):
        if list2[j][1] == "":
            continue
        result.append([list2[i][0], list2[j][1]])

print(result)
