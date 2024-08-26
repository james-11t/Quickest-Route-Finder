import sqlite3 as sql
#Importing an SQL library to allow me to create databases using python
from deepface import DeepFace
import facerecog
#This is a library I have imported to allow me to perform facial recognition
import datetime as dt
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDRaisedButton, MDIconButton
#will allow the user to interact with buttons on the screen
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.properties import ObjectProperty
#Will load the kv file to allow me to customise the application
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivy.uix.camera import Camera
import sys
sourcenode = ''
destinationnode = ''
global referencedate
referencedate = dt.datetime(2000,5,12)
#Date that will be used to determine the order of dates the routes where accessed


class WindowManager(ScreenManager):
    pass

class VisitorTypeScreen(Screen):
    Routesdb = sql.connect("Routes.db")
    routecursor = Routesdb.cursor()
    routecursor.execute("CREATE TABLE IF NOT EXISTS VisitorRoutes (VisitorID TEXT, RouteID INTEGER PRIMARY KEY, StartingPoint TEXT, DestinationPoint TEXT, Date TEXT, Days INTEGER NOT NULL)")
    Visitorsdb = sql.connect("Visitors.db")
    visitorcursor = Visitorsdb.cursor()
    visitorcursor.execute("CREATE TABLE IF NOT EXISTS UserDetails (VisitorID TEXT FirstName TEXT, SecondName TEXT, image TEXT)")
    #Here the databases will be created so that they can be used throughout the program


class Stack():
    def __init__(self,maxsize):
        self.maxsize = maxsize
        self.contents = [None for i in range(self.maxsize)]
        self.top =-1
        self.routes = []
        self.startingpoints = []
        self.destinationpoints = []
    #This will set up the stack. Initially, the contents of it will be empty.
    def push(self,newroute):
        self.top +=1 
        self.contents[self.top] = newroute
        #This is the procedure that will be called when a route is added to the stack
    def clearstack(self):
        self.contents = [None for i in range(self.maxsize)]
        self.top =-1
        self.routes = []
        self.startingpoints = []
        self.destinationpoints = []
        #This is the procedure that will clear the stack if the user has selected another route
    def listroutes(self):
        for i in range(0,len(self.contents)):
            if self.contents[i] != None:
                self.routes.append((str(self.contents[i])))
        return self.routes
    #Here, the contents of the stack will be listed so that the user can view their previous routes

    def startingpoint(self,thestartingpoint):
        if thestartingpoint == 'r':
            return self.startingpoints
        else:
            self.startingpoints.append(thestartingpoint)
            print (self.startingpoints)
    def destinationpoint(self,thedestinationpoint):
        if thedestinationpoint == 'r':
            return self.destinationpoints
        else:
            self.destinationpoints.append(thedestinationpoint)
            print (self.destinationpoints)
    #The starting and destination points will be stored in separate lists





class ExistingVisitorScreen(Screen):
    visitorinformation = []
    def on_enter(self,*args):
        self.thecamera = Camera(play = True, index = 0, resolution = (800,800))
        self.add_widget(self.thecamera)
        Snackbar(text = "Press the camera button in order for your face to be scanned").open()
        camerabutton = MDIconButton(icon = "camera", icon_size = "60dp", pos_hint = {"x": 0.85, "y": 0.45}, md_bg_color= "grey",on_press = self.facerecognised)       
        self.add_widget(camerabutton)
        #This piece of code will access the user's camera to allow their face to be scanned.
    def facerecognised(self,*args):
        screen_manager = self.manager
        visitorscreen = screen_manager.get_screen('existingvisitor')
        self.thecamera.export_to_png("facecomparison.png")
        visitorscreen.visitorinformation = facerecog.validface()
        if visitorscreen.visitorinformation[0] == 'Invalid':
            Snackbar(text = "No face identified, take another picture").open()
            self.manager.current = "visitorscreen"
            #This will control instances where no face has been picked up, or the scanned face is invalid
        else: 
            self.clear_widgets()
            self.manager.current = "existingroutes"
            #User will be taken to existing routes screen to load their existing routes if their face is recognised
          
global routeStack
routeStack = Stack(5)
class ExistingRouteScreen(Screen):
    def on_enter(self, *args):
        screen_manager = self.manager
        screen_manager = self.manager
        visitorscreen = screen_manager.get_screen('existingvisitor')
        Visitorsdb = sql.connect("Visitors.db")
        routecursor = Visitorsdb.cursor()
        routecursor.execute("SELECT FirstName,SecondName FROM UserDetails WHERE VisitorID = ?", (visitorscreen.visitorinformation[1],))
        details = routecursor.fetchall()
        print (details)
        name = (str(details[0][0] + ' ' + details[0][1])) + "'s routes"
        routecursor.close()
        username = MDLabel(text = name, pos_hint = {"x":0.25,"y":0.3})
        username.font_size = "30sp"
        self.add_widget(username)
        routesdb = sql.connect("Routes.db")
        routecursor2 = routesdb.cursor()
        routecursor2.execute("SELECT RouteId, StartingPoint, DestinationPoint, DATE FROM VisitorRoutes WHERE visitorID = ? ORDER BY Days DESC ", (visitorscreen.visitorinformation[1],))
       #This query will get all the routes of the user who has been identifed
        userRoutes = routecursor2.fetchall()
        #I have printed it to test that the correct routes are being selected
        #Here I have instantiated the stack - the maximum size of the stack is 6
        routestoremove = []
        routeStack.clearstack()
        #A new route has been added so the stack will be cleared so that it can be updated when the user enters the existing visitors screen
        if len(userRoutes) > 5:
            for i in range (5,len(userRoutes)):
                routecursor2.execute("DELETE FROM VisitorRoutes WHERE RouteID = ?",(userRoutes[i][0],))
                routesdb.commit()
                routecursor2.execute("SELECT * FROM VisitorRoutes")
                print(routecursor2.fetchall())
                print (userRoutes[i])
         #This will delete the 5th route and onwards from the database
        if len(userRoutes) == 5:
            for i in range(0,5):
                currentroute = userRoutes[i][1] + ' TO ' + userRoutes[i][2] + ' - ' + userRoutes[i][3]
                routeStack.push(currentroute)
                routeStack.startingpoint(userRoutes[i][1])
                routeStack.destinationpoint(userRoutes[i][2])
                #Here the most 5 recent routes will be pushed onto the stack 
        elif len(userRoutes) > 5:
            for route in range(5,len(userRoutes)):
                routestoremove.append(route)
            for removedroute in routestoremove:
                userRoutes.remove(removedroute)
            #The 6th route and onwards will be removed from the list
            for i in range(0,5):
                currentroute = userRoutes[i][1] + ' TO ' + userRoutes[i][2] + ' - ' + userRoutes[i][3]
                routeStack.push(currentroute)
                routeStack.startingpoint(userRoutes[i][1])
                routeStack.destinationpoint(userRoutes[i][2])
                #Here the most 5 recent routes will be pushed onto the stack 
            #If there are more than 5 routes, the excess routes will be removed before they are added to the stack
        else:
            for i in range(0,len(userRoutes)):
                currentroute = userRoutes[i][1] + ' TO ' + userRoutes[i][2] + ' - ' + userRoutes[i][3]
                routeStack.push(currentroute)
                routeStack.startingpoint(userRoutes[i][1])
                routeStack.destinationpoint(userRoutes[i][2])
        self.visitorRoutes = routeStack.listroutes()
        print (self.visitorRoutes)
        #Most 5 recent routes will be displayed
    def drpmenu(self,instance):
        self.dropdown_list = []
        for i in self.visitorRoutes:
            self.dropdown_list.append(  {
    "viewclass": "OneLineListItem", "text": (str(i)) , "on_release": lambda x = i: self.option_callback(x)
            })
        self.dropdown = MDDropdownMenu(items = self.dropdown_list, position= "center", width_mult = 9, )
        self.dropdown.caller = instance
        self.dropdown.open()
        #Here is some code that creates the drop down list and displays it to the user
    def option_callback(self,option):
        Snackbar(text = "The route you have selected is " + (str(option))).open()
        self.ids.selectedexistingroute.text = option
        #The user's choice will be stored as text
       
    def newroute(self):
        screen_manager = self.manager
        homescreen = screen_manager.get_screen('home')
        homescreen.currentnumofvisitors +=1
        #This will increase the current number of visitors currently using the application on this device
        existingvisitor = screen_manager.get_screen('existingvisitor')
        homescreen.currentvisitors.append(existingvisitor.visitorinformation[1])
        #This will add the id of the visitor to the currentvisitors list
        #A visitor has joined the site so number of visitors will increment by one
        self.manager.current = "startingscreen"
        #User will be taken to the starting screen so they can choose their starting point
    
    def existingroute(self):
        if self.ids.selectedexistingroute.text != "Select One Of Your Existing Routes":
            userstartingpoints = routeStack.startingpoint("r")
            userdestinationpoints = routeStack.destinationpoint("r")
            #This will return the starting and destination points that have been stored in each of the lists
            selectedroute = self.ids.selectedexistingroute.text
            print (selectedroute)
            #The route that has been selected will be stored here
            routenum = 0
            found = False
            print (userstartingpoints)
            print (userdestinationpoints)
            while routenum != len(userstartingpoints) and found == False:
                if userstartingpoints[routenum] in selectedroute and userdestinationpoints[routenum] in selectedroute:
                    screen_manager = self.manager
                    destscreen = screen_manager.get_screen('destinationscreen')
                    startscreen = screen_manager.get_screen('startingscreen')
                    startscreen.startingpoint.text = userstartingpoints[routenum]
                    #The starting point that has been identified will be stored
                    destscreen.destinationpoint.text = userdestinationpoints[routenum]
                    print (destscreen.destinationpoint.text)
                    #The destination point that has been identified will be stored
                    found = True
                    #This will break out of the loop while as the search is complete
                else:
                    routenum +=1
            #This while loop identifies the starting and destination point the user has chosen amongst their existing routes
            screen_manager = self.manager
            homescreen = screen_manager.get_screen('home')
            existingvisitorscreen = screen_manager.get_screen('existingvisitor')
            homescreen.currentnumofvisitors +=1
            homescreen.currentvisitors.append(existingvisitorscreen.visitorinformation[1])
            #This code will update the current number of visitors once they've chosen an existing route
            self.manager.current = "loadingscreen"
            #Screen will be switched to the loading screen while the user waits for their route to be generated



        



    

