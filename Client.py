from tkinter import *
import tkinter.messagebox
tkinter.messagebox
from tkinter import messagebox 
tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	SETUP_STR = 'SETUP'
	PLAY_STR = 'PLAY'
	PAUSE_STR = 'PAUSE'
	TEARDOWN_STR = 'TEARDOWN'

	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3

	RTSP_VER = "RTSP/1.0"
	TRANSPORT = "RTP/UDP"
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master #GUI
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0 #CSeq number, client and server request and response same number
		self.sessionId = 0 #section number has been responsed from server 
		self.requestSent = -1 #request to server
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		self.countLostFrame = 0
		
		
	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		playImg = PhotoImage(file="play.png")
		setupImg = PhotoImage(file="gear.png")
		pauseImg = PhotoImage(file="pause.png")
		tearImg = PhotoImage(file="teardown.png")
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

	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
		if self.state == self.READY or self.state == self.PLAYING:
			print("pressed tear down button")
			self.sendRtspRequest(self.TEARDOWN)

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			print("pressed pause button")
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			self.eventThread = threading.Event()
			self.eventThread.clear()
			self.rcvThread = threading.Thread(target=self.listenRtp, daemon=True).start()
			print("pressed play button")
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		while True:
			try:
				if self.eventThread.is_set():
					break
				# print("receiving")
				data, _ = self.rtpSocket.recvfrom(102400)
				rtpPacket = RtpPacket()
				rtpPacket.decode(data)
				seqNumPacket = rtpPacket.seqNum()
				if self.frameNbr < seqNumPacket:
					temp = self.writeFrame(rtpPacket.getPayload())
					self.updateMovie(temp)
					self.frameNbr = seqNumPacket
			except:
				# Upon receiving ACK for TEARDOWN request,
				# close the RTP socket
				if self.teardownAcked == 1:
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					break
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()
		return cachename
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		frame = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image=frame, height=500)
		self.label.image = frame

		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.clientSocket.connect((self.serverAddr, self.serverPort))
		except:
			messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		
		# Setup request
		if requestCode == self.SETUP:
			self.rtspThread = threading.Thread(target=self.recvRtspReply, daemon= True).start()
			self.rtspSeq += 1
			print("SETUP ", self.fileName)
			requestMessage = f"SETUP {self.fileName} RTSP/1.0\nCseq: {self.rtspSeq}\nTransport: RTP/UDP; client_port= {self.rtpPort}"
		elif requestCode == self.PLAY:
			self.rtspSeq += 1
			requestMessage = f"PLAY {self.fileName} RTSP/1.0\nCseq: {self.rtspSeq}\nSession {self.sessionId}"
		elif requestCode == self.PAUSE:
			self.rtspSeq += 1
			requestMessage = f"PAUSE {self.fileName} RTSP/1.0\nCseq: {self.rtspSeq}\nSession {self.sessionId}"
		elif requestCode == self.TEARDOWN:
			self.rtspSeq += 1
			requestMessage = f"TEARDOWN {self.fileName} RTSP/1.0\nCseq: {self.rtspSeq}\nSession {self.sessionId}"

		self.requestSent = requestCode
		self.clientSocket.send(requestMessage.encode("utf-8"))
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		while True:
			try:
				reply, addr = self.clientSocket.recvfrom(2048)
				self.parseRtspReply(reply.decode())
			except:
				pass
			# Close the RTSP socket upon requesting Teardown
	
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
				self.countLostFrame = 0
				
				# self.rtpSocket.close()
				# self.clientSocket.close()
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
        
		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(0.5)
		
		try:
			self.rtpSocket.bind(('', self.rtpPort))
		except:
			messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		try:
			self.exitClient()
			self.rtpSocket.shutdown(socket.SHUT_RDWR)
			self.clientSocket.shutdown(socket.SHUT_RDWR)
		except:
			pass
		self.master.destroy()