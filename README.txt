To run:

-Must be able to run a basic node server

-Make sure main directory has:

  -server.js
  
  empty file folders for images to be saved to:
  -Local
    -Feed
    -Faces

-cam-driver.py can be on any machine on the local network
 as long as python is installed, added to PATH, and proper modules installed

cmd:
-Navigate to project directory then:
  >>node server.js

  listening on port 8080 by default

-Then run cam-driver.py to capture, process, and send images to node server
 -machine with cam-driver.py on it must have web cam (built in or external)
  and have access to the local network the node server is running on
  
  if on same machine, should be able to access via localhost:8080
  on another machine on same network, needs to be full ip address to server machine

Received images are saved to server machine, priority images (containing faces)
are expedited in the threadQueue so they get to server before less important images
then the server emails the face to the desired recipient(s)

As it is, images will pile up on server machine and you will need to manually clean them up
Will eventually add something to detect # of files in dir and delete oldest image as
new image comes in (with a window of X images as defined by user)
i.e. when "Feed" file grows to 1000 frames or greater, delete oldest frame
upon receiving new frame, unless user specified otherwise

NOTE-might have to set up alternative password to use app with your email provider

NOTE-read all notes within cam-driver.py and server.js!
     this is a simple project but make sure you read everything first!

NOTE!!!
the following instructions might be needed, will test on a machine without anything
installed on it to make sure what's what and what does or doesn't need to be installed!:

make package.json file
{
  "name": "example",
  "version": "0.0.1",
  "description": "",
  "dependencies": {}
}

(in project directory via cmd):

npm install express@4

npm install socket.io

package.json should look something like this now:
{
  "name": "template",
  "version": "1.0.0",
  "description": "",
  "dependencies": {
    "express": "^4.18.2",
    "socket.io": "^4.5.4"
  }
}

The above instructions might only be needed if node isn't installed?
Tested without doing above instructions and it worked, but it could
just be my machine with it's current (and somewhat messy) installations.
Originally there was supposed to be an HTML client to view the live camera
but I decided to go with something more simplified and lightweight, so some
stuff here might not need to be here, I'll clean it up as I tinker...