class HomeScreen(Screen):  
    currentnumofvisitors = 0
    currentvisitors = []
    picturestaken = 0
    consented = 'No'
    routesselected = 0
    #Here specific attributes relating to visitors will be stored
    valid = False
    global Visitorsdb
    Visitorsdb = sql.connect("Visitors.db")
    global thecursor
    routecursor = Visitorsdb.cursor()
    fname = ObjectProperty(None)
    sname = ObjectProperty(None)
    global alphabet
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','n','m','o','p','q','r','s','t','u','v','w','x','y','z']
    #Here I am declaring variables and lists that I will be making use of
    def isvalid(self):
    #This code will take the first name, and surname the user has inputted, and check that every character is in the alphabet. If it is, then you can assume the name is valid
        fnamecount = 0
        snamecount = 0
        for letter in self.ids.fname.text:
            if letter.lower() in alphabet:
                fnamecount = fnamecount+1
        for letter in self.ids.sname.text:
            if letter.lower() in alphabet:
                snamecount = snamecount+1
        if fnamecount == len(self.ids.fname.text) and snamecount  == len(self.ids.sname.text):
            valid = True
        else:
            valid = False
        return valid
    def pressedAV(self):
        Visitorsdb = sql.connect("Visitors.db")
        routecursor = Visitorsdb.cursor()
        #This code will take the first name, and surname the user has inputted, and check that every character is in the alphabet. If it is, then you can assume the name is valid
        fnamecount = 0
        snamecount = 0
        for letter in self.ids.fname.text:
            if letter.lower() in alphabet:
                fnamecount = fnamecount+1
        for letter in self.ids.sname.text:
            if letter.lower() in alphabet:
                snamecount = snamecount+1
        if fnamecount == len(self.ids.fname.text) and snamecount  == len(self.ids.sname.text):
            valid = True
        else:
            valid = False
        #a = isvalid()
        #Number that will be added to the visitorID to prevent duplication
        duplicationnum = 1
        #Prevents the visitor from pressing the submit button if they have not entered any of their details
        if self.ids.fname.text != '' and self.ids.sname.text != '' and valid == True:
        #Generates a visitorID for each record (consists of first letter of their first name and all of their second name)
            thevisitorID = self.ids.fname.text[0] + self.ids.sname.text
            #Check to see whether the visitorID already exists as it should be unique for each record
            results = routecursor.execute("SELECT * FROM UserDetails")
            for line in results.fetchall():
                while thevisitorID == line[0][0]:
                    duplicationnum +=1 
                    thevisitorID = self.ids.fname.text[0] + self.ids.sname.text + str(duplicationnum)


            #This will insert the details the user has entered into the database
            routecursor.execute("INSERT INTO UserDetails (VisitorID, FirstName,SecondName) VALUES (?,?,?)", (thevisitorID,self.ids.fname.text,self.ids.sname.text))
            #for line in results.fetchall():
            #   print line[0]
            
            #Will save any changes that have been made, updating the database
            Visitorsdb.commit()
            self.ids.fname.text = ''
            self.ids.sname.text = ''
            screen_manager = self.manager
            homescreen = screen_manager.get_screen('home')
            homescreen.currentnumofvisitors +=1 
            #This variable will increment by one to show there's one more visitor in the group, or to show that one visitor has come to visit the site
            homescreen.currentvisitors.append(thevisitorID)
            #The current user's details will be added to the currentvisitors list.

            routecursor.close()
        else:
            Snackbar(text = "Invalid input").open()

      

       
   
 
      
    
    def pressedsubmit(self):
        Visitorsdb = sql.connect("Visitors.db")
        routecursor = Visitorsdb.cursor()
        #This code will take the first name, and surname the user has inputted, and check that every character is in the alphabet. If it is, then you can assume the name is valid
        fnamecount = 0
        snamecount = 0
        for letter in self.ids.fname.text:
            if letter.lower() in alphabet:
                fnamecount = fnamecount+1
        for letter in self.ids.sname.text:
            if letter.lower() in alphabet:
                snamecount = snamecount+1
        if fnamecount == len(self.ids.fname.text) and snamecount  == len(self.ids.sname.text):
            valid = True
        else:
            valid = False
        
        #Number that will be added to the visitorID to prevent duplication
        duplicationnum = 1
        #Prevents the visitor from pressing the submit button if they have not entered any of their details
        if self.ids.fname.text != '' and self.ids.sname.text != '' and valid ==True:
            #Generates a visitorID for each record (consists of first letter of their first name and all of their second name)
            thevisitorID = self.ids.fname.text[0] + self.ids.sname.text
            #Check to see whether the visitorID already exists as it should be unique for each record
            results = routecursor.execute("SELECT * FROM UserDetails")
            for line in results.fetchall():
                while thevisitorID in line:
                    thevisitorID = self.ids.fname.text[0] + self.ids.sname.text + str(duplicationnum)
                    duplicationnum +=1 
            #This will insert the details the user has entered into the database
            routecursor.execute("INSERT INTO UserDetails (VisitorID, FirstName,SecondName) VALUES (?,?,?)", (thevisitorID,self.ids.fname.text,self.ids.sname.text))
     
            #Will save any changes that have been made, updating the database
            Visitorsdb.commit()
            screen_manager = self.manager
            homescreen = screen_manager.get_screen('home')
            homescreen.currentnumofvisitors +=1 
            #Since visitors can come in a group, this will record the amount of visitors present together on site
            homescreen.currentvisitors.append(thevisitorID)
            #The current user's details will be added to the currentvisitors list.

        else:
            Snackbar(text = "Invalid input").open() 
    routecursor.close()

