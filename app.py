import requests
import streamlit as st

# --- CONFIG ---
BROWSERLESS_API_KEY = st.secrets.get("BROWSERLESS_API_KEY", "2SivQ6I57t68zTh02a77f7d9efb9b2591c542419ebe6fefc8")
DROPBOX_REQUEST_LINK = "https://www.dropbox.com/request/tydarVR6Ty4qZEwGGTPd"

st.set_page_config(page_title="Automated Dropbox Upload")
st.title("📤 Automate File Upload to Dropbox (via Browserless)")

# --- UI ---
name = st.text_input("Your Name")
email = st.text_input("Your Email")
public_file_url = st.text_input("Public File URL to Upload (e.g., Dropbox, S3, GitHub)")

if st.button("Upload File Automatically"):
    if not name or not email or not public_file_url:
        st.error("Please fill in all fields.")
    else:
        # Puppeteer script to run in Browserless
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
          await page.goto('{DROPBOX_REQUEST_LINK}');

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

        # Send to Browserless
        with st.spinner("Uploading via Browserless Chrome..."):
            response = requests.post(
                "https://chrome.browserless.io/puppeteer",
                params={"token": BROWSERLESS_API_KEY},
                json={"code": puppeteer_script}
            )

        if response.ok:
            st.success("✅ Upload completed successfully!")
            st.code(response.text)
        else:
            st.error(f"❌ Upload failed. Status: {response.status_code}")
            st.code(response.text)
