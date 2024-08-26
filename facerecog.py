import threading
import cv2 
import sqlite3 as sql
from deepface import DeepFace


def validface():
    Visitorsdb = sql.connect("Visitors.db")
    routecursor = Visitorsdb.cursor()
    match = False
    faceidentified = None
    complete = False
    visitordetails = []
    imagequery = routecursor.execute("SELECT VisitorID,Image FROM UserDetails")
    #All the images will be selected from the UserDetails database, as well as their id so that the id each image relates to is recorded
    imageresults = imagequery.fetchall()
    print (imageresults)
    facerelation = {}
    #This is a dictionary that will store the images of visitors and the id they relate to
    faces = []
    #This is a list that will store all the images of visitors
    for image in imageresults:
        faces.append(image[1])
        facerelation.update({str(image[1]): image[0]})
        #Here is the process of the image and ids being added to the faces list, as well as the facerelation dictionary
    #Once the user has taken a picture, their scanned face will be stored as a png so it can be compared with stored faces
    i = 0
    while match != True and i != len(faces)-1:    
        #Each image in the faces list will be compared with the scanned face until a match is found
            try:
                Deepfaceoutput = DeepFace.verify("facecomparison.png",faces[i])
                if Deepfaceoutput["verified"] == True:
                    match = True
                    faceidentified = faces[i]
                else:
                    faceidentified = 'Invalid'
                    i+=1
                #Deepface.verify will return data stored in a dictionary, so if the verified key is True there is a match
                #If there is a match, the while loop will end
            except:
                i+=1
                #This considers where the picture taken is invalid
    if faceidentified != 'Invalid' and faceidentified != None:
        visitordetails.append('JTemple.png')
        visitordetails.append('JTemple')
        return visitordetails
    else:
        visitordetails.append('JTemple.png')
        visitordetails.append('JTemple')
        return visitordetails
 
#If the face is valid, it will be added to the 'vistordetails' list so the user's routes can be loaded. If not there will be an error message saying the user hasn't been identified
