import numpy as np
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,ElementNotInteractableException,ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
from selenium.webdriver.common.by import By
import pandas as pd 

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

#chọn trình duyệt để crawl data
driver = webdriver.Chrome(chrome_options)
driver.get("D:\hoang\EXE101\WEB_SCRAPING\chromedriver.exe")

# mở link web cần crawl data
driver.get("https://gearvn.com/collections/laptop")
sleep(random.randint(5,10))

# Click on the "See more" button iteratively (example loop)
wait = WebDriverWait(driver, 10)  # 10 seconds timeout

for i in range(4):  # Adjust the range based on how many times you want to click "See more"
    try:
        # Wait for the element to be clickable
        # elems_more = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#load_more")))

        elems_more = driver.find_element(By.CSS_SELECTOR, '#load_more')


        driver.execute_script("arguments[0].scrollIntoView();", elems_more)

        
          
        # Add a longer sleep to wait for content to load (adjust as needed)
        sleep(random.randint(5, 10))
        
        # Use JavaScript to click on the element
        driver.execute_script("arguments[0].click();", elems_more)
        
    except (NoSuchElementException, ElementNotInteractableException) as e:
        print(f"Error clicking 'See more': {e}")
        break  # Exit the loop if there's an error
    except ElementClickInterceptedException:
        print("Element was not clickable. Retrying...")
        continue  # Retry the loop if the click was intercepted
# lấy link từng sản phẩm với tên của sản phẩm 
elems = driver.find_elements(By.CSS_SELECTOR,".proloop-name [href]")
name = [elem.text for elem in elems]
link = [elem.get_attribute("href") for elem in elems]

# lấy giá của sản phẩm 
elems_price = driver.find_elements(By.CSS_SELECTOR,".proloop-price--highlight")
price = [elem.text for elem in elems_price]

#tạo table với 3 cột đầu trước tại xem video nên nó dị 


df1 = pd.DataFrame(list(zip(name, price, link)), columns = ['Name', 'Price','Link'])
df1['index_']= np.arange(1, len(df1) + 1)


discount_list, discount_idx, discount_percent_list = [], [], []
for i in range(1,len(name)+1):
    try:
        discount = driver.find_element("xpath", f"/html/body/div[1]/main/div/div[2]/div/div[2]/div[1]/div[2]/div/div[{i}]/div/div[2]/div[3]/div[1]/del")
        discount_list.append(discount.text)
        discount_percent = driver.find_element("xpath",f"/html/body/div[1]/main/div/div[2]/div/div[2]/div[1]/div[2]/div/div[{i}]/div/div[2]/div[3]/div[2]/span[2]")
        discount_percent_list.append(discount_percent.text)
        print(i)
        discount_idx.append(i)
    except NoSuchElementException:
        print("No Such Element Exception " + str(i))
df2 = pd.DataFrame(list(zip(discount_idx , discount_list, discount_percent_list)), columns = ['discount_idx', 'discount_list','discount_percent_list'])


df_merged = df1.merge(df2, how='left', left_on='index_', right_on='discount_idx')


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
    
    # Lấy toàn bộ thông tin trong product-desc-short prtab2
    try:
        Gift_gurantee = []
        shortdb_class = driver.find_element(By.CSS_SELECTOR, '.product-desc-short.prtab2')
        elements = shortdb_class.find_elements(By.XPATH, './*')
        for element in elements:
            Gift_gurantee.append(element.text + "\n")
    except NoSuchElementException:
        Gift_gurantee.append("No details available from gift and gurantee")

    return '\n'.join(details), '\n'.join(Gift_gurantee)

# Duyệt qua từng link sản phẩm và lấy dữ liệu chi tiết
product_details = []
gift_gurantee_list = []

for lnk in link:
    details, gift_gurantee = getDetailItems(lnk)
    product_details.append(details)
    gift_gurantee_list.append(gift_gurantee)

# Chuyển đổi danh sách chi tiết sản phẩm và gift/gurantee thành DataFrame
df3 = pd.DataFrame(list(zip(product_details, gift_gurantee_list)), columns=['Product_Details', 'Gift_Gurantee'])
df3['index_'] = np.arange(1, len(df3) + 1)

df_final = df_merged.merge(df3, how='left', left_on='index_', right_on='index_')
df_final.drop(columns=['index_', 'discount_idx'], inplace=True)
print(df_final)

df_final.to_excel("merged_data.xlsx", index=False)
