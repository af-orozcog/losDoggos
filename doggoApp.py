# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart  # New line
from email.mime.base import MIMEBase  # New line
from email import encoders  # New line
from imutils.video import VideoStream
from cv2 import *
import argparse
import datetime
import imutils
import time
import random
import platform
import winsound
import subprocess
import time

possible_names = ["Gordo.wav", "Juguete.wav", "Pisadas.wav", "Puerta.wav", "Rocky.wav", "Timbre.wav",
                  "service-bell_daniel_simion.wav"]



def sendmail(lista, tiempos):
    sender_email = 'goricrates@gmail.com'
    reciever_email = 'd.galindo@uniandes.edu.co'
    password = 'Chicago2019'
    msg = MIMEMultipart()
    msg['To'] = formataddr(('Daniel G', reciever_email))
    msg['From'] = formataddr(('Daniel G', sender_email))
    msg['Subject'] = 'Hello, my friend Daniel'
    print("Enviando correo...")
    mensaje = 'Su mascota intentó entrar - me re cago en la vida :v'
    mensaje += "\nintento entrar : " + str(len(tiempos)) + " veces\npara cada vez que visito la zona prohibida estuvo:\n"
    for i in range(0,len(tiempos)):
        mensaje += str(i+1) + " : " + str(tiempos[i])+" minutos\n"
    mensaje += "wtf is happening"
    print(mensaje)
    msg_content = MIMEText(mensaje, 'plain', 'utf-8')
    msg.attach(msg_content)
    #filename = nombres_fotos[len(nombres_fotos)-1]
    try:
        for filename in lista:
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header("Content-Disposition", f"attachment; filename= {filename}", )
                msg.attach(part)

    except Exception as e:
        print(f'No se encontro el archivo n{e}')
    try:
        # Creating a SMTP session | use 587 with TLS, 465 SSL and 25
        server = smtplib.SMTP('smtp.gmail.com', 587)
        # Encrypts the email
        context = ssl.create_default_context()
        server.starttls(context=context)
        # We log in into our Google account
        server.login(sender_email, password)
        # Sending email from sender, to receiver with the email body
        server.sendmail(sender_email, reciever_email, msg.as_string())
        print('Email sent!')
    except Exception as e:
        print(f'Error en correo {e}')
    finally:
        print('Cerrando el servidor...')



# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

# otherwise, we are reading from a video file
else:
    vs = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

ids = 0
millis = None
nombres_fotos = []
tiempos = []
oc = False
inside = False
# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = vs.read()
    frame = frame if args.get("video", None) is None else frame[1]
    text = "Unoccupied"
    oc = False
    actual = int(round(time.time() * 1000))
    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if frame is None:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"
        oc = True
        actual = int(round(time.time() * 1000))
        if (inside == False):
            currentDT = datetime.datetime.now()
            name = "taken" + str(currentDT.year) + str(currentDT.month) + str(currentDT.day) + str(
                currentDT.hour) + str(
                currentDT.minute) + ".jpg"
            cv2.imwrite(name, frame)
            nombres_fotos.append(name)
            millis = actual
            inside = True

        if (platform.system() == 'Windows'):
            pass
            # print("wtf is happening")
            # winsound.PlaySound(random.choice(possible_names),winsound.SND_ASYNC)
        elif (platform.system() == 'Linux'):
            subprocess.call(["aplay", random.choice(possible_names)])
        else:
            subprocess.call(["afplay", random.choice(possible_names)])

    actual = int(round(time.time() * 1000))
    if(oc == False and inside == True):
        tiempos.append((actual-millis)/6000)
        inside = False

    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

sendmail(nombres_fotos,tiempos)
# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
