
def return_normal(value):
    for i in str(value):
        if i == "0":
            continue
        else:
            return value[value.index(i):]
    return "0"

print(return_normal("0012"))