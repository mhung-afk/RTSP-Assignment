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
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3, )
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup["icon"] = setupImg
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start["icon"] = playImg
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause["icon"] = pauseImg
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown["icon"] = tearImg
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)

	
	def exitClient(self):
		"""Teardown button handler."""
	#TODO

	def pauseMovie(self):
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		if self.state == self.READY:
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		#TODO
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
	#TODO
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
	#TODO
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.clientSocket = socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientSocket.connect((self.serverAddr, self.serverPort))
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		if requestCode == self.SETUP:
			threading.Thread(target=self.recvRtspReply).start()
			self.rtspSeq += 1
			requestMessage = f"SETUP movie.Mjpeg RTSP/1.0\nCseq: {self.rtspSeq}\nTransport: RTP/UDP; client_port={self.rtpPort}"
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
		self.clientSocket.send(requestMessage.encode())
		
	
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""

		#TODO
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		#TODO
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		# self.rtpSocket = ...
		
		# Set the timeout value of the socket to 0.5sec
		# ...
		

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		#TODO
