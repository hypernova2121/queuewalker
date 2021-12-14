import configparser
config = configparser.ConfigParser()
config.read("settings.ini")
from time import sleep
from datetime import datetime
import smtplib
import imaplib
import email
import subprocess
import getpass

import warnings
warnings.simplefilter('ignore', category=UserWarning) #ignore warning that FF14 launcher is 32-bit

from playsound import playsound

import pyautogui
pyautogui.useImageNotFoundException()
pyautogui.FAILSAFE = True

pw = ''
mfa = ''
isLoggedIn = False
waitCounter = 0
errorCounter = 0

def getPassword():
    global pw
    if config['settings']['FF14Password']: #if user stored a password in settings.ini
        return config['settings']['FF14Password']
    else:
        return getpass.getpass("Enter your FF14 Password: ")

def getMFA():
    global mfa
    if not mfa: #first-time
        return (input("Enter your MFA Code: "))
    elif config['settings']['useEmail'].lower() == 'true': #if using email to ask for mfa code
        return sendEmailForMFA()
    else: #if NOT using email to enter subsequent mfa codes
        return (input("Enter your MFA Code: "))

def login():
    
    global pw
    global mfa
    global isLoggedIn
    global waitCounter

    if not pw:
        pw = getPassword()
    if config['settings']['useMFA'].lower() == 'true':
        mfa = getMFA()

    print ('***************************************')
    print ("Logging you in. DON'T TOUCH THE MOUSE")
    print ('***************************************')

    #Open FF14
    try:
        subprocess.Popen([config['settings']['FF14InstallLocation']])
    except FileNotFoundError as e:
        print (f'Error: {e}. Check that the FF14InstallLocation in settings.ini is correct')
        exit('Exiting')
    print ('Waiting for FF14 Launcher to load')
    sleep(6)

    #Use PyAutoGUI to find password screen and enter password and MFA
    print ('Looking for Password field')
    if config['settings']['launcher'].lower() == 'dark':
        loc = findOnScreen('sq_password_dark.png')
    else:
        loc = findOnScreen('sq_password_light.png')
    print ('Entering credentials') #we can only get here if findOnScreen() returns a loc, otherwise a failsafe is triggered and script exits
    pyautogui.moveTo(loc)
    pyautogui.move(0,25) #move mouse cursor over password text box
    pyautogui.doubleClick() #doubleclick just in case there is something already in password field to highlight and delete it
    pyautogui.typewrite(pw)
    pyautogui.press('tab')
    pyautogui.typewrite(mfa)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter') #Select "Login"
    print ('Waiting for login to process')
    sleep(5)

    #would like to add password/mfa error handling here later

    #Click the Play button
    print ('Looking for Play button')
    if config['settings']['launcher'].lower() == 'dark':
        loc = findOnScreen('play_dark.png')
    else:
        loc = findOnScreen('play_light.png')
    pyautogui.click(loc)
    print ('Play button clicked\n')
    sleep(1)
    pyautogui.press('enter') #confirm 2nd play button (if there is an announcment)
    print ('Waiting for FF14 to load')
    sleep(11)

    #Click the Start button
    print ('Looking for Start button')
    loc = findOnScreen('start.png')
    sleep(1) #sometimes doesnt click correctly if the start button just loaded
    inGameClick(loc)
    print ('Start button clicked\n')
    print ('Waiting for Character Selection screen to load')
    sleep(7) #this is also where a 2002 error might happen

    #Click character name (or handle lobby error)
    #Looks for the Backup Character Icon that is next to every character name
    if config['settings']['characterPosition'] == '1':
        loc = findOnScreen('character.png', retryNum=30, checkForError=True) #retryNum is high because it can take 30 seconds before an error might appear
    else:
        loc = findOnScreen('character.png', retryNum=30, checkForError=True, locateAll=True)
        loc = pyautogui.center(loc[int(config['settings']['characterPosition'])-1]) #find the backup icon that corresponds with characterPosition
    if loc == 'err': #if findOnScreen() returns 'err', an error was found by checkForErrorScreen()
        return #break out of login() to start entire login process over
    print ('Found character in position ' + config['settings']['characterPosition'])
    pyautogui.moveTo(loc) #move cursor to the Backup Character Icon
    pyautogui.move(-200,0) #move cursor to the left to actually click on character name
    inGameClick()
    print ('Clicked on character in position ' + config['settings']['characterPosition'])
                
    #Click OK to confirm character login
    print ('Looking for OK button')
    loc = findOnScreen('ok.png')
    inGameClick(loc)
    pyautogui.move(100,100) #move cursor out of the way
    print ('Clicked OK button')

    print ('***************************************')
    print ('You can use the computer again, just be sure that FF14 window is still fully visible at all times')
    print ('***************************************\n')

    print ('Waiting 10 seconds to see if "World is Full" message appears')
    sleep(10)
    try:
        if checkForErrorScreen():
            return #break out of login() and start login process over
        pyautogui.locateOnScreen('worldisfull.png') #look for "world is full" message
        waitCounter += 1
        print (f'See "World is Full" message. In queue ({waitCounter}). Will check again every 30 seconds')
        sleep(30)
        inQueue = True
    except pyautogui.ImageNotFoundException: #never saw world is full message and already checked for black error screen, so user must be logged in (hopefully)
        print ('Never saw "World is Full" message. Assuming user is logged in')
        inQueue = False
        isLoggedIn = True

    #In queue, time to wait
    while inQueue:
        if checkForErrorScreen(): #check for error screen, and if one happened, break out of "while inQueue" loop (and start login() process over)
            break
        try:
            pyautogui.locateOnScreen('worldisfull.png') #look for "world is full" message
            waitCounter += 1
            print (f'Still in queue ({waitCounter})')
            sleep(30)
        except pyautogui.ImageNotFoundException: #dont see world is full message and already checked for black error screen, so user must be logged in (hopefully)
            try:
                sleep(1)
                pyautogui.locateOnScreen('worldisfull.png') #possible that worldisfull message was refreshing, so take a 2nd look to make sure
                waitCounter += 1
                print (f'Still in queue ({waitCounter})')
                sleep(30)
            except pyautogui.ImageNotFoundException:
                print ('No longer see "World is Full" message. Assuming user is logged in')
                inQueue = False
                isLoggedIn = True

