import time


ssid = 'MRL-Guest'

test_list = [(1, '70:18:a7:14:cd:c0', 'eq-secure'),
             (2, '70:18:a7:14:cd:c1', 'eq-apple'),
             (3, '70:18:a7:14:cd:c2', 'MRL-Guest'),
             (4, '70:18:a7:14:cd:c3', 'MRL-RnD')]

for item in test_list:
     if item[2] == ssid:
          print(f'AP id: {item[0]}\nAP MAC: {item[1]}\nAP Name: {item[2]}')

print(test_list[3][1])

if ssid in test_list:
    print('Yes')


