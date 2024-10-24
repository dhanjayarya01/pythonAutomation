import re
import sys
import time
import keyboard  
import pyperclip  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import Select
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, 
                             QPushButton, QLineEdit, QMessageBox, QFormLayout, 
                             QScrollArea, QGroupBox, QStyleFactory)

import re

def read_user_info(file_path):
    user_info = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file: 
            for line in file:
                key, value = line.strip().split(':', 1)
               
                key = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', key.strip().lower())  
                user_info[key] = value.strip() 
               
        
        for key in user_info.keys():
            if key not in ALTERNATIVE_LABELS:
                
                ALTERNATIVE_LABELS[key] = []
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please check the file path.")
        exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")
        exit(1)
    return user_info





ALTERNATIVE_LABELS = {
    "name": ["username","accountname","new_username","enterfirstname","fullname", "nameofapplicant", "name","firstname", "nameofcandidate", "applicantname", "applicant'sname"],
    "lastname":[],
    "आवेदिकाकानाम":["आवेदकआवेदिकाकानाम"],
    "email": ["email", "emailorphonenumber", "emailaddress", "useremail", "emailid", "emailofapplicant", "emailaddress"],
    "confirmemail":[],
    "phone": ["phone", "mobileno.ofapplicant","emailorphonenumber", "mobileno","mobile", "contactnumber", "phonenumber", "mobilenumber", "applicantmobile"],
    "password": ["password","passcode", "pwd", "userpassword", "securitypassword"],
    "confirmpassword":[],
    "fathersname": ["fathername", "father'sname", "nameoffather", "fathersfullname", "father'sfull_name"],
    "पिताकानाम":[],
    "mothersname": ["mothername", "mother'sname", "nameofmother", "mothersfullname", "mother'sfull_name"],
    "माताकानाम":[],
    "address": ["address","पताaddress", "homeaddress", "residentialaddress", "addressline", "applicantaddress"],
    "village":["ग्रामvillageमोहल्लाtown","ग्रामvillage","मोहल्लाtown"],
    "block":["प्रखंडblock","प्रखंड","block"],
    "district":["जिला","जिलाdistrict","district"],
    "subdivision":["अनुमंडल","अनुमंडलsubdivision","subdivision"],
    "postoffice":["डाकघर","डाकघरpostoffice","postoffice"],
    "policestation":["थाना","थानाpolicestation","policestation"],
    "pincode":["पिनकोड","पिनकोडpincode","zipcode"],
    "city": ["city", "town", "localcity", "applicantcity", "cityname", "townname"],
    "state": ["state","राज्यstate", "राज्य","statename", "applicantstate", "applicant'sstate"],
    "district":["district","जिलाDistrict","जिला"],
    "aadhaar": ["आधारसंख्याaadhaarnumber","aadhaarno", "aadhaarcard", "aadhaarcardnumber", "aadhar"],
    "country": ["country", "countryname", "nation", "applicantcountry", "applicant'scountry"],
    "wardno":["वार्डसंख्याwardno","Wardno","वार्डसंख्या"]
}





def match_label_to_key(label_text):
    label_text = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', label_text.strip().lower())
    for key, alternatives in ALTERNATIVE_LABELS.items():
        if label_text == key or label_text in alternatives:
            return key
    return None



def fill_input_fields(driver, user_info, matched_key, input_element):
    try:
        input_type = input_element.get_attribute("type")
        time.sleep(0.2)
        if input_type in ["text", "email", "tel", "password"]:
            input_element.clear()
            time.sleep(0.1)
            input_element.send_keys(user_info[matched_key])  
            time.sleep(0.2)
    except:
        pass
     


