This Python script is designed to automatically log you into FF14, as well as log you back in if a Lobby Error (like Error 2002) occurs. It will also (if enabled) email you once you are logged in

Script will:
1. Open FF14
2. Log you in and select your character by (temporarily) taking control of mouse and keyboard using pyautogui (https://pyautogui.readthedocs.io/)
3. If in queue, will check every 30 seconds to see if you are 
    - still in queue
    - if an error has occured
    - or if you are logged in
4. If error has occured, script will close FF14 and (if enabled) email you asking for a new MFA code, and will automatically log back in with that new MFA code
5. Will send email letting you know once you are fully logged in, or if something went wrong and script needed to close

How to install:

1. Install Python (Go here: https://www.python.org/downloads/)
2. Download this repo as a ZIP (link goes here)
3. Unzip anywhere
4. Fill out settings.ini:
    - If you want the script to email you, you will need to provide it with an email address it can login with in settings.ini:
        - Recommended: Create a new gmail account, turn on "less secure app access" for that account, then enter your email/password in the 'fromEmail' and 'from_email_password' fields in settings.ini, respectively
            - How to turn on "less secure app access": https://support.google.com/accounts/answer/6010255?hl=en#zippy=%2Cif-less-secure-app-access-is-off-for-your-account
        - You can leave the 'fromEmail' as queuewalker2121@gmail.com and that will probably work. However, this email could easily get suspended since anyone can see the email address / app password combo and start using it maliciously
        - I would recommended setting the 'toEmail' field to be your phone number's email address, that way you will get a text instantly if a lobby error occurs. If you don't know your phone number's email address, just send a text message from your phone to your normal email, and see what the From address is
        - 'toEmail' and 'fromEmail' can be the same email address, if desired
5. Run "run.bat". This will:
    - Open a command prompt window in the queuewalker folder directory
    - Install neccesary Python modules using pip
    - Start the queuewalker.py script

Limitations:
1. Must be using Windows PC
2. FF14 must be on active monitor and fully visible at all times
3. Launcher must have Square Enix ID already filled in and "Remember Square Enix ID" checked
4. While logging in, cannot use the computer (script uses mouse and keyboard to log in). This only lasts until you get to the "World is Full" message or you are logged in
5. Might have issues if screen DPI is not set to 100%
6. Might have issues if using a 4K monitor. Can't test since I don't have one


Contact: hypernova2121@gmail.com
Reddit: hypernova2121