import streamlit as st
import tempfile
from pathlib import Path
import shutil
import requests

# Dropbox file request link
REQUEST_LINK = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"
BROWSERLESS_API_KEY = st.secrets.get("BROWSERLESS_API_KEY", "2SivQ6I57t68zTh02a77f7d9efb9b2591c542419ebe6fefc8")

def upload_with_browserless(url: str, filepath: str, name: str, email: str):
    # Upload file to a public endpoint first (e.g., file.io) so browserless can access it
    with open(filepath, 'rb') as f:
        upload_response = requests.post('https://file.io', files={'file': f})
    if not upload_response.ok:
        raise RuntimeError("File upload to file.io failed")

    public_file_url = upload_response.json().get('link')

    puppeteer_script = f"""
    const puppeteer = require('puppeteer');
    const fs = require('fs');
    const https = require('https');

    function downloadFile(url, dest, cb) {{
      const file = fs.createWriteStream(dest);
      https.get(url, function(response) {{
        response.pipe(file);
        file.on('finish', function() {{
          file.close(cb);
        }});
      }}).on('error', function(err) {{
        console.error('Download error:', err);
      }});
    }}

    (async () => {{
      const browser = await puppeteer.launch();
      const page = await browser.newPage();
      await page.goto('{url}');

      const filePath = '/tmp/uploaded_file.pdf';
      await new Promise(resolve => downloadFile('{public_file_url}', filePath, resolve));

      const [fileChooser] = await Promise.all([
        page.waitForFileChooser(),
        page.click('input[type="file"]')
      ]);
      await fileChooser.accept([filePath]);

      await page.type('input[name="name"]', '{name}');
      await page.type('input[name="email"]', '{email}');
      await page.click('button[type="submit"]');

      await page.waitForSelector('text=Thank you');
      await browser.close();
    }})();
    """

    response = requests.post(
        "https://chrome.browserless.io/puppeteer",
        params={"token": BROWSERLESS_API_KEY},
        json={"code": puppeteer_script}
    )

    if not response.ok:
        raise RuntimeError(f"Browserless error: {response.text}")

# --- Streamlit UI ---
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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("Uploading via Browserless..."):
                upload_with_browserless(REQUEST_LINK, tmp_path, user_name, user_email)
            st.success("✅ File uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