def inGameClick(loc=None): #regular pyautogui click doesn't work in-game
    pyautogui.mouseDown(loc)
    sleep(.1)
    pyautogui.mouseUp()

def sendEmail(subject, msgContents, toEmailAddress=config['settings']['toEmail'], fromEmailAddress=config['settings']['fromEmail']):

    msg = email.message.EmailMessage()
    msg['Subject'] = subject
    msg['From'] = fromEmailAddress
    msg['To'] = toEmailAddress
    msg.set_content(msgContents)

    #_ = input("Press Enter when ready to send email (DEBUG)")

    print (f'Sending email to "{toEmailAddress}"')
    print (f'Subject: "{subject}')
    print (f'Body: "{msgContents}"')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(fromEmailAddress,config['settings']['from_email_password'])
        smtp.send_message(msg)
        smtp.quit()

def sendEmailForMFA(retryNum=20, sleepNum=15, toEmailAddress=config['settings']['toEmail'], fromEmailAddress=config['settings']['fromEmail']): 
    
    #send email
    subject = 'FF14 Lobby Error'
    msgContents = 'Reply to this email with MFA Code'
    sendEmail(subject, msgContents)
    
    #wait for email reply
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(fromEmailAddress, config['settings']['from_email_password'])
    print (f'Waiting {sleepNum} seconds for reply to email')
    sleep(sleepNum) #wait sleepNum seconds for email reply
    
    #Keep checking for email reply
    for i in range(retryNum):
        try:
            imap.select("INBOX")
            _, messages = imap.search(None, f'(FROM "{toEmailAddress}" TO "{fromEmailAddress}")') #maybe use UID?
            messages = messages[0].split(b' ')
            _, data = imap.fetch(messages[-1], "(RFC822)") #always take the latest message
            raw_email = data[0][1]
            msg = email.message_from_string(raw_email.decode())
            for part in msg.walk():       
                if part.get_content_type() == "text/plain":
                    mfa = part.get_payload()[:6] #get the first 6 character of reply email, which should be mfa code
                    if mfa.isdigit(): #check if this is a number
                        if config['settings']['deleteEmails'].lower() == 'true': #check if we should delete the mfa emails
                            imap.store(messages[-1], '+FLAGS', '\\Deleted') #delete the REPLY email with MFA code
                            if toEmailAddress == fromEmailAddress:
                                imap.store(messages[-2], '+FLAGS', '\\Deleted') #delete the INITIAL email asking for MFA code too
                            imap.expunge()
                        imap.close()
                        imap.logout()
                        #print (mfa)
                        return (mfa)
                    else:
                        print (f'Did not find email with valid MFA code. Will retry {retryNum - i} more times with {sleepNum} second(s) delay')
                        sleep(sleepNum)
                        break #this is wrong email. wait "sleepNum" seconds and check latest message again
        except imaplib.IMAP4.error:
            print (f'Did not find email from {toEmailAddress}. Will retry {retryNum - i} more times with {sleepNum} second(s) delay')
            sleep(sleepNum)

