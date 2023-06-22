import csv
import os
import random

import pyperclip
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading

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




class MiroCall:
    def __init__(self, user_driver=None, user_name=None):
        self.initial_user_driver = user_driver if user_driver else webdriver.Chrome(service=s, options=chrome_options)
        self.user_name = user_name
        self.call_url = self.start_a_call()
        self.participants = [User(self.user_name, self.call_url,  self.initial_user_driver)]

    def add_participant(self, driver_to_add=None, username=None):
        '''Username and driver can be inputted, but not necessarily'''
        if not driver_to_add:
            driver_to_add = webdriver.Chrome(service=s, options=chrome_options)
        if not username:
            username = str(len(self.participants) + 1)

        self.join_a_call(driver_to_add, username)
        if self.confirm_participants(username):
            self.participants.append(User(username,self.call_url,driver_to_add))
        else:
            print(f'user not in call! failed adding user {username} to call')


    def start_a_call(self):
        '''
        Starts a call using the provided web driver.

        Parameters:
        driver (webdriver): An instance of a WebDriver from the Selenium WebDriver library.

        Returns:
        str: URL of the initiated call.

        Note: Ensure the correct driver for your browser is in your PATH.
        '''
        if not self.user_name:
            self.user_name = '1'
        driver = self.initial_user_driver
        wait = WebDriverWait(driver, 20)
        driver.get('https://p2p.mirotalk.com/')
        # Click the "Join Room" button
        join_button = wait.until(EC.presence_of_element_located((By.ID, 'joinRoomButton')))
        join_button.click()
        # Wait for the prompt to show up
        input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.swal2-input')))
        time.sleep(2)
        input_box.send_keys(self.user_name)
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


    def join_a_call(self, driver, participant_name):
        '''
        Joins a call with multiple participants using provided Selenium WebDriver instances and a call URL.

        Parameters:
        participant_name: string of participant
        driver: The driver of the participant
        '''

        wait = WebDriverWait(driver, 30)
        driver.get(self.call_url)
        # enter participant name
        time.sleep(4)
        input_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.swal2-input')))
        input_box.send_keys(participant_name)

        # join meeting
        join_meeting_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.swal2-confirm')))

        join_meeting_button.click()

    def confirm_participants(self, participant_name):
        '''
        Confirms the presence of participants in a video call.
        Parameters:
        - starter (WebDriver): The observer user's WebDriver instance.
        - participants: A specific participant to check.

        Returns:
        - bool: True if all participants are present in the call, False otherwise.
        '''
        # wait for participant to show up
        time.sleep(7) # must have
        elements = self.initial_user_driver.find_elements(By.CLASS_NAME, 'videoPeerName')
        participant_names = [element.text for element in elements]
        print('participants are ', participant_names)
        if not (participant_name in participant_names):
            return False
        return True


##### Question 2 functions #####
class User:
    def __init__(self, name, urlcall, driver=None):
        self.driver = driver if driver else webdriver.Chrome(service=s, options=chrome_options)
        self.name = name
        self.urlcall = urlcall
        self.open_chat_box() # did not find out a way to dynamically open it yet, didnt have time to find relevant html
        self.message_count = 0 # number of messages sent

    def move_mouse_in_circles(self, seconds=2):
        """
        Moves the mouse cursor in circles on the screen for the specified duration.
        Args:
            driver (WebDriver): The Selenium WebDriver instance.
            seconds (int): The duration in seconds for which to move the mouse in circles.
        Returns:
            None
        """
        actions = ActionChains(self.driver)
        # Get the current timestamp
        start_time = time.time()
        # Move the mouse in circles for x seconds
        while time.time() - start_time < seconds:
            # Move the mouse in a circular pattern
            actions.move_by_offset(5, 0).perform()
            actions.move_by_offset(0, 5).perform()
            actions.move_by_offset(-5, 0).perform()
            actions.move_by_offset(0, -5).perform()

    def open_chat_box(self):
        '''this function goes through all the participants and opens their chat box for the start of the discussion'''
        wait = WebDriverWait(self.driver, 20)
        self.move_mouse_in_circles(2)
        print(f'{self.name} is opening chat box')
        self.move_mouse_in_circles(2)
        button_element = wait.until(EC.presence_of_element_located((By.ID, "chatRoomBtn")))
        self.move_mouse_in_circles(2)
        button_element.click()

    def wait_for_message_and_reply(self):
        print(f"wait_for_message() in user {self.name}")
        if self.message_count == 3:
            print('read enough messages, sending killer message')
            wait = WebDriverWait(self.driver, 20)
            textarea_element = wait.until(EC.element_to_be_clickable((By.ID, 'msgerInput')))
            textarea_element.send_keys(f'-1')
            textarea_element.send_keys(Keys.ENTER)
            return

        time2wait = random.random()
        time.sleep(time2wait)
        self.read_messages()

    def read_messages(self):
        messages = self.driver.find_elements(By.CLASS_NAME, 'msg-text')
        messages = [message.text for message in messages]
        for message in messages:
            print(f'read message {message}')
            if message == '-1':
                return
            message = message.split(',')

            if message[1] == self.name:
                continue
            if self.add_row(message[1], self.name, message[0]):
                self.send_message()
            else:
                continue
        self.wait_for_message_and_reply()

    def send_message(self, specific_text='Hello'):
        print(f'user {self.name} sending message')
        wait = WebDriverWait(self.driver, 20)
        # send message
        textarea_element = wait.until(EC.element_to_be_clickable((By.ID, 'msgerInput')))
        textarea_element.send_keys(f'{specific_text}#{self.message_count},{self.name}')
        textarea_element.send_keys(Keys.ENTER)
        print(f"{self.name} sent message {specific_text}#{self.message_count}")
        self.message_count += 1
        self.wait_for_message_and_reply()



    @staticmethod
    def add_row(sentby, readby, text):
        """
        Adds a new row to a CSV file with the provided data, only if it has not yet been recorded

        Args:
            sentby (str): The sender of the message.
            readby (str): The recipient of the message.
            text (str): The content of the message.

        Returns:
            Bool: if message has been seen before
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
                return True
            return False




def exam_main():
    # q1
    call = MiroCall()
    call.add_participant()
    print(f'current confirmed participants in call is {len(call.participants)}')
    for par in call.participants:
        print(f'participant_name {par.name}')
    print(call.participants[0].name)
    print(call.participants[1].name)
    t1 = threading.Thread(target = call.participants[1].wait_for_message_and_reply)
    t2 = threading.Thread(target=call.participants[0].send_message)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # call.participants[0].wait_for_message_and_reply()

if __name__ == '__main__':
    exam_main()