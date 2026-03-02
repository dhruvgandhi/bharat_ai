import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://niimh.nic.in/ebooks/ecaraka/?mod=read"

# Setup driver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

driver.get(URL)

data = []

# Wait for dropdown
wait.until(EC.presence_of_element_located((By.NAME, "selAdhi")))
select_element = driver.find_element(By.NAME, "selAdhi")
select = Select(select_element)

total_options = len(select.options)

print(f"Total options found: {total_options}")

for i in range(1, total_options-2):  # skip index 0 if placeholder
    try:
        # Refresh select element each loop (important after DOM updates)
        select_element = driver.find_element(By.NAME, "selAdhi")
        select = Select(select_element)

        group_text = select.options[i].text.strip()
        print(f"Processing: {group_text}")

        select.select_by_index(i)

        # Wait for page content to load
        time.sleep(2)

        # MAIN BODY TABLE
        main_table = driver.find_element(By.XPATH, "//body//table//table")
        tbody = main_table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        # Ensure minimum rows exist
        if len(rows) < 5:
            print(f"Skipped {group_text} (Not enough rows)")
            continue

        # --------------------
        # SHLOK (4th TR)
        # --------------------
        shlok_tr = rows[3]
        
        shlok_td = shlok_tr.find_element(By.TAG_NAME, "td")

        inner_table = shlok_td.find_element(By.TAG_NAME, "table")
        inner_tr = inner_table.find_element(By.TAG_NAME, "tr")
        inner_td = inner_tr.find_element(By.TAG_NAME, "td")

        spans = inner_td.find_elements(By.TAG_NAME, "span")
        shlok_text = " ".join(
            [s.text.strip() for s in spans if s.text.strip()]
        )

        if not shlok_text:
            print(f"Skipped {group_text} (Empty shlok)")
            continue

        # --------------------
        # DESCRIPTION (5th TR)
        # --------------------
        
        #rows = tbody.find_elements(By.TAG_NAME, "tr")
        desc_tr = rows[5]
        desc_td = desc_tr.find_element(By.TAG_NAME, "td")
        
        #print(f"found {desc_td.text} td div for {group_text}, removing it")

        # Remove heading div if exists
        try:
            heading_div = desc_td.find_element(By.ID, "sthAdhTitle")
            #print(f"found {heading_div.text} heading div for {group_text}, removing it")
            driver.execute_script("""
                var element = arguments[0];
                element.parentNode.removeChild(element);
            """, heading_div)
        except:
            #print(f"No heading div to remove for {group_text}" )
            pass
        
        desc_spans = desc_td.find_elements(By.TAG_NAME, "span")
        print(f"Found {len(desc_spans)} description spans for {group_text}")
        desc_text = " ".join(
            [s.text.strip() for s in desc_spans if s.text.strip()]
        )

        data.append({
            "group": group_text,
            "shlok": shlok_text,
            "description": desc_text
        })

        print(f"Saved: {group_text}")

    except Exception as e:
        print(f"Skipped {group_text} due to error:", e)
        continue


# Save JSON
with open("charaka_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Scraping completed. Saved to charaka_data.json")

driver.quit()