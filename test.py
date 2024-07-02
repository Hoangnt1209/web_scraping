import numpy as np
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
from selenium.webdriver.common.by import By
import pandas as pd 

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# chọn trình duyệt để crawl data
driver = webdriver.Chrome(options=chrome_options)
driver.get("D:/hoang/EXE101/WEB_SCRAPING/chromedriver.exe")

# mở link web cần crawl data
driver.get("https://gearvn.com/collections/laptop")
sleep(random.randint(5, 10))

# Click on the "See more" button iteratively (example loop)
wait = WebDriverWait(driver, 10)  # 10 seconds timeout

for i in range(1):  # Adjust the range based on how many times you want to click "See more"
    try:
        elems_more = driver.find_element(By.CSS_SELECTOR, '#load_more')
        driver.execute_script("arguments[0].scrollIntoView();", elems_more)
        sleep(random.randint(5, 10))
        driver.execute_script("arguments[0].click();", elems_more)
    except (NoSuchElementException, ElementNotInteractableException) as e:
        print(f"Error clicking 'See more': {e}")
        break  # Exit the loop if there's an error
    except ElementClickInterceptedException:
        print("Element was not clickable. Retrying...")
        continue  # Retry the loop if the click was intercepted

# Lấy link từng sản phẩm với tên của sản phẩm 
elems = driver.find_elements(By.CSS_SELECTOR, ".proloop-name [href]")
name = [elem.text for elem in elems]
link = [elem.get_attribute("href") for elem in elems]

# Lấy giá của sản phẩm 
elems_price = driver.find_elements(By.CSS_SELECTOR, ".proloop-price--highlight")
price = [elem.text for elem in elems_price]

# Tạo bảng với 3 cột đầu tiên
df1 = pd.DataFrame(list(zip(name, price, link)), columns=['Name', 'Price', 'Link'])
df1['index_'] = np.arange(1, len(df1) + 1)
print(df1)

# Hàm để lấy chi tiết sản phẩm từ trang chi tiết
def getDetailItems(link):
    driver.get(link)
    sleep(random.randint(5, 10))  # Đợi trang chi tiết tải

    # Lấy thông tin từ bảng
    details = []
    try:
        table = driver.find_element(By.ID, 'tblGeneralAttribute')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            attribute = cols[0].text.strip()
            value = cols[1].text.strip()
            details.append(f"{attribute}: {value}")
    except NoSuchElementException:
        details.append("No details available from table")
    
    # Lấy thông tin trước và sau phần tử hr
    try:
        content_class = driver.find_element(By.CLASS_NAME, 'product-desc-short')
        elements = content_class.find_elements(By.XPATH, './*')

        data_before_hr = []
        data_after_hr = []
        found_hr = False

        for elem in elements:
            if elem.tag_name == 'hr':
                found_hr = True
            elif elem.tag_name == 'p':
                if not found_hr:
                    data_before_hr.append(elem.text)
                else:
                    data_after_hr.append(elem.text)

        return ' | '.join(details), ' '.join(data_before_hr), ' '.join(data_after_hr)
    except NoSuchElementException:
        return ' | '.join(details), "No data before HR", "No data after HR"

# Duyệt qua từng link sản phẩm và lấy dữ liệu chi tiết
product_details = []
data_before_hr_list = []
data_after_hr_list = []

for lnk in link:
    details, data_before_hr, data_after_hr = getDetailItems(lnk)
    product_details.append(details)
    data_before_hr_list.append(data_before_hr)
    data_after_hr_list.append(data_after_hr)

# Thêm dữ liệu chi tiết vào df1
df1['Product_Details'] = product_details
df1['Data_Before_HR'] = data_before_hr_list
df1['Data_After_HR'] = data_after_hr_list

# In bảng df1 đã được cập nhật
print(df1)

# # Đóng trình duyệt
# driver.quit()
