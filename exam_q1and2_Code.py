import csv
import os

import pyperclip
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import actions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up ChromeDriver service
s = Service('/Users/urisegman/Downloads/chromedriver_mac_arm64/chromedriver')

# Set up Chrome options
chrome_options = Options()

# Add preferences to allow any popups that come up, mic and camera
chrome_options.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 1,     # 1:allow, 2:block
    "profile.default_content_setting_values.media_stream_camera": 1,  # 1:allow, 2:block
    "profile.default_content_setting_values.notifications": 1
})

##### Question 1 functions #####
def start_a_call(driver):
    '''
    Starts a call using the provided web driver.

    Parameters:
    driver (webdriver): An instance of a WebDriver from the Selenium WebDriver library.

    Returns:
    str: URL of the initiated call.

    Note: Ensure the correct driver for your browser is in your PATH.
    '''

    wait = WebDriverWait(driver, 20)

    driver.get('https://p2p.mirotalk.com/')

    # Click the "Join Room" button
    join_button = wait.until(EC.presence_of_element_located((By.ID, 'joinRoomButton')))
    join_button.click()
    # Wait for the prompt to show up
    input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.swal2-input')))
    time.sleep(2)
    input_box.send_keys('observer_user1')
    time.sleep(2)
    # second join call button opens call under the given name
    join_meeting_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.swal2-confirm')))
    time.sleep(2)

    join_meeting_button.click()
    # copy url
    # WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'p')))

    copy_url_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[text()="Copy URL"]')))
    time.sleep(2)  # Wait for 5 seconds so website loads

    copy_url_button.click()
    time.sleep(2)  # Wait for 2 seconds so paste is registered in memory

    call_url = pyperclip.paste()
    print(call_url, 'is the call url')
    try:
        close_button = driver.find_element(By.CSS_SELECTOR, 'button.swal2-cancel.swal2-styled.swal2-default-outline')
        close_button.click()

    except Exception:
        pass


    return call_url


def join_a_call(participants, call_url):
    '''
    Joins a call with multiple participants using provided Selenium WebDriver instances and a call URL.

    Parameters:
    participants (dict): A dictionary mapping participant names (str) to their corresponding
                         WebDriver instances. Each participant will join the call using their
                         respective WebDriver.
    call_url (str): The URL of the call to join.

    Behavior:
    For each participant, the function navigates to the call URL, waits for the input box to load,
    inputs the participant's name, waits for the join button to load, and then clicks it to join
    the meeting. There are hard-coded sleeps after getting the call URL and clicking the join button,
    which may need to be adjusted based on the page load time and specific web application behavior.

    Note: Ensure the correct driver for your browser is in your PATH.
    '''

    for participant_name, driver in participants.items():
        wait = WebDriverWait(driver, 30)
        driver.get(call_url)
        # enter participant name
        time.sleep(4)
        input_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.swal2-input')))
        input_box.send_keys(participant_name)

        # join meeting
        join_meeting_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.swal2-confirm')))

        join_meeting_button.click()

def confirm_participants(starter, participants: dict):
    '''
    Confirms the presence of participants in a video call.

    Parameters:
    - starter (WebDriver): The observer user's WebDriver instance.
    - participants (dict): A dictionary containing the names and WebDriver instances of the participants.

    Returns:
    - bool: True if all participants are present in the call, False otherwise.

    Description:
    This function takes the observer user's WebDriver instance, referred to as "starter," and a dictionary
    of participants. The participants dictionary maps the string names of the participants to their
    corresponding WebDriver instances. The function confirms the presence of participants in the video call.

    The function finds all elements on the page with the class name 'videoPeerName', which represents the
    participant names in the video call. It collects the names into a list and checks if each participant's
    name exists in the list. If any participant's name is missing, the function returns False; otherwise,
    it returns True.

    Note: Ensure the correct driver for your browser is in your PATH.
    '''
    # wait for participant to show up
    time.sleep(7)
    elements = starter.find_elements(By.CLASS_NAME, 'videoPeerName')
    participant_names = [element.text for element in elements]
    print('participants are ', participant_names)
    for participant_name in participants.keys():
        if not (participant_name in participant_names):
            return False
    return True


##### Question 2 functions #####
def open_chat_box(participants):
    '''this function goes through all the participants and opens their chat box for the start of the discussion'''
    for user_name, driver in participants:
        wait = WebDriverWait(driver, 20)
        move_mouse_in_circles(driver, 2)
        print(f'{user_name} is opening chat box')
        move_mouse_in_circles(driver, 2)
        button_element = wait.until(EC.presence_of_element_located((By.ID, "chatRoomBtn")))
        move_mouse_in_circles(driver, 2)
        button_element.click()


