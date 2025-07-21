
import streamlit as st
import tempfile
from pathlib import Path
import shutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

REQUEST_LINK = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"

def upload_with_selenium(url: str, filepath: str, name: str, email: str):
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    chrome_path = "/usr/bin/google-chrome"
    driver = uc.Chrome(options=options, browser_executable_path=chrome_path)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url)

        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
        file_input.send_keys(filepath)

        name_input = driver.find_element(By.NAME, "name")
        email_input = driver.find_element(By.NAME, "email")
        name_input.send_keys(name)
        email_input.send_keys(email)

        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Thank you')]")))

    finally:
        driver.quit()

st.set_page_config(page_title="Upload File to Dropbox")
st.title("📂 Upload File to Dropbox File Request")

user_name = st.text_input("Your Name")
user_email = st.text_input("Your Email")
uploaded_file = st.file_uploader("Choose a file to upload")

if st.button("Upload"):
    if not uploaded_file:
        st.error("❗ Please choose a file to upload.")
    elif not user_name or not user_email:
        st.error("❗ Please enter both your name and email.")
    else:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("Launching browser and uploading..."):
                upload_with_selenium(REQUEST_LINK, tmp_path, user_name, user_email)
            st.success("✅ File uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