class CameraScreen(Screen):
    def on_enter(self,*args):
        self.thecamera = Camera(play = True, index = 0, resolution = (800,800))
        self.add_widget(self.thecamera)
        #Camera will be added to the screen
        Snackbar(text = "Press the camera button to take a picture").open()
        camerabutton = MDIconButton(icon = "camera", icon_size = "60dp", pos_hint = {"x": 0.85, "y": 0.45}, md_bg_color= "grey",on_press = self.captureimage)       
        self.add_widget(camerabutton)
        #This piece of code will access the user's camera to allow them to take a picture of their face.
        
    def captureimage(self,*args):
        Visitorsdb = sql.connect("Visitors.db")
        routecursor = Visitorsdb.cursor()
        screen_manager = self.manager
        homescreen = screen_manager.get_screen('home')
        if homescreen.picturestaken < homescreen.currentnumofvisitors:
            self.imagename = "./" + str(homescreen.currentvisitors[homescreen.picturestaken]) + '.png'
            #The name of the image will consist of the visitor's id so each image has a unique name
            print (self.imagename)
            self.thecamera.export_to_png(self.imagename) 
            #Here, the image taken will be exported as a png
            try:
                facecheck = DeepFace.analyze(self.imagename)
                #This will check that the picture being taken is a face
            except:
                Snackbar(text = "Face not recognised. Please try again.").open()
                #Snackbar will pop up if no face is recognised
                facecheck = None
                #Facecheck will be set to None as no face has been found in the image provided
            if facecheck != None:
                print (self.imagename)
                routecursor.execute("UPDATE UserDetails SET image = ? WHERE VisitorID = ?",(self.imagename,homescreen.currentvisitors[homescreen.picturestaken]))
                Visitorsdb.commit()
                routecursor.execute("SELECT * FROM UserDetails")
                if homescreen.currentnumofvisitors > 1:
                    Snackbar(text = "Visitor " + (str(homescreen.picturestaken+1)) + " picture has been taken").open()


                #Image of user will be added to the userdetails database if a face is detected
                homescreen.picturestaken +=1

                if homescreen.picturestaken == homescreen.currentnumofvisitors:
                    print (homescreen.picturestaken)
                    self.manager.current = "startingscreen"
                #If all the visitors in the group, or the visitor has taken their pictures, they can be taken to the starting screen

    #This is a check to see that the image that has been captured is a face, so that it can be stored in the UserDetails database
  
    #If the user presses the camera button, this is the function that will be called. It will allow the current frame of the camera to be captured and recorded
  
        routecursor.close()



class StartingPointScreen(Screen):  
    def on_enter(self,*args):
        identified = False
        appname = MDLabel(text = "QEGS Route Finder", pos_hint = {"x":0.05,"y":0.36})
        appname.font_size = 25
        self.add_widget(appname)
        destinationtitle = MDLabel(text = "Starting Point", pos_hint = {"x":0.43,"y":0.08})
        destinationtitle.font_size = 16
        self.add_widget(destinationtitle)
        banner = MDRaisedButton(text = "QEGS Route Finder - Making the process of finding your way around the school much easier", pos_hint = {"center_x": 0.5,"y":0.68}, md_bg_color = ( 26/255,26/255,26/255,1))
        self.add_widget(banner)
        self.startingpoint = MDRectangleFlatButton(text = "Select Your Starting Point", text_color = "grey", pos_hint = {"center_x": 0.5, "y": 0.40}, on_release = self.drpmenu)
        self.add_widget(self.startingpoint)
        confirmbutton = MDRaisedButton(text = "Confirm", md_bg_color = (32/255,45/255,115/255,1), pos_hint = {"center_x": 0.5, "y": 0.20}, on_press = self.confirmstarting)
        self.add_widget(confirmbutton)
        returnbutton  = MDRaisedButton(text = "Return", pos_hint = {"x":0.85,"y":0.82}, md_bg_color = (1,0,0,1), on_release = self.switch)
        RoutesDb = sql.connect('Routes.db')
        Routecursor = RoutesDb.cursor()
        Routecursor.execute("SELECT * FROM VisitorRoutes")
        routes = Routecursor.fetchall()
        #All the records from the visitor routes table will be selected
        homescreen = self.manager.get_screen("home")
        for route in routes:
            if homescreen.currentvisitors[0] in route:
                identified = True
        #If the ID is in any of the tuples (containing the routes), then it means the user is an existing visitor
        if homescreen.currentnumofvisitors == 1 and identified == True:
            pass
        else:
            self.add_widget(returnbutton)
        #The return button will only be displayed to the user if they are not an existing visitor
        
    def switch(self,*args):
        self.clear_widgets()
        self.manager.current = 'home'

    def drpmenu(self,instance):
        self.dropdown = MDDropdownMenu()
        departments = ["Art","Chemistry","DT","Economics/Business","Elizabeth Theatre","English","Head Office","History","Languages","Latin","Lecture Room","Library","Lower Biology","Lower Geography","Lower Maths","Main Entrance","Office", "Matron","Music","Politics","Physics","QE Hall","Religious Studies","Sixthform Centre","Sports Hall","Upper Geography","Upper Maths"]
        #I have stored all the departments in a list so that the list can be iterated through to create a drop down list full of options
        self.dropdown_list = []
        for i in departments:
            self.dropdown_list.append(  {
    "viewclass": "OneLineListItem", "text": (str(i)) , "on_release": lambda x = i: self.option_callback(x)
            })
        self.dropdown = MDDropdownMenu(items = self.dropdown_list, position= "bottom", width_mult = 4, )
        self.dropdown.caller = instance
        self.dropdown.open()
        #Here is some code that creates the drop down list and displays it to the user
    def option_callback(self,option):
        Snackbar(text = "Your current starting point is " + (str(option))).open()
        self.startingpoint.text = option
        #This piece of code will display to the user the starting point they have selected
        #self.dropdown.dismiss()
        global sourcenode
    def confirmstarting(self,*args):
        if self.startingpoint.text != 'Select Your Starting Point':
            global sourcenode
            sourcenode = self.startingpoint.text
            #If the user's choice is valid, it will be stored in the source node
            print (sourcenode)
            if self.manager.current == "startingscreen":
                self.clear_widgets()
                self.manager.current = "destinationscreen"
                #This ensures the screen is only switched to the destination screen if the screen prior to that was the starting screen
            return sourcenode
        else:
            Snackbar(text = "You need to select an option").open()
            #This is the procedure that will be called if the user has not selected their starting p

        #This is the starting point that the user has chosen. It will need to be used in other parts of the program so I have returned it so that the result can be used outside this function

    


