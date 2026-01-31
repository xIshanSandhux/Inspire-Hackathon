import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext('test.jpeg')
for _, text, _ in result:
    print(f"{text} ")