def start_discussion(participants: list[tuple], iterations):
    """
    Starts a discussion among participants in a live call by sending messages and reading the chat box.
    for each red message it calls the add_row function that records the message

    Args:
        participants (list[tuple]): A list of tuples representing the participants in the call.
        Each tuple contains the participant's driver name as a string and the driver instance.
        iterations (int): The number of iterations to perform the discussion process.

    Returns:
        None

    """
    if iterations <= 0:
        user_name, driver = participants[0]
        messages = driver.find_elements(By.CLASS_NAME, 'msg-text')
        messages = [message.text for message in messages]
        print('received messages: ', messages)
        for message in messages:
            message = message.split(',')
            add_row(message[1], user_name[-1], message[0])
            # add to csv what hasnt been read already
        add_row(user_name[-1],'none','end_of_test')
        return
    if not len(participants):
        return

    for user_name, driver in participants:
        wait = WebDriverWait(driver, 20)
        # to check if we need to chat if not open, we must toggle the icons to appear through mouse movements:

        # send message
        textarea_element = wait.until(EC.element_to_be_clickable((By.ID, 'msgerInput')))
        textarea_element.send_keys(f'Hello,{user_name[-1]}')
        textarea_element.send_keys(Keys.ENTER)
        time.sleep(2)
        # read messages
        messages = driver.find_elements(By.CLASS_NAME, 'msg-text')
        messages = [message.text for message in messages]
        for message in messages:
            message = message.split(',')
            add_row(message[1], user_name[-1], message[0])
            # add to csv what hasnt been read already

    start_discussion(participants, iterations-1)



def move_mouse_in_circles(driver, seconds):
    """
    Moves the mouse cursor in circles on the screen for the specified duration.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        seconds (int): The duration in seconds for which to move the mouse in circles.

    Returns:
        None

    """
    actions = ActionChains(driver)
    # Get the current timestamp
    start_time = time.time()
    # Move the mouse in circles for x seconds
    while time.time() - start_time < seconds:
        # Move the mouse in a circular pattern
        actions.move_by_offset(5, 0).perform()
        actions.move_by_offset(0, 5).perform()
        actions.move_by_offset(-5, 0).perform()
        actions.move_by_offset(0, -5).perform()


def add_row(sentby, readby, text):
    """
    Adds a new row to a CSV file with the provided data, only if it has not yet been recorded

    Args:
        sentby (str): The sender of the message.
        readby (str): The recipient of the message.
        text (str): The content of the message.

    Returns:
        None

    """

    headers = ['sentby', 'readby', 'message']
    data = [sentby, readby, text]
    file_path = 'chat_data.csv'

    file_exists = os.path.isfile(file_path)

    if not file_exists:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerow(data)
    else:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        if data not in rows:
            with open(file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(data)


def exam_main():
    '''
    This exam function has two parts:
    question 1 cretes a call, and adds participants using a dictionary where the key is the name it uses to sign in,
    and the value is the driver instance

    once a call has begun, it adds the participant one by one to the call.
    Then it uses the call starter participant to check that all the added participants are in the call using the name
    they signed in.

    If all the participants are accounted for, it prints out that all the participants have been accounted for.


    The second part of the function puts all the call participants into a list of tuples (user_name, driver_instance)
    it then opens the chat icon for each participant and sends messages and records them iterativeely recording
    for each message who sent it and who read it and the contents of the message in a csv for later analysis
    '''
    driver_starter = webdriver.Chrome(service=s, options=chrome_options)
    driver_user2 = webdriver.Chrome(service=s, options=chrome_options)
    participants_drivers = {'driver_user2':driver_user2} # here you can create as many participants as you would like
    # to add to the call

    call_url = start_a_call(driver_starter)
    # double try starting a call if fails
    if not call_url:
        # try again:
        driver_starter.quit()
        driver_starter = webdriver.Chrome(service=s, options=chrome_options)
        call_url = start_a_call(driver_starter)
    if not call_url:
        raise Exception('call failed to start twice, exiting')

    join_a_call(participants_drivers, call_url=call_url)
    if confirm_participants(driver_starter, participants_drivers):
        print('all users have entered the call!, end of q1')

    print('question2: starting chat')
    participants_drivers['starter_user1'] = driver_starter
    tuple_list_participants = list(participants_drivers.items())

    # for purpose of test remove old csv of chat data collection
    file_path = 'chat_data.csv'
    if os.path.exists(file_path):
        os.remove(file_path)
    open_chat_box(tuple_list_participants)
    start_discussion(tuple_list_participants, 3)

# run exam here
exam_main()