class DestinationPointScreen(Screen):
    thegraph = {"Main Entrance": {"DT": 13, "Lower Geography": 42, "Head Office": 44, "Office": 49, "Lecture Room": 57, "History": 61, "Languages": 36, "Music": 22, "Lower Biology": 57, "Sports Hall": 87, "Economics/Business": 53, "Sixthform Centre": 93,"Elizabeth Theatre": 93, "QE Hall": 66, "Bathroom 1 (Near DT)": 21},
"Office": {"Main Entrance":49, "Economics/Business": 27, "QE Hall": 67, "Sports Hall": 75, "Head Office": 12, "Matron": 25, "Religious Studies": 39, "Bathroom 2 (Next to Matron)": 21},
"Economics/Business": {"Main Entrance": 53, "Office": 27},
"Head Office": {"Main Entrance": 44, "Office": 12},
"DT": {"Main Entrance": 13, "Lower Geography": 45, "Bathroom 1 (Near DT)": 5},
"QE Hall": {"Main Entrance":  66, "Sports Hall": 28, "Office": 67,"Bathroom 3 (QE Hall)": 1},
"Lecture Room": {"Main Entrance": 57},
"Religious Studies": {"Office": 39},
"Matron": {"Office": 25, "Bathroom 2 (Next to Matron)": 7},
"Sports Hall": {"Elizabeth Theatre": 103, "Sixthform Centre": 102, "History": 72, "Office": 75, "QE Hall": 28, "Main Entrance": 87},
"Elizabeth Theatre": {"Main Entrance": 93, "English": 45, "Library": 71, "Sixthform Centre": 4, "Sports Hall": 103},
"History": {"Main Entrance": 61, "Sports Hall": 72, "Sixthform Centre": 33, "Lower Biology": 19, "Latin": 11, "Lower Maths": 16,"Fire Exit 1 (Near History)": 9},
"Sixthform Centre": {"Elizabeth Theatre": 4, "Sports Hall": 102, "History": 33, "Library": 71, "Main Entrance": 93, "English": 45,"Bathroom 4 (Sixthform Centre)": 6},
"Library": {"Elizabeth Theatre": 71, "English": 30, "Sixthform Centre": 71, "Chemistry": 13},
"Lower Geography": {"DT": 45, "Main Entrance": 93, "Upper Geography": 14, "Lower Biology": 23, "Lower Maths": 20},
"Upper Geography": {"Physics": 26, "Lower Geography": 14, "Upper Maths": 16, "Lower Maths": 22, "Lower Biology": 27},
"English": {"Elizabeth Theatre": 45, "Library": 30,  "Sixthform Centre": 45,  "Politics": 17}, "Politics": {"English": 17,  "Physics": 4}, "Upper Maths": {"Upper Geography": 16, "Physics": 47}, "Physics": {"Politics": 4, "Upper Geography": 26, "Upper Maths": 47, "Lower Biology": 18, "Lower Maths": 14, "Chemistry": 27},
"Lower Maths": {"Physics": 14, "Chemistry": 27, "Lower Biology": 17, "Latin": 9, "History": 16},
"Latin": {"Lower Maths": 9, "Chemistry": 36, "History": 11}, "Chemistry": {"Physics": 27, "Library": 13, "Lower Maths": 27, "Latin": 36},
"Lower Biology": {"Main Entrance": 57, "Languages": 69, "Music": 55, "Lower Geography": 23, "Latin": 20, "Lower Maths": 17,  "Physics": 18, "History": 19, "Upper Geography": 27,"Fire Exit 1 (Near History)": 9},
"Art": {"Languages": 12, "Music": 23},
"Music": {"Lower Biology": 55, "Languages": 33, "Art": 23, "Main Entrance": 22, "Bathroom 1 (Near DT)": 22},
"Languages": {"Art": 12, "Music": 33, "Lower Biology": 69, "Main Entrance": 36, "Bathroom 1 (Near DT)": 34}, "Bathroom 4 (Sixthform Centre)": {"Sixthform Centre": 6}, "Bathroom 3 (QE Hall)": {"QE Hall": 1}, "Bathroom 2 (Next to Matron)": {"Matron": 7, "Office": 21, "Religious Studies": 18}, "Bathroom 1 (Near DT)": {"Languages": 34, "Music": 22, "Main Entrance": 21, "DT": 5}, "Fire Exit 1 (Near History)" : {"History": 9, "Lower Biology": 9}
}
#This is the graph that will store all the nodes as well as their neighbours and their weights
    #Here is my implementation of dijkstra's algorithm that will determine the quickest route using the user's starting point and end point
    def get_startingscreen(self):
        screenref = self.manager.get_screen("startingscreen")
        startingpoint = str(screenref.startingpoint.text)
        return startingpoint
        #This piece of code accesses the previous screen to store the starting point the user has selected


    def getdestination(self):
        global destinationnode
        destinationnode = self.destinationpoint.text
        return destinationnode
        #This piece of codes stores the destination point that the user has selected
    
        
    def on_enter(self,*args):
        screen_manager = self.manager
        thescreen = screen_manager.get_screen('startingscreen')
        destscreen = screen_manager.get_screen('destinationscreen')
        homescreen = screen_manager.get_screen('home')
        theusersourcenode = destscreen.get_startingscreen()
        returnpointtext = ("FROM " + str(theusersourcenode))
        appname = MDLabel(text = "QEGS Route Finder", pos_hint = {"x":0.05,"y":0.36})
        appname.font_size = 25
        self.add_widget(appname)
        destinationtitle = MDLabel(text = "Destination Point", pos_hint = {"x":0.43,"y":0.08})
        destinationtitle.font_size = 16
        self.add_widget(destinationtitle)
        self.destinationpoint = MDRectangleFlatButton(text = "Select Your Destination Point", text_color = "grey", pos_hint = {"center_x": 0.5, "y": 0.40}, on_release = self.drpmenudestination)
        self.add_widget(self.destinationpoint)
        self.returnpoint = MDRaisedButton(text = returnpointtext, pos_hint = {"center_x": 0.5, "y": 0.68})
        self.add_widget(self.returnpoint)
        confirmbutton = MDRaisedButton(text = "Confirm", md_bg_color = (32/255,45/255,115/255,1), pos_hint = {"center_x": 0.5, "y": 0.20}, on_press = self.confirmdestination)
        self.add_widget(confirmbutton)
        returnbutton  = MDRaisedButton(text = "Return", pos_hint = {"x":0.85,"y":0.82}, md_bg_color = (1,0,0,1), on_release = self.switch)
        if homescreen.routesselected >= 1:
            pass
        else:
            self.add_widget(returnbutton)
        #The return button will only be added to the screen if the user has not yet selected a route

        
        #This will display the user's starting point choice on the destination screen, as well as all the other widgets
    def switch(self,*args):
        self.clear_widgets()
        self.manager.current = 'startingscreen'
    #Here is the code that displays the return button to the user only if they have not already selected a route
    def drpmenudestination(self,instance):
        self.dropdowndestination = MDDropdownMenu()
        departments = ["Art","Chemistry","DT","Economics/Business","Elizabeth Theatre","English","Head Office","History","Languages","Latin","Lecture Room","Library","Lower Biology","Lower Geography","Lower Maths","Main Entrance","Office", "Matron","Music","Politics","Physics","QE Hall","Religious Studies","Sixthform Centre","Sports Hall","Upper Geography","Upper Maths"]
        #This is a list that stores all the departments of the schools
        self.dropdowndestination_list = []
        for i in departments:
            self.dropdowndestination_list.append(  {
    "viewclass": "OneLineListItem", "text": (str(i)) , "on_release": lambda x = i: self.option_callback(x)
            })
           
        self.dropdowndestination = MDDropdownMenu(items = self.dropdowndestination_list, position= "bottom", width_mult = 4, )
        self.dropdowndestination.caller = instance
        self.dropdowndestination.open()
         #This code loops through the departments so that each item can be added to the drop down list
    def option_callback(self,option):
        if self.returnpoint.text == "FROM " + str(option):
            self.destinationpoint.text = option
            Snackbar(text = "You cannot select the same starting point as destination point").open()
            self.destinationpoint.text = "Select Your Destination Point"
        #If the user selects the same starting point and destination point, they will be told that their choice is invalid. This means they will have to choose another destination point

        else:
            Snackbar(text = "Your current destination point is " + (str(option))).open()
            self.destinationpoint.text = option
        #self.dropdown.dismiss()
        #Based on the department the user has pressed, their chosen department will be recorded so that it can be used later on.
    def dijkstrasalgorithm(self,graph,startnode,endnode):
        unvisited = {}
        visited = {}
        path = []
        thecost = 0
        previous = 1       
        for node in graph:
            unvisited[node] = [sys.maxsize,None]

        unvisited[startnode][thecost] = 0   
        currentnode = startnode
        while unvisited != {} and currentnode != endnode: 
            #The quickest route finding process will continue until the unvisited list is empty and the current node becomes the goal node. This means the route has been found
            neighbours = graph[currentnode]
            #This will get all the neighbours of the current node
            for node in neighbours:
                if node not in visited:
                    cost =  neighbours[node] + (unvisited[currentnode][thecost]) 
                    if cost < unvisited[node][thecost]:
                        unvisited[node][thecost] = cost 
                        unvisited[node][previous] = currentnode
            visited[currentnode] = unvisited[currentnode]
            #This piece of code will check the cost of the current node + the neighbour that is currently being dealt with. If the total is less than the weight of that neighbour, their cost will be updated. Otherwise, no change will be made to the cost.
            del unvisited[currentnode]
            #Once all the current node's neighbours have been visited, it can be removed from the unvisited list
            if unvisited !={}:
                currentnode = min(unvisited, key = unvisited.get)
                #Amongst the nodes in the unvisited list, the node with the lowest weight will be the next one to be dealt with
                #print (visited)
        path.append(endnode)
        somenode = unvisited[endnode][1]
        path.append(somenode)
        while somenode != None:
            path.append(visited[somenode][1])
            somenode = visited[somenode][1]
        #This piece of code will trace the quickest pathway back to the startnode, allowing the quickest route to be displayed to the user
        estimatedtime = (unvisited[endnode][0])/60
        roundedestimatedtime = round(estimatedtime,1)
        print (path)
        print (roundedestimatedtime)
        #This piece of code will convert the time from seconds into minutes by dividing it by 60, and rounding it to the nearest decimal place
        dijkstrasresults = []
        #This will store the results from the path finding process which includes the identified route and estimated until arrival
        dijkstrasresults.append(path)
        dijkstrasresults.append(roundedestimatedtime)
        return dijkstrasresults
    def confirmdestination(self,obj):
        screen_manager = self.manager
        destscreen = screen_manager.get_screen('destinationscreen')
        if self.destinationpoint.text != "Select Your Destination Point":
            destscreen.dijkstrasalgorithm(destscreen.thegraph,destscreen.get_startingscreen(),self.destinationpoint.text)
            self.clear_widgets()
            self.manager.current = "loadingscreen"
        else:
            Snackbar(text = "You need to select an option").open()
       

