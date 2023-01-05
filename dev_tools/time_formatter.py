from time import strptime, mktime

print(mktime(strptime(input(), '%c')))