def checkForErrorScreen(numTimesCheck=5, numSleepTime=1):

    errorOccurred = True
    for i in range(numTimesCheck):
        if not pyautogui.pixelMatchesColor(200, 200, (0, 0, 0)): #don't see black error screen
            #print ('No error')
            errorOccurred = False
            break
        else:
            print (f'Might see error screen. Will check {numTimesCheck - i} more times with {numSleepTime} second(s) delay')
            sleep(numSleepTime)

    if errorOccurred:
        if config['settings']['playAlert'].lower() == 'true':
            playsound('alert.mp3')
        print ('An error has occurred, need to restart FF14')
        global errorCounter
        errorCounter += 1
        loc = findOnScreen('ok_error.png', confidence=0.9) #click ok to error, which will close FF14. Note: passing checkForError=True here will cause infinite loop
        inGameClick(loc)
        sleep(5) #wait for FF14 to close
    
    return errorOccurred 

def findOnScreen(imagePath, retryNum=10, sleepNum=1, confidence=0.95, checkForError=False, locateAll=False):
    for i in range(retryNum):
        try:
            if locateAll:
                return list(pyautogui.locateAllOnScreen(imagePath, confidence=confidence))
            else:
                return pyautogui.locateCenterOnScreen(imagePath, confidence=confidence)
        except pyautogui.ImageNotFoundException:
                print (f'Did not see image on screen matching {imagePath}. Will retry {retryNum - i} times with {sleepNum} second(s) delay')
                sleep(sleepNum)
                if checkForError:
                    if checkForErrorScreen(): #if checkForErrorScreen() found error, it returns True
                        return 'err' #an error has occurred
    
    #if we get here, findOnScreen() could not find the image. script will need to alert user and close
    if config['settings']['useEmail'].lower() == 'true':
        sendEmail("FF14 - Unable to log you in", "Sorry, something went wrong and the script was unable to get you logged in")
    print (f'Could not find image matching {imagePath} after checking {retryNum} times. Script must exit')
    exit('Failsafe triggered, exiting script')

#script start
if config['settings']['useEmail'].lower() == 'true':
    if not config['settings']['toEmail']:
        exit('Put the email you want to receive MFA emails in the "toEmail" settings.ini')

startTime=datetime.now().replace(microsecond=0)
print (f'Script started at {startTime}')

while isLoggedIn == False:
    login()

if config['settings']['useEmail'].lower() == 'true':
    sendEmail('Logged in!', 'You are logged in! Remember, you only have 30 minutes before getting logged out by the AFK timer!')

print (f'\nScript took {datetime.now().replace(microsecond=0)-startTime} to complete')
print (f'Script encountered {errorCounter} lobby error(s)')
