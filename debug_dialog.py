from playwright.sync_api import sync_playwright

def inspect_dialog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # Try multiple ports since Vite may use different ports
        connected = False
        for port in [5173, 5174, 5175, 5176, 5177, 5178]:
            try:
                url = f'http://localhost:{port}'
                print(f"Trying to connect to {url}")
                page.goto(url, timeout=5000)
                if page.query_selector('body'):
                    print(f"Successfully connected to {url}")
                    connected = True
                    break
            except Exception as e:
                print(f"Failed to connect to {url}: {str(e)}")
                continue
                
        if not connected:
            raise Exception("Could not connect to frontend service on any port")
        
        # Start the backend service
        import subprocess
        import time
        import os
        
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = "123"
        os.environ["DMX_API_KEY"] = "sk-mIf8Kh6Lq2TUjBfobaet7CeI4qUmeXBsD5Lq865zvWP5iteQ"
        
        # Start backend in a separate process
        backend_process = subprocess.Popen(
            ["python", "-m", "ttc_agent.chat_app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        time.sleep(5)
        
        # Click new conversation button
        new_conv_button = page.locator('[data-testid="new-conversation-button"]')
        if new_conv_button.is_visible():
            print("New conversation button is visible")
            new_conv_button.click()
            time.sleep(1)
            
            # Take screenshot
            page.screenshot(path='dialog_debug.png')
            
            # Inspect dialog elements
            dialog_elements = page.query_selector_all('dialog')
            print(f"Found {len(dialog_elements)} dialog elements")
            
            for i, dialog in enumerate(dialog_elements):
                print(f"Dialog {i+1}:")
                print(f"  Role: {dialog.get_attribute('role')}")
                print(f"  Class: {dialog.get_attribute('class')}")
                print(f"  Data-testid: {dialog.get_attribute('data-testid')}")
                
            # Check for any element with data-testid="bot-selection-dialog"
            bot_dialog = page.locator('[data-testid="bot-selection-dialog"]')
            if bot_dialog.count() > 0:
                print("Found bot-selection-dialog with data-testid")
            else:
                print("Could not find bot-selection-dialog with data-testid")
                
            # Try to find the dialog using different selectors
            selectors = [
                'dialog',
                '.fixed',
                '[role="dialog"]',
                '.dialog',
                '.modal'
            ]
            
            for selector in selectors:
                elements = page.locator(selector)
                count = elements.count()
                print(f"Selector '{selector}': found {count} elements")
        else:
            print("New conversation button is NOT visible")
        
        # Clean up
        backend_process.terminate()
        browser.close()

if __name__ == "__main__":
    inspect_dialog()
