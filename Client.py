from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		
		
		
	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		playImg = PhotoImage(file="play.png")
		setupImg = PhotoImage(file="gear.png")
		pauseImg = PhotoImage(file="pause.png")
		tearImg = PhotoImage(file="teardown.png")
		print("done images")
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, padx=3, pady=3,image=setupImg, command=self.setupMovie)
		self.setup.image = setupImg
		self.setup.grid(row=1, column=0, padx=100, pady=50)
		self.play = Button(self.master,  padx=3, pady=3,image=playImg, command=self.playMovie)
		self.play.image = playImg
		self.play.grid(row=1, column=1, padx=100, pady=50)
		self.pause = Button(self.master, padx=3, pady=3,image=pauseImg, command=self.pauseMovie)
		self.pause.image = pauseImg
		self.pause.grid(row=1, column=2, padx=100, pady=50)
		self.tear = Button(self.master, padx=3, pady=3,image=tearImg, command=self.exitClient)
		self.tear.image = tearImg
		self.tear.grid(row=1, column=3, padx=100, pady=50,)
		self.label = Label(self.master, height=35, width=30)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)
		# self.setup = Button(self.master, width=20, padx=3, pady=3, )
		# self.setup["text"] = "Setup"
		# self.setup["command"] = self.setupMovie
		# self.setup["image"] = setupImg
		# self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		# self.start = Button(self.master, width=20, padx=3, pady=3)
		# self.start["text"] = "Play"
		# self.start["command"] = self.playMovie
		# self.start["image"] = playImg
		# self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		# self.pause = Button(self.master, width=20, padx=3, pady=3)
		# self.pause["text"] = "Pause"
		# self.pause["command"] = self.pauseMovie
		# self.pause["image"] = pauseImg
		# self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		# self.teardown = Button(self.master, width=20, padx=3, pady=3)
		# self.teardown["text"] = "Teardown"
		# self.teardown["command"] =  self.exitClient
		# self.teardown["image"] = tearImg
		# self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		# self.label = Label(self.master, height=19)
		# self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)

	
	def exitClient(self):
		"""Teardown button handler."""
		if self.state == self.READY or self.state == self.PLAYING:
			print("press tear down button")
			self.sendRtspRequest(self.TEARDOWN)

	def pauseMovie(self):
		if self.state == self.PLAYING:
			print("press pause button")
			self.sendRtspRequest(self.PAUSE)
			

	
	def playMovie(self):
		if self.state == self.READY:
			self.eventThread = threading.Event()
			self.eventThread.clear()
			self.rcvThread = threading.Thread(target=self.listenRtp, daemon=True).start()
			print("press play button")
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		#TODO
		while True:
			try:
				if self.eventThread.is_set():
					break
				print("receiving")
				data, _ = self.rtpSocket.recvfrom(102400)
				rtpPacket = RtpPacket()
				rtpPacket.decode(data)
				print(self.frameNbr)
				print(rtpPacket.seqNum())
				if self.frameNbr < rtpPacket.seqNum():
					temp = self.writeFrame(rtpPacket.getPayload())
					self.updateMovie(temp)
					self.frameNbr = rtpPacket.seqNum()
			except:
				if self.teardownAcked == 1:
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					break
			
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		tempImgFile = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		f = open(tempImgFile, "wb")
		f.write(data)
		f.close()
		return tempImgFile
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		frame = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image=frame, height=500)
		self.label.image = frame
		print("updated frame")

		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientSocket.connect((self.serverAddr, self.serverPort))
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		if requestCode == self.SETUP:
			self.rtspThread = threading.Thread(target=self.recvRtspReply, daemon= True).start()
			self.rtspSeq += 1
			requestMessage = f"SETUP movie.Mjpeg RTSP/1.0\nCseq: {self.rtspSeq}\nTransport: RTP/UDP; client_port= {self.rtpPort}"
		elif requestCode == self.PLAY:
			self.rtspSeq += 1
			requestMessage = f"PLAY movie.Mjpeg RTSP/1.0\nCseq: {self.rtspSeq}\nSession {self.sessionId}"
		elif requestCode == self.PAUSE:
			self.rtspSeq += 1
			requestMessage = f"PAUSE movie.Mjpeg RTSP/1.0\nCseq: {self.rtspSeq}\nSession {self.sessionId}"
		elif requestCode == self.TEARDOWN:
			self.rtspSeq += 1
			requestMessage = f"TEARDOWN movie.Mjpeg RTSP/1.0\nCseq: {self.rtspSeq}\nSession {self.sessionId}"

		self.requestSent = requestCode
		print(self.requestSent)
		self.clientSocket.send(requestMessage.encode("utf-8"))
		
	
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		while True:
			reply, addr = self.clientSocket.recvfrom(2048)
			self.parseRtspReply(reply.decode())
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		#TODO
		lines = data.split('\n')
		code = lines[0].split(' ')[1]
		cseq = lines[1].split(' ')[1]
		sess = lines[2].split(' ')[1]
		if str(self.rtspSeq) == str(cseq) and code == "200":
			if self.requestSent == self.SETUP:
				self.openRtpPort()
				self.state = self.READY
				self.sessionId = sess
			elif self.requestSent == self.PLAY:
				self.state = self.PLAYING
			elif self.requestSent == self.PAUSE:
				self.eventThread.set()
				self.state = self.READY
			elif self.requestSent == self.TEARDOWN:
				self.eventThread.set()
				self.state = self.INIT
				self.label = Label(self.master, height=30, width=30)
				self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)
				self.frameNbr = -1
				
				# self.rtpSocket.close()
				# self.clientSocket.close()
		
		print(f"{self.state}")
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		# self.rtpSocket = ...
		
		# Set the timeout value of the socket to 0.5sec
		# ...
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.rtpSocket.bind(('', self.rtpPort))
		self.rtpSocket.settimeout(0.5)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		#TODO
		self.exitClient()
		self.rtpSocket.shutdown(socket.SHUT_RDWR)
		self.clientSocket.shutdown(socket.SHUT_RDWR)
		self.master.destroy()
