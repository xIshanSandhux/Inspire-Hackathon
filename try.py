import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext('test.jpeg')
for _, text, _ in result:
    print(f"{text} ")

result2 = reader.readtext('test2.jpeg')
for _, text, _ in result2:
    print(f"{text} ")


result3 = reader.readtext('test3.webp')
for _, text, _ in result3:
    print(f"{text} ")
