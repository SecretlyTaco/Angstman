import socket
import random
import sys
import StringIO
import time

"""
For some reason this bot doens't join channels automatically so an admin has to
   /msg BotName .join #chan
replacing botname with nick, and chan with chan from the config below
"""

#Config
nick = "Angstman" #define nick
network = "my.irc.server"
port = 6667
chan = "#lobby"
admins = ["sockspls", "SocksPls"]

with open("wordlist.txt") as f:
    words = f.readlines()

def connect():
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define IRC network

    print "[*] Connecting"
    irc.connect((network,port))
    print "[*] Connected"

    irc.recv (4096)
    irc.send('NICK ' + nick + '\r\n') #Set nick
    irc.send('USER ' + nick + " " + nick + " " + nick + " " + nick + "\r\n") #Sent user info
    irc.send('JOIN ' + chan + "\r\n")
    return irc

def join(chan):
    print("[*] Trying to join " + str(chan))
    irc.send('JOIN ' + chan + "\r\n")

def ping(data):
    irc.send('PONG ' + data.split()[1] + '\r\n') #Send back a PONG

def msgchan(msg, chan):
    irc.send('PRIVMSG ' + chan + " :" + msg + "\r\n")

def voice(tovoice, chan):
    irc.send("MODE " + chan + " v:" + tovoice + "\r\n")

qword = ""
def resetgame(gword=""):
    global qword
    if gword == "" and qword == "":
        word = random.choice(words).strip()
    elif qword != "":
        word = qword
        qword = ""
    else:
        word = gword
    global word
    correct = ""
    global correct
    incorrect = ""
    global incorrect
resetgame()

def showboard(channel):
    clue = ""
    for letter in word:
        if letter in correct:
            clue = clue + " " + letter
        else:
            clue = clue + " " + "_"
    clue = clue[1:]
    if incorrect != "":
        msgchan("Incorrect guesses: " + incorrect, channel)
    msgchan(clue, channel)

irc = connect()

def privmsgdetails(data):
    sender = data.split("!")[0][1:]
    senderhostname = data.split()[0].split("!")[1]
    fromchannel = data.split()[2]
    messagesent = ":".join(data.split(":")[2:])
    return(sender, senderhostname, fromchannel, messagesent)

resetgame() #Starts the first game
while True:
    data = irc.recv (4096)
    print data
    if data.find('PING') != -1:
        ping(data)
    elif data.split()[1] == "PRIVMSG":
        sender, senderhostname, fromchannel, messagesent = privmsgdetails(data)
        if messagesent.startswith(".ping"):
            msgchan("pong", fromchannel)
            reg = 1
        elif messagesent.startswith(".say"):
            msgchan(messagesent[4:], fromchannel)
        elif messagesent.startswith(".join") and sender in admins:
            join(messagesent[6:])
            print "Joining " + messagesent[6:]
        elif messagesent.startswith(".quit") and sender in admins:
            exit()
        elif messagesent.startswith(".word") and sender in admins:
            resetgame(messagesent[5:].strip())
        elif messagesent.startswith(".qword") and sender in admins:
            qword = messagesent[6:].strip()
        elif messagesent.startswith(".reset") and sender in admins:
            msgchan("Resetting game", chan)
            resetgame()
            showboard(chan)
        elif messagesent.startswith(".g"):
            errorcode = 0
            try:
                guess = messagesent[2:].strip()
                guess = guess.lower() #Converts the guess to lowecase
            except:
                showboard(chan)
                guess = ""
            for letter in guess:
                if letter not in "qwertyuiopasdfghjklzxcvbnm":
                    errorcode = 1
            if errorcode == 1:
                msgchan("Your guess can only contain letters", chan)
            elif guess == "":
                pass
            elif len(guess) > 1: #Guessing a word
                if guess == word:
                    msgchan("You win!", chan)
                    resetgame()
                else:
                    msgchan("You guessed the incorrect word " + guess, chan)
            elif guess in correct or guess in incorrect:
                msgchan("You have already guessed the letter " + guess, chan)
            else:
                if guess in word and guess != "":
                    correct += guess
                    msgchan("You guessed the correct letter " + guess, chan)
                    winrar = 1
                    for current in word:
                        if current not in correct: #If any letters are in the word and you haven't guessed them
                            winrar = 0
                    if winrar == 1:
                        showboard(chan)
                        msgchan("You win! Resetting board", chan)
                        resetgame()

                else:
                    incorrect += guess
                    msgchan("You have guessed the incorrect letter " + guess, chan)
            showboard(chan)
