# import requests
#
# # Tronscan API URL for transaction details
# tronscan_api_url = "https://apilist.tronscanapi.com/api/transaction-info"
# tx_hash = "97bd76e99dd0fd26c4aad6f17189acdb9f3ca14d6b4cb12b1bb2d31f752a2a4b"
#
# try:
#     # Fetch transaction details from Tronscan
#     response = requests.get(f"{tronscan_api_url}?hash={tx_hash}")
#     response.raise_for_status()  # Raise an HTTPError for bad responses
#     transaction_data = response.json()
#
#     if "confirmed" in transaction_data and transaction_data["confirmed"]:
#         transaction_block = transaction_data.get("block", 0)
#
#         # Fetch latest block information
#         latest_block_url = "https://apilist.tronscan.org/api/block/latest"
#         latest_block_response = requests.get(latest_block_url)
#         latest_block_response.raise_for_status()
#         latest_block_data = latest_block_response.json()
#         latest_block_number = latest_block_data.get("number", 0)
#
#         if transaction_block and latest_block_number:
#             confirmations = latest_block_number - transaction_block
#             print(f"Transaction {tx_hash} has {confirmations} block confirmations.")
#         else:
#             print("Unable to calculate confirmations. Check transaction data.")
#     else:
#         print(f"Transaction {tx_hash} is not confirmed yet.")
# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# import json
#
# # Initialize WebDriver
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service)
#
# driver.get("https://vipdivision.payform.ru/authorize/login")
#
# time.sleep(15)  # Allow time for manual login if needed
#
# page = 1
#
# # Function to process each ID
# def process_id(order_id, results):
#     link = f"https://vipdivision.payform.ru/paylist/?filter_date_start=30.12.2024&filter_date_end=03.01.2025&filter_text=&filter_payment_type=&filter_payment_status=&filter=&id={order_id}&page={page}"
#
#     # Navigate to the generated link
#     driver.get(link)
#
#     # Click on the specific element
#     try:
#         target_row = driver.find_element(By.XPATH, '//tr[contains(@class, "payments-item-details")]')
#
#         # Locate all rows in the table body
#         tbody = driver.find_element(By.XPATH,
#                                     '/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[3]/div[1]/table/tbody')
#         all_rows = tbody.find_elements(By.TAG_NAME, 'tr')
#
#         # Find the index of the target row
#         target_index = all_rows.index(target_row)
#
#         # The number of rows above the target row is the index
#         rows_above_count = target_index
#         click_path = f"/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[3]/div[1]/table/tbody/tr[{rows_above_count + 1}]/td/div[3]/div/table/tbody/tr[2]/td[5]/a[1]"
#         element_to_click = driver.find_element(By.XPATH, click_path)
#         element_to_click.click()
#     except Exception as e:
#         print(f"Error clicking for ID {order_id}: {e}")
#         results.append({"id": order_id, "result": f"Error clicking: {e}"})
#         return False
#
#     # Copy the text after clicking
#     try:
#         text_element = driver.find_element(By.XPATH, '/html/body/div[8]/div/pre[3]')
#         extracted_text = text_element.text
#
#         # Append the result to the results list
#         results.append({"id": order_id, "result": extracted_text})
#         print(f"Extracted and saved text for ID {order_id}.")
#         print({"id": order_id, "result": extracted_text})
#         return True
#     except Exception as e:
#         print(f"Error extracting text for ID {order_id}: {e}")
#         results.append({"id": order_id, "result": f"Error extracting text: {e}"})
#         return False
#
# # Main Script
# try:
#     # Load IDs from id_list.txt
#     with open("id_list.txt", "r", encoding="utf-8") as file:
#         id_list = [line.strip() for line in file.readlines()]
#
#     results = []  # Store results for each processed ID
#
#     # Process each ID from the file
#     for order_id in id_list:
#         result = process_id(order_id, results)
#         while not result:
#             page += 1
#             result = process_id(order_id, results)
#
#     # Save results to a JSON file
#     with open("results.json", "w", encoding="utf-8") as file:
#         json.dump(results, file, ensure_ascii=False, indent=4)
#     print("Results saved to 'results.json'.")
#
# finally:
#     # Close the browser
#     driver.quit()

import json

file_path = "results.json"

# Чтение данных из файла
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Преобразование поля 'result' в массив
for item in data:
    if 'result' in item:
        item['result'] = json.loads(item['result'])

# Сохранение изменений обратно в файл
with open(file_path, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print("Файл успешно обновлён, поля 'result' заменены на массивы.")
