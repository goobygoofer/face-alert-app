const express = require('express');
bodyParser = require('body-parser');
const app = express();
app.use(bodyParser.json());
const http = require('http');
const server = http.createServer(app);
//const { Server } = require("socket.io");
//const io = new Server(server);
var nodemailer = require('nodemailer');
var fs = require('fs');

//pass needs to NOT be stored in plain text here - implement your own security!
var transporter = nodemailer.createTransport({
	service: 'emailserviceprovider',//e.g. 'gmail'
	auth: {
		user: 'user@email.com',//replace with your email and password
		pass: 'password'       //you may have to set up an alternative Password
		                       //with your email provider for it to work!
	}
});

//send email alert to address
sendAlertEmail = function(buff){
	img=buff;
	var mailOptions = {
	    from : 'user@email.com',  //replace with sender email
	    to: 'otherUser@email.com',//replace with recipient, can be same as sender and/or multiple recips
	    subject: 'Alert!',        //this can be whatever, make sure it's something you notice in email!
	    text: 'Face detected!',   //also can be whatever
	    attachments: [{'filename': 'attachment.png', 'content':img}],//image attached to file, name can be whatever
		                                                             //although could be named by timestamp or etc...
    }
	transporter.sendMail(mailOptions, function(error, info){
		if (error) {
			console.log(error);//did not send...
		} else {
			console.log('Email sent: ' + info.response);//success!
		}
	});
}

var emailSent = false    //bool used in app.post('/reciever'... to limit email spam
var sessionTotal = 0;    //incremental, used for naming regular frames        change sessionTotal and facesThisSession
var facesThisSession = 0;//incremental, used for naming priority frames(faces)    initializes to length of respective dirs

//receive images, sort regular frames from priority frames(faces), save to respective dir
app.post('/receiver',(req, res) => {
	picData = {'img':req.body.img, 'ts':req.body.ts, 'type':req.body.type};
	res.end();
	let buff = Buffer.from(picData['img'], 'base64');//buff is an actual image object...
    if (picData['type']==='priority'){
		facesThisSession+=1;                         //that gets saved here...
		fs.writeFileSync('./Local/Faces/' + JSON.stringify(facesThisSession) + '.png', buff);
		if (emailSent==false){
		    sendAlertEmail(buff);                    //and gets emailed here!
		    emailSent = true;//should wait for sent confirmation!
		    setTimeout(function(){emailSent=false}, 30000);//limit email spam. comment out and watch your inbox fill up...
			                                                                   //(not recommended!)
		}
		return
	}
    sessionTotal+=1;
	fs.writeFileSync('./Local/Feed/' + JSON.stringify(sessionTotal) + '.png', buff);
});
  
//server listening for incoming images!
server.listen(8080, () => {
  console.log('listening on *:8080');
});