class LoadingScreen(Screen):
    dialog = None
    def on_enter(self,*args):
        screen_manager = self.manager
        startscreen = screen_manager.get_screen('startingscreen')
        theusersourcenode = str(startscreen.startingpoint.text)
        #This piece of code will get the user's starting point
        destscreen = screen_manager.get_screen('destinationscreen')
        theuserdestinationnode = str(destscreen.destinationpoint.text)
        #This piece of code will get the user's destination point
        self.ids.sourceanddestinationpoint.text = ("From " + theusersourcenode + " To " + theuserdestinationnode)
       #Now that we have both the user's starting and destination point, they can be displayed as text to the user
        departmentinformation = {"Art": ["Every week an artist of the week is chosen, which allows us to showcase all our talented artists throughout the year.", "You study art from year 7, with the option to choose it at GCSE and A Level.", "Students typically have one art lesson per week."], "Chemistry": ["Chemistry is compulsory up until A level", "There is a good balance between experiments and theoretical content", "Boys are tested regularly throughout the year to ensure they are keeping up with the content."],"DT": ["There are several workshops which allow boys to get on with practical work", "Boys are given the freedom to manufacture anything they want using the available materials", "DT is optional at GCSE and A Level."], "Economics/Business": ["These are two subjects that are very popular amongst GCSE and A Level students", "There are trips on offer that allow boys to go to London to learn more about business and economics", "Cannot be studied from Year 7 - 9"], "Elizabeth Theatre": ["Junior school plays are typically performed here", "This is the room where sixthform assemblies are hosted", "Boys typically come in here to play table tennis at break and lunchtimes"], "English": ["Boys have many opportunities to take part in creative writing competitions", "Boys typically study a book to aid their comprehension skills", "Boys will also conduct a presentation in front of their class to improve their speaking skills"], "Head Office": ["Typically the least visited area by students","Every year, all year 12 forms are invited here for pizza and discussion","Visitors may enter the office if they would like to speak to the head"],"History": ["Boys typically study key areas of the past such as World War 2", "There is coursework at A Level which allows you to conduct a historical investigation","Optional at GCSE and A Level"], "Languages": ["A range of languages are on offer at QEGS such as french, spanish, and german", "You can only study one of french and spanish in Year 7", "There are language plays hosted with the girls school each year"], "Latin": ["A subject that is compulsory in year 7 and 8", "Latin becomes optional from Year 9","Not as popular as other subjects but many find it interesting"], "Lecture Room": ["Typically visitors that come in to give a talk conduct them here", "This room is also used for year group assemblies", "The Lecture room has a maximum capacity of 50 people"], "Library": ["A quiet area for students to get on with some work", "Only 3 fictional books, and 3 non fictional books can be borrowed at a time", "Students typically get their textbooks from here"], "Lower Biology": ["Biology is compulsory up until A Level", "There is a good balance between experiments and theoretical content", "A common experiment that students are taught is the osmosis experiment using potatoes"], "Lower Geography": ["Geography at QEGS is much more than learning about countries of the world","There are many topics that students learn about such as human geography","Another subject that is very popular amongst GCSE and A Level students"], "Lower Maths": ["Every year group takes part in the UKMT to put their problem solving to the test", "There are regular assessments to check that students are on top of the content", "Many videos are published online by teachers to support students"], "Main Entrance": ["Boys typically enter school through this entrance", "You can speak to the office through the phone in case you have any issues", "The code is changed regularly to maintain security"], "Office": ["Visitors typically come here to speak to office staff in person", "Top GCSE and A Level results are displayed on the wall here", "There is a sofa allowing visitors to sit down and get comfortable if they need to speak to anyone"],"Matron": ["Boys will typically come see matron if they are feeling unwell in any way", "Matron will provide medication if a boy is feeling unwell", "The room is close to the office"],"Music": ["Boys are given the freedom to play a range of instruments", "It becomes optional at GCSE and A Level", "Boys get the chance to perform in school concerts"], "Politics": ["Can only be studied at A Level", "Only subject that is taught in only one classroom", "Classes typically have a mix of boys and girls"],"Physics": ["There is a good level of balance between theory and experiments","Boys develop their mathematical and scientific skills simultaneously","We typically enter our students into physic competitions"], "QE Hall": ["Full school assemblies are conducted here", "Prize giving assemblies are hosted here and parents are invited", "Senior school plays take place here"], "Religious Studies": ["You learn about many other religions", "You are not just taught about religion but also ethics", "Optional at GCSE and A Level"], "Sixthform Centre": ["Space for sixthformers to relax at break and lunchtime", "Food is made at break time that they are free to purchase", "Sixthformers typically use their free periods to get work done in here"], "Sports Hall": ["Sport is highly regarded at QEGS", "Rugby, hockey and cricket are three sports taken very seriously here", "Our coaches have played at high levels in their respective sports, demonstrating their high level of experience"],"Upper Geography": ["Geography at QEGS is much more than learning about countries of the world","There are many topics that students learn about such as human geography","Another subject that is very popular amongst GCSE and A Level students"], "Upper Maths": ["Every year group takes part in the UKMT to put their problem solving to the test", "There are regular assessments to check that students are on top of the content", "Many videos are published online by teachers to support students"]

}
# Here is a dictionary containing all the department information. This will allow visitors to understand more about the department so they can ask questions.
        Clock.schedule_once(self.next_screen,1)
        #After 9 seconds, the screen will switch
#Here is all the information about each department. This information will be displayed to the user, depending on the destination point they have chosen
        def updatetext(dt):
            global informationnum
            if informationnum != 3:
                self.ids.informationbox.text = str(departmentinformation[theuserdestinationnode][informationnum])
                informationnum +=1
        #This is the procedure that will be repeatedly called every 3.5 seconds, allowing the text to be updated
        global informationnum
        informationnum = 0
        initialinformation = str(departmentinformation[theuserdestinationnode][0])
        self.ids.informationbox.text = initialinformation
        #The first piece of information relating to the destination point will be displayed to the user upon their arrival to the loading screen
        Clock.schedule_interval(updatetext,3.5)

        #This line of code will update the label every 3.5 seconds so that a new piece of information can be displayed
    def show_alert_dialog(self):
        questions = ["Q: What is the entrance assessment?","Q: How much are the school fees?","Q:  What are the GCSE and A level exam results like?","Q: Why should I choose QEGS and not another school?", " Q:  What kind of clubs do you offer?", "Q:  Do you have school buses to get to and from school?", "Q:  How many boys are in a class?", "Q: Can I get a reduction in the school fees?"]
        #Here is a list containing questions that are commonly asked about the school. This list will be iterated through so each question is displayed.
        answers = ["A: The entrance assessment is an exam taken by students looking to join from years 7-10","A: Typically the school fee is £16250 annually, however this is subject to increases", "A: Boys typically perform exceptionally nationally. 30% of our A level students achieved A and A* grades in 2023. Furthermore 60% of boys achieved 7-9 grades at GCSE", "A: The support at QEGS is exceptional, as boys are always supported throughout their time at the school. We also offer many extra curricular activities to help boys develop life skills. The broad range of trips we offer allow boys to reach new horizons", "A: We offer all sorts of clubs from sport clubs such as football and rugby, to fantasy role playing games such as dungeons and dragons. There really is no limit to the clubs we have on offer", "A: We offer a number of bus routes across Yorkshire which are available for all students from age 8.", "A: Class sizes can vary, however typically there are around 30 students per class in years 7-11. Class sizes are much smaller at A Level due to the freedom in the subjects you can pick.", "A: Yes, it is possible to get a reduction in the school fees as there are scholarships and bursaries on offer if a candidate has very high academic ability. Household income is also something that we consider"]
        #Here is the list containing the answers to the questions
        global information
        information = ''
        #I have made the information variable global so that the variable updates in line with the changes to it in the for loop
        for i in range (0,len(questions)-1):
            information = information + str(questions[i]) + '\n' + str(answers[i]) + '\n'
            #\n will create a new line for each question and each answer to separate each line of text
            information = information + "\n"
            #This line of code will separate each question set which consists of the question and the answer to the question
        if not self.dialog:
            self.dialog = MDDialog(
            text = information, buttons = [MDFlatButton( text = "Close", on_release = self.close_dialog),
            ],
            
            )
        
        self.dialog.open()
        #This piece of code will display the dialog box so that the user can read the information

    def close_dialog(self,obj):
        self.dialog.dismiss()
    
    def next_screen(self,dt):
        self.manager.current = "themap"
        #This piece of code will move the user to the next screen after a certain amount of time


    
class MapScreen(Screen):
    returnback = False
    Bathrooms = ["Bathroom 1 (Near DT)", "Bathroom 2 (Next to Matron)", "Bathroom 3 (QE Hall)","Bathroom 4 (Sixthform Centre)"]
    Fireexits = ["Fire Exit 1 (Near History)", "Elizabeth Theatre"]
    fireexitsunstored = ["Fire Exit 1 (Near History)"]
    def nearest(self):
        global nearestresults
        nearestresults = []
        #The list will be empty, allowing the values to be appended to it throughout the function
        screen_manager = self.manager
        destscreen = screen_manager.get_screen('destinationscreen')
        startscreen = screen_manager.get_screen('startingscreen')
        mapscreen = screen_manager.get_screen('themap')
        #This will allow me to access the data from the starting and destination screens
        global bathroomcurrentquickestroute
        bathroomcurrentquickestroute = None
        #There is currently no quickest route for the bathroom
        global lowestestimatedtime
        bathroomlowestestimatedtime = sys.maxsize
        remainingbathrooms = 4
        #This is a list that stores all the bathrooms in the school. They will be used to identify the closest bathroom to the user's starting point

        global nearestbathroom
        nearestbathroom = None
        #Currently, the nearestbathroom has not been identified, so it is assigned a value of 'None'
        current = 0
        #This will allow the first item in the bathroom list to be accessed
        while remainingbathrooms != 0:
            #The while loop will continue until all the bathrooms have been examined
            routecompare = destscreen.dijkstrasalgorithm(destscreen.thegraph,startscreen.startingpoint.text, mapscreen.Bathrooms[current])
            #Here dijkstra's algorithm will be performed to identify the estimated time until arrival to the current bathroom
            if routecompare[1] < bathroomlowestestimatedtime:
                bathroomlowestestimatedtime = routecompare[1]
                nearestbathroom = mapscreen.Bathrooms[current]
                bathroomcurrentquickestroute = routecompare[0]
            #If the estimated time of the route is less than the current lowest estimated time, it should be updated. Moreover, this means that it will now become the nearest bathroom
            current +=1
            #Increment current by one to access the data of another bathroom
            remainingbathrooms -=1
            #This variable should be decremented by one once the current bathroom has been dealt with
        nearestresults.append(nearestbathroom)
        nearestresults.append(bathroomcurrentquickestroute)
        nearestresults.append(bathroomlowestestimatedtime)

        global lowestestimatedtime
        global fireexitcurrentquickestroute
        fireexitcurrentquickestroute = None
        fireexitlowestestimatedtime = sys.maxsize
        remainingbathrooms = 4
        #This is a list that stores all the fire exits in the school. They will be used to identify the closest fire exit to the user's starting point
        global nearestfireexit
        nearestfireexit = None
        remainingfireexits = 2
        #Currently, the nearestfireexit has not been identified, so it is assigned a value of 'None'
        current = 0
        #This will allow the first item in the fire exit list to be accessed
        while remainingfireexits != 0:
            #The while loop will continue until all the fire exits have been examined
            routecompare = destscreen.dijkstrasalgorithm(destscreen.thegraph,destscreen.get_startingscreen(), mapscreen.Fireexits[current])
            #Here dijkstra's algorithm will be performed to identify the estimated time until arrival to the current fire exit
            if routecompare[1] < fireexitlowestestimatedtime:
                fireexitlowestestimatedtime = routecompare[1]
                nearestfireexit = mapscreen.Fireexits[current]
                fireexitcurrentquickestroute = routecompare[0]
            #If the estimated time of the route is less than the current lowest estimated time, it should be updated. Moreover, this means that it will now become the nearest fire exit
            current +=1
            #Increment current by one to access the data of another fire exit
            remainingfireexits -=1
            #This variable should be decremented by one once the current fire exit has been dealt with
        nearestresults.append(nearestfireexit)
        nearestresults.append(fireexitcurrentquickestroute)
        nearestresults.append(fireexitlowestestimatedtime)
        return nearestresults
        #This will return a list which stores the nearest bathroom, the lowest estimated time to that bathroom, the route to the bathroom, and the same thing for the fire exits
        
#Here is the updated graph containing all the departments as well as the nearest bathrooms and fire exits. It will be used to generate the route to the nearest bathroom and fire exit
    def leavesite(self,obj):
        screen_manager = self.manager
        destscreen = screen_manager.get_screen('destinationscreen')
        startscreen = screen_manager.get_screen('startingscreen')
        mapscreen = screen_manager.get_screen('themap')
        #This code will allow me to access the starting and destination point screens
        mapscreen.returnback = True
        #If this is set to 'true' then the 'done' button will not be displayed to the screen
        startscreen.startingpoint.text = destscreen.destinationpoint.text
        #This will set the starting point to the previous destination point
        destscreen.destinationpoint.text = "Main Entrance"
        #This will set the destination point as the main entrance so the user can leave the site
        self.manager.current = "loadingscreen"
        self.dialog.dismiss()

    def removeuserdetails(self,obj):
        screen_manager = self.manager
        homescreen = screen_manager.get_screen('home')
        Visitorsdb = sql.connect("Visitors.db")
        routesdb = sql.connect("Routes.db")
        routecursor2 = routesdb.cursor()
        routecursor = Visitorsdb.cursor()
        if homescreen.currentnumofvisitors == 1:
            routecursor2.execute("DELETE FROM VisitorRoutes WHERE VisitorID = ?",(homescreen.currentvisitors[0],))
            routecursor.execute("DELETE FROM UserDetails WHERE VisitorID = ?",(homescreen.currentvisitors[0],))
            Visitorsdb.commit()
            routesdb.commit()
            #User's routes will be removed from the database if they do not consent, as well as their details
            routecursor2.close()
            routecursor.close()
        else:
            for visitor in homescreen.currentvisitors:
                routecursor2.execute("DELETE FROM VisitorRoutes WHERE VisitorID = ?", (visitor,))
                routecursor.execute("DELETE FROM UserDetails WHERE VisitorID = ?",(visitor,))
                Visitorsdb.commit()
                routesdb.commit()
                routecursor2.close()
                routecursor.close()
                #If it's a group of visitors, all their routes will be removed, as well as the user details
        self.dialog.dismiss()
        #This will close the pop up box
    def on_enter(self,*args):
        screen_manager = self.manager
        thescreen = screen_manager.get_screen('destinationscreen')
        mapscreen = screen_manager.get_screen('themap')
        homescreen = screen_manager.get_screen('home')
        if homescreen.consented == 'No':
            self.dialog = MDDialog(
                text = "Do you consent to your details being stored for future visits?", buttons = [MDFlatButton( text = "Yes", on_release = self.close_dialog), MDFlatButton( text = "No", on_release = self.removeuserdetails)
                ],
            
                )
            self.dialog.open()
            homescreen.consented = 'Yes'
        #This piece of code will display the dialog box so that the user can read the information, if they have 
        #not already been asked
        #The user should only need to consent once throughout the run time of the application
        thenearestresults = mapscreen.nearest()
        #This will allow me to use variables from the 'destinationscreen' and map screen