def find_input_element(driver, identifier):
    
    try:
        return driver.find_element(By.ID, identifier)
    except NoSuchElementException:
        pass

    
    try:
        return driver.find_element(By.CLASS_NAME, identifier)
    except NoSuchElementException:
        pass

    
    try:
        return driver.find_element(By.NAME, identifier)
    except NoSuchElementException:
        pass

    
    try:
        return driver.find_element(By.XPATH, f"//input[@placeholder='{identifier}']")
    except NoSuchElementException:
        pass

    
    try:
        return driver.find_element(By.XPATH, f"//input[@data-type='{identifier}']")
    except NoSuchElementException:
        pass

    return None  




def fill_form(url):

    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    info_file_path = os.path.join(desktop_path, "info.txt")
    user_info = read_user_info(info_file_path)  
    filled_fields = set()  

    driver = webdriver.Chrome() 

    try:
    
        driver.get(url)  

        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        except WebDriverException:
            print("Timeout waiting for page to load.")
            return



        def print_input_placeholders(driver):
            input_fields = driver.find_elements(By.TAG_NAME, "input")  
            print("Detected input fields and their placeholders:")
            
            for input_field in input_fields:
                placeholder = input_field.get_attribute("placeholder")
                field_type = input_field.get_attribute("type")
                data_type = input_field.get_attribute("data-type")
                input_name = input_field.get_attribute("name")
                
                matched_key = None
                matched_fields = None
                
                if input_name:
                    input_name = input_name.strip()
                    matched_key = match_label_to_key(input_name)
                    if matched_key:
                        matched_fields = input_name
                        

                
                if placeholder:
                    placeholder = placeholder.strip()
                    matched_key = match_label_to_key(placeholder)
                    if matched_key:
                        matched_fields = placeholder

                
                
                if not matched_key:
                    field_type = field_type.strip()
                    matched_key = match_label_to_key(field_type)
                    if matched_key:
                        matched_fields = field_type
                
                
                if not matched_key and data_type:
                    data_type = data_type.strip()
                    matched_key = match_label_to_key(data_type)
                    if matched_key:
                        matched_fields = data_type
                
                
                if matched_key and matched_key in user_info and matched_key not in filled_fields:
                    
                    input_element = find_input_element(driver, matched_fields)
                    

                    if input_element:

                        try:
                            input_element.send_keys(user_info[matched_key]) 
                            filled_fields.add(matched_key)
                        except WebDriverException:
                            print(f"Element not interactable for {matched_key}")
                    else:
                        pass




        

        labels = driver.find_elements(By.TAG_NAME, "label")

        for label in labels:
            label_text = label.text.strip()
            matched_key = match_label_to_key(label_text)  
    

            if matched_key and matched_key in user_info and matched_key not in filled_fields:  
                input_id = label.get_attribute("for")
                if input_id:
                    input_element = find_input_element(driver, input_id)
                    if input_element:
                        fill_input_fields(driver, user_info, matched_key, input_element)
                        filled_fields.add(matched_key)  
        
        print_input_placeholders(driver)


        
        
        while True:
            time.sleep(1)  
            try:
                if not driver.window_handles:  
                    print("Browser closed. Ready to listen for new URL...")
                    break
            except WebDriverException:
                print("Driver disconnected. Exiting.")
                break

    finally:
        driver.quit()  

# Set a custom style for the application
def set_style():
    app.setStyle(QStyleFactory.create('Fusion'))
    # Customize the application palette
    palette = app.palette()
    palette.setColor(palette.Window, Qt.white)
    palette.setColor(palette.WindowText, Qt.black)
    palette.setColor(palette.Button, Qt.lightGray)
    palette.setColor(palette.ButtonText, Qt.black)
    app.setPalette(palette)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Info Application")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout()
        
        self.welcome_label = QLabel("Welcome! Please choose an option:")
        self.welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.welcome_label)

        self.setinfo_button = QPushButton("Set Info")
        self.setinfo_button.setStyleSheet("font-size: 16px;")
        self.setinfo_button.clicked.connect(self.show_setinfo_form)
        layout.addWidget(self.setinfo_button)

        self.fillform_button = QPushButton("Fill Form")
        self.fillform_button.setStyleSheet("font-size: 16px;")
        self.fillform_button.clicked.connect(self.show_fillform)
        layout.addWidget(self.fillform_button)

        self.setLayout(layout)

    def show_setinfo_form(self):
        self.set_info_window = SetInfoWindow()
        self.set_info_window.show()

    def show_fillform(self):
        self.fill_form_window = FillFormWindow()
        self.fill_form_window.show()

class SetInfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Set User Info")
        self.setGeometry(150, 150, 400, 500)
        self.setStyleSheet("background-color: #ffffff;")

        layout = QVBoxLayout()

        # Create a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QFormLayout(self.scroll_content)

        self.info_fields = {}

        initial_fields = {
            "Name": QLineEdit(),
            "आवेदिकाकानाम": QLineEdit(),
            "Email": QLineEdit(),
            "Phone": QLineEdit(),
            "Password": QLineEdit(),
            "Father's Name": QLineEdit(),
            "पिताकानाम": QLineEdit(),
            "Mother's Name": QLineEdit(),
            "माताकानाम": QLineEdit(),
            "Address": QLineEdit(),
            "Village": QLineEdit(),
            "Block": QLineEdit(),
            "District": QLineEdit(),
            "Subdivision": QLineEdit(),
            "Post Office": QLineEdit(),
            "Police Station": QLineEdit(),
            "Pincode": QLineEdit(),
            "City": QLineEdit(),
            "State": QLineEdit(),
            "Country": QLineEdit(),
            "Aadhaar": QLineEdit(),
            "Ward No": QLineEdit(),
        }

        for label, line_edit in initial_fields.items():
            line_edit.setStyleSheet("padding: 5px; font-size: 14px;")
            self.scroll_layout.addRow(QLabel(label), line_edit)
            self.info_fields[label] = line_edit

        self.add_field_button = QPushButton("Add More Field")
        self.add_field_button.clicked.connect(self.add_more_field)
        self.scroll_layout.addRow(self.add_field_button)

        self.submit_button = QPushButton("Save Info")
        self.submit_button.clicked.connect(self.save_info)
        self.scroll_layout.addRow(self.submit_button)

        # Set the layout of the scroll content and add it to the scroll area
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def add_more_field(self):
        field_name_input = QLineEdit()
        field_name_input.setPlaceholderText("Enter field name")
        
        field_value_input = QLineEdit()
        
        self.scroll_layout.addRow(field_name_input, field_value_input)

        field_name_input.editingFinished.connect(lambda: self.update_field(field_name_input.text(), field_value_input))

    def update_field(self, field_name, field_value_input):
        if field_name:
            self.info_fields[field_name] = field_value_input  

    def save_info(self):
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        info_file_path = os.path.join(desktop_path, "info.txt")

        if not os.path.exists(info_file_path):
            with open(info_file_path, "w") as file:
                pass
        time.sleep(0.5)

        with open(info_file_path, 'w', encoding='utf-8') as f:
            for key, line_edit in self.info_fields.items():
                if line_edit.text():  
                    f.write(f"{key}: {line_edit.text()}\n")

        QMessageBox.information(self, "Success", "User info saved successfully!")
        self.close()

class FillFormWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fill Form")
        self.setGeometry(150, 150, 400, 200)
        self.setStyleSheet("background-color: #ffffff;")

        layout = QVBoxLayout()
        self.instruction_label = QLabel("Copy the URL of the webpage you want to fill from, then press Ctrl + Alt.")
        layout.addWidget(self.instruction_label)
        
        self.run_script_button = QPushButton("Start Listening...")
        self.run_script_button.clicked.connect(self.start_listening)
        layout.addWidget(self.run_script_button)

        self.setLayout(layout)

    def start_listening(self):
        print("Listening for Ctrl + Alt to fill the form...")
        while True:
            if keyboard.is_pressed('ctrl+alt'):
                url = pyperclip.paste()  
                if url:
                    fill_form(url)
                    break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())