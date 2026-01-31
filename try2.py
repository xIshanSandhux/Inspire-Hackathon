import cv2
import os
import easyocr
IMAGE_PATH = "testing.jpeg"
def cap_image():
    cap = cv2.VideoCapture(0)

    while True:
        ret,frame = cap.read()

        if not ret:
            break

        cv2.imshow("test",frame)

        key = cv2.waitKey(1)

        if key==27:
            cap.release()
            cv2.destroyAllWindows()
            exit()
        elif key == 32:
            g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(IMAGE_PATH,g)
            print("image captured")
            break

    cap.release()
    cv2.destroyAllWindows()

def ocr_stuff():
    reader = easyocr.Reader(['en'])
    result = reader.readtext(IMAGE_PATH)

    for _,text,_ in result:
        print(f"{text}")

if __name__=="__main__":
    cap_image()
    ocr_stuff()
    os.remove(IMAGE_PATH)