#Here is the graph that will be used to perform dijkstra's algorithm again, using the starting and destination point to regenerate the quickest route
        title = MDLabel(text = "Queen Elizabeth Grammar School - Map", pos_hint = {"center_x": 0.72, "y": 0.445})
        title.font_size = "25sp"
        self.add_widget(title)
        routeandtime = thescreen.dijkstrasalgorithm(thescreen.thegraph,thescreen.get_startingscreen(),thescreen.getdestination())
        #The table storing the VisitorRoutes will be created if it does not already exist
        currentdate = dt.datetime.today()
        dateasstring = currentdate.strftime('%d-%m-%y')
        #This will store the current date so the date the route was accessed can be recorded
        dateresult = currentdate - referencedate
        routecursor = Visitorsdb.cursor()
        routecursor.execute("Select RouteID from VisitorRoutes")
        routeids = routecursor.fetchall()
        newrouteid = len(routeids)+1
        print (thescreen.get_startingscreen())
        print (thescreen.getdestination())
        if (thescreen.get_startingscreen() not in mapscreen.Bathrooms and thescreen.getdestination() not in mapscreen.Bathrooms) and (thescreen.get_startingscreen() not in mapscreen.fireexitsunstored and thescreen.getdestination() not in mapscreen.fireexitsunstored):
            if homescreen.currentvisitors == 1:
                routecursor.execute("INSERT into VisitorRoutes (VisitorID,RouteID, StartingPoint, DestinationPoint, Date, Days) VALUES (?,?,?,?,?,?)",(user,newrouteid,thescreen.get_startingscreen(),thescreen.getdestination(),dateasstring,dateresult.days,))
                Visitorsdb.commit()
            #This code will add new routes into the database
            else:
                for user in homescreen.currentvisitors:
                    routecursor.execute("INSERT into VisitorRoutes (VisitorID, RouteID, StartingPoint, DestinationPoint, Date, Days) VALUES (?,?,?,?,?,?)",(user,newrouteid,thescreen.get_startingscreen(),thescreen.getdestination(),dateasstring,dateresult.days,))
                    #This considers visitors coming as a group. They will all have taken the same route so they will have the same routes being added to the database
                    Visitorsdb.commit()
            #Changes in the database will be confirmed here
        #Routes will only be added to the database if they are not routes to the nearest bathroom or fire exit
           
    
        results = routecursor.execute("SELECT * FROM VisitorRoutes")
        print ("___________________")
        print (results.fetchall())
        routecursor.close()

        quickestpath = routeandtime[0]
        #The 'routeandtime' variable will store the result of dijkstra's algorithm
        mapkey = {"Art": [8, "black",0.01,-0.31,0.66,0.317],"Chemistry": [20, "black",0.01,-0.35,0.479,-0.015],"DT": [9, "black",0.01,-0.39,0.453,0.224],"Economics/Business": [3, "black",0.01,-0.43,0.459,0.265],"Elizabeth Theatre": [13, "black",0.01,-0.47,0.351,-0.061],"English": [23, "black",0.15,-0.31,0.432,-0.109],"Head Office": [2, "black",0.15,-0.35,0.44,0.315],"History": [11,"black",0.15,-0.39,0.425,0.134],"Languages": [7, "black",0.15,-0.43,0.599,0.25],"Latin": [19, "black",0.15,-0.47,0.458,0.114],"Lecture Room": [5, "black",0.25,-0.31,0.532,0.351],"Library": [21, "black",0.25,-0.35,0.343,-0.132],"Lower Biology": [18, "black",0.25,-0.39,0.425,0.03],"Lower Geography": [10, "black",0.25,-0.43,0.478,0.175],"Lower Maths": [25, "black",0.25,-0.47,0.527,0.110],"Main Entrance": [1, "black",0.39,-0.31,0.483,0.329],"Office": [4, "black",0.39,-0.35,0.418,0.348], "Matron": [14, "black",0.39,-0.39,0.375,0.260],"Music": [6, "black",0.39,-0.43,0.605,0.322],"Politics": [24, "black",0.39,-0.47,0.531,-0.104],"Physics": [22,"black",0.5,-0.31,0.5273,-0.035],"QE Hall": [16, "black",0.5,-0.35,0.362,0.208],"Religious Studies": [15, "black",0.5,-0.39,0.421,0.265],"Sixthform Centre": [12, "black",0.5,-0.43,0.303,-0.018],"Sports Hall": [17, "black",0.5,-0.47,0.389,0.199],"Upper Geography": [26, "black",0.63,-0.31,0.5275,0.165],"Upper Maths": [27, "black",0.63,-0.35,0.57,0.08], "Bathroom 1 (Near DT)": [28,"black", 0.63,-0.39,0.501,0.242], "Bathroom 2 (Next to Matron)": [29,"black", 0.63,-0.43,0.3460,0.268],"Bathroom 3 (QE Hall)": [30,"black", 0.63,-0.47,0.337,0.1967],"Bathroom 4 (Sixthform Centre)": [31,"black", 0.81,-0.31,0.333,-0.0056],"Fire Exit 1 (Near History)": [32,"black", 0.81,-0.35,0.407,0.104],"Fire Exit 2 (Elizabeth Theatre)": [33,"black", 0.81,-0.39,0.387,-0.048]}
        #The map key consists of the number the department relates to, and also the department itself. It also contains the positions of the keys on the map, as well as their positions on the points of the map.
        for department in mapkey:
            if department in quickestpath:
                mapkey[department][1] = "blue"
         #This code will colour code the keys that are part of the quickest route so they can be uniquely identified

        mapkey[thenearestresults[0]][1] = "purple"
        mapkey[thenearestresults[3]][1] = "green"
        #The nearest bathroom and fire exit will be colour coded so they can be identified by the user
        self.labels = [MDLabel(text = str(mapkey[point][0]) + '. ' + str(point), theme_text_color = "Custom",text_color =  str(mapkey[point][1]), pos_hint = {"x": mapkey[point][2], "y": mapkey[point][3]}) for point in mapkey] 
        for label in self.labels:
            label.font_size = "10.5sp"
            #This will change the size of the labels in the mapkey
        [self.add_widget(label) for label in self.labels] 
        #This piece of code will print the map key, which will be done using a for loop
        global finalroute
        finalroute = str(quickestpath[len(quickestpath)-2])
        #This will store the sourcenode into the final route variable
        for i in range(len(quickestpath)-3,-1,-1):
            if quickestpath[i] != None:
                finalroute = finalroute + ' - ' + quickestpath[i]
        #This piece of code loops through the quickest path list to display it to the user. After every iteration it will be concatenated with the finalroute variable which holds the source node initially
        fireexitfinalroute = ''
        fireexitfinalroute = str(thenearestresults[4][len(thenearestresults[4])-2])
        for i in range(len(thenearestresults[4])-3,-1,-1):
            if thenearestresults[4][i] != None:
                fireexitfinalroute = fireexitfinalroute + '\n' + ' - ' + thenearestresults[4][i]
        #This piece of code loops through the quickest route list to display it to the user. After every iteration it will be concatenated with the finalroute variable which holds the source node initially
        #Here, the quickest route will be displayed to the user
        routelabel = MDLabel(text = "The quickest route is: " + finalroute + '(Estimated time: ' + str(routeandtime[1]) + " minutes)",pos_hint = {"center_x": 0.52,"y":-0.22})
        
        self.add_widget(routelabel)
        bathroomfinalroute = ''
        bathroomfinalroute = str(thenearestresults[1][len(thenearestresults[1])-2])
        for i in range(len(thenearestresults[1])-3,-1,-1):
            if thenearestresults[1][i] != None:
                bathroomfinalroute = bathroomfinalroute + '\n' + ' - ' + thenearestresults[1][i]
        #This piece of code loops through the quickest route list to display it to the user. After every iteration it will be concatenated with the finalroute variable which holds the source node initially
        if thescreen.get_startingscreen() == thenearestresults[0]: #This is a check to see that the starting point is not the nearest bathroom
            self.add_widget(MDRaisedButton(text = "Go to nearest fire exit", md_bg_color = (7/255,140/255,18/255,1), pos_hint = {"x": 0.74,"y": 0.7}, on_press = self.show_alert_dialogfire)) #This will add the fire exit button to the screen
            #Here is the button that the user will need to press in order to go to the nearest fire exit
            routelabel = MDLabel(text = "Nearest Fire Exit:\n " + fireexitfinalroute + '\n(Estimated time: ' + str(thenearestresults[5]) + " minutes)",pos_hint = {"x": 0.02,"y":0.05})
            self.add_widget(routelabel)
            #Here the route to the nearest bathroom will be displayed to the user if the user is not already there
            doneypos = 0.55
        elif thescreen.get_startingscreen() == thenearestresults[3]: #This is a check to see whether the starting point is the nearest fire exit
            doneypos = 0.55
            self.add_widget(MDRaisedButton(text = "Go to nearest bathroom", md_bg_color = (32/255, 45/255, 115/255, 1), pos_hint = {"x": 0.73,"y": 0.7}, on_press =self.show_alert_dialog,)) #If the starting point is not the nearest bathroom then the button can be displayed on the screen
            #Here is the button that the user will need to press in order to go to the nearest bathroom
            routelabel = MDLabel(text = "Nearest Bathroom:\n " + bathroomfinalroute + '\n(Estimated time: ' + str(thenearestresults[2]) + " minutes)",pos_hint = {"x": 0.02,"y":0.3}) 
            self.add_widget(routelabel)
            

        else:
            doneypos = 0.35
            #This sets the y position of the 'done' button
            self.add_widget(MDRaisedButton(text = "Go to nearest bathroom", md_bg_color = (32/255, 45/255, 115/255, 1), pos_hint = {"x": 0.73,"y": 0.7}, on_press =self.show_alert_dialog,)) #If the starting point is not the nearest bathroom then the button can be displayed on the screen
            self.add_widget(MDRaisedButton(text = "Go to nearest fire exit", md_bg_color = (7/255,140/255,18/255,1), pos_hint = {"x": 0.74,"y": 0.5}, on_press = self.show_alert_dialogfire)) #This will add the fire exit button to the screen
            routelabel = MDLabel(text = "Nearest Bathroom:\n " + bathroomfinalroute + '\n(Estimated time: ' + str(thenearestresults[2]) + " minutes)",pos_hint = {"x": 0.02,"y":0.3}) 
            self.add_widget(routelabel)
            routelabel = MDLabel(text = "Nearest Fire Exit:\n " + fireexitfinalroute + '\n(Estimated time: ' + str(thenearestresults[5]) + " minutes)",pos_hint = {"x": 0.02,"y":0.05})
            self.add_widget(routelabel)
        finished = MDRaisedButton(text = "Done", md_bg_color = (223/255, 9/255, 227/255,1), pos_hint = {"x": 0.8,"y": doneypos}, on_press = self.donedialog)
        #Here is the button that the user will need to press if they have finished following the quickest route 
        if mapscreen.returnback == False:
            self.add_widget(finished) #This will add the done button to the screen
        for department in mapkey:
            if department in quickestpath:
                mapkey[department][1] = "yellow"
            #If the key is part of the quickest route, the text will change to yellow
            else:
                mapkey[department][1] = "white"
                #Otherwise, the text will be white
        mapkey[thenearestresults[0]][1] = "pink"
        mapkey[thenearestresults[3]][1] = "lime"
        #The nearest bathroom and fire exit will be highlighted so the user knows where to find them
        self.keys = [MDLabel(text = "[b]" + str(mapkey[department][0]) + "[/b]", markup = True, theme_text_color = "Custom",text_color =  str(mapkey[department][1]) , pos_hint = {"x": mapkey[department][4], "y": mapkey[department][5]}) for department in mapkey] 
        #This will print out all the numbers onto the various points using a loop. It will position them using the the two values stored in the dictionary at index 4 and 5
        theimage = Image(source = "C:/Users/Family/Downloads/map.png", pos_hint = {"center_x":0.5,"y":0.34},size_hint = (1.65, 0.55))
        
        self.add_widget(theimage)
        for key in self.keys:
            key.font_size = "13sp"
            #This will change the size of the labels
        [self.add_widget(key) for key in self.keys] 
        #Here the numbers will be added to the screen
    dialog = None
    def show_alert_dialog(self,*args):
        self.dialog = MDDialog(
            text = "Would you like to go ahead with this change? Your route will be recalculated.", buttons = [MDFlatButton(text = "Confirm", on_release = self.bathroomrecalculatedroute), MDFlatButton(text = "Close", on_release = self.close_dialog)])
        
        self.dialog.open()
        #This piece of code will display the dialog box so that the user can read the information
    def show_alert_dialogfire(self,*args):
        self.dialog = MDDialog(
            text = "Would you like to go ahead with this change? Your route will be recalculated.", buttons = [MDFlatButton(text = "Confirm", on_release = self.fireexitrecalculatedroute), MDFlatButton(text = "Close", on_release = self.close_dialog)])
        
        self.dialog.open()
    def donedialog(self,*args):
        self.dialog = MDDialog(text = "Would you like to select another route?", buttons = [MDFlatButton(text = "Yes", on_press = self.newroute), MDFlatButton(text = "No",on_press = self.leavesite)])
        
        self.dialog.open()
        #This piece of code will display the dialog box so that the user can read the information
    
    def newroute(self,obj):
        screen_manager = self.manager
        destscreen = screen_manager.get_screen('destinationscreen')
        startscreen = screen_manager.get_screen('startingscreen')
        homescreen = screen_manager.get_screen('home')
        #This code will allow me to access the starting and destination point screens
        startscreen.startingpoint.text = destscreen.destinationpoint.text
        #This will set the starting point to the previous destination point
        destscreen.destinationpoint.text = "Select Your Destination Point"
        #The destination point button will then be reset to allow the user to select another
        self.manager.current = "destinationscreen"
        #This will switch the screen so that the user can select a new destination point
        self.dialog.dismiss()
        #This will close the pop up box
        homescreen.routesselected +=1



    def close_dialog(self,obj):
        self.dialog.dismiss()
    def bathroomrecalculatedroute(self,obj):
        screen_manager = self.manager
        startscreen = screen_manager.get_screen('startingscreen')
        #The data from the starting screen will need to be accessed so the starting point can be changed to the nearest bathroom
        themap = screen_manager.get_screen('themap')
        nearestresults = themap.nearest()
        #The 'nearestresults' variable will store the nearest bathroom and fire exit that has been identified, as well as the lowest estimated times and the routes to them for both (as a list)
        startscreen.ids.startingpointchoice.text = nearestresults[0]
        #The nearest bathroom is stored at index 0, so this will become the new starting point
        self.dialog.dismiss()
        self.manager.current = "loadingscreen"
        #The user will be taken to the loading screen while the recalculated route is being generated
    def fireexitrecalculatedroute(self,obj):
        screen_manager = self.manager
        startscreen = screen_manager.get_screen('startingscreen')
        #The data from the starting screen will need to be accessed so the starting point can be changed to the nearest fire exit
        themap = screen_manager.get_screen('themap')
        nearestresults = themap.nearest()
        #The 'nearestresults' variable will store the nearest bathroom and fire exit that has been identified, as well as the lowest estimated times and the routes to them for both (as a list)
        startscreen.ids.startingpointchoice.text = nearestresults[3]
        #The nearest fire exit is stored at index 3, so this will become the new starting point
        self.dialog.dismiss()
        self.manager.current = "loadingscreen"
        #The user will be taken to the loading screen while the recalculated route is being generated
    def on_leave(self,*args):
        self.clear_widgets()
        #The widgets will be cleared from the screen once the screen switches so that a new route can be displayed if the user returns to the map screen
        
    
        


    
      




    
class QegsRouteFinder(MDApp):
    #This is the sub class which is the base for creating the application
    def build(self):
        #Sets the theme of the application to light, so the background will appear white effectively
        self.theme_cls.theme_style = "Light"
        #All buttons will appear in this colour initially
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Blue"
        kv = Builder.load_file('designfile.kv')
        return kv
    
   




    


if __name__ == '__main__':
    QegsRouteFinder().run()
    #This piece of code will display the app to the user