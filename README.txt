In order to run this code you must download chromium driver.
if you havent download the chromium driver: do so on this link https://sites.google.com/chromium.org/driver/downloads

This code runs an automation on the Chrome browser
The function to run is called exam() and it answers the first two sections together.


This exam function has two parts:
question 1 creates a videocall, and adds participants using a dictionary where the key is the name it uses to sign
in,
and the value is the driver instance

once a call has begun, it adds the participant one by one to the call.
Then it uses the call starter participant to check that all the added participants are in the call using the name
they signed in.

If all the participants are accounted for, it prints out that all the participants have been accounted for.


The second part of the function puts all the call participants into a list of tuples (user_name, driver_instance)
it then opens the chat icon for each participant and sends messages and records them iterativeely recording
for each message who sent it and who read it and the contents of the message in a csv for later analysis

If you want to run the test on 3 callers or more we can do so by adding them to the dictionary,
we can run x itterations of message sending using the itteration argument in the start_discussion function