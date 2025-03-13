from playwright.sync_api import sync_playwright

def take_debug_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch()
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
        page.screenshot(path='frontend_debug.png')
        
        # Click the new conversation button
        new_conv_button = page.locator('[data-testid="new-conversation-button"]')
        if new_conv_button.is_visible():
            print("New conversation button is visible")
            new_conv_button.click()
            page.wait_for_timeout(1000)
            page.screenshot(path='after_click_debug.png')
            
            # Check if dialog appears
            dialog = page.locator('[data-testid="bot-selection-dialog"]')
            if dialog.is_visible():
                print("Bot selection dialog is visible")
            else:
                print("Bot selection dialog is NOT visible")
                
            # Try to find any dialog
            any_dialog = page.locator('dialog')
            count = any_dialog.count()
            print(f"Found {count} dialog elements")
            
        else:
            print("New conversation button is NOT visible")
        
        browser.close()

if __name__ == "__main__":
    take_debug_screenshot()
