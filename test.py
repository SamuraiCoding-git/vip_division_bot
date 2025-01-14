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
import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time
#
# # Initialize WebDriver
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service)
#
# driver.get("https://vipdivision.payform.ru/authorize/login")
#
# time.sleep(15)
#
# # Function to process each ID
# def process_id(order_id, results):
#     link = f"https://vipdivision.payform.ru/paylist/?&id={order_id}&page=1"
#
#     # Navigate to the generated link
#     driver.get(link)
#
#     # Click on the specific element
#     try:
#         element_to_click = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[3]/div[1]/table/tbody/tr[2]/td/div[3]/div/table/tbody/tr[2]/td[5]/a[1]')
#         element_to_click.click()
#         time.sleep(2)  # Wait for the new content to load after click
#     except Exception as e:
#         print(f"Error clicking for ID {order_id}: {e}")
#         results.append({"id": order_id, "result": f"Error clicking: {e}"})
#         return
#
#     # Copy the text after clicking
#     try:
#         text_element = driver.find_element(By.XPATH, '/html/body/div[9]/div/pre[2]')
#         extracted_text = text_element.text
#
#         # Append the result to the results list
#         results.append({"id": order_id, "result": extracted_text})
#         print(f"Extracted and saved text for ID {order_id}.")
#     except Exception as e:
#         print(f"Error extracting text for ID {order_id}: {e}")
#         results.append({"id": order_id, "result": f"Error extracting text: {e}"})
#         return
#
# # Main Script
# try:
#     base_url = "https://vipdivision.payform.ru/paylist/?&&page="
#     total_pages = 1  # Adjust the total number of pages as needed
#     results = []  # Store results for each processed ID
#
#     for page in range(1, total_pages + 1):
#         # Open the page
#         page_url = f"{base_url}{page}"
#         driver.get(page_url)
#         print(f"Processing IDs on page: {page}")
#
#         # Wait for the page to load
#         time.sleep(2)
#
#         # Collect IDs from the page
#         tbody = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[3]/div[1]/table/tbody')
#         rows = tbody.find_elements(By.TAG_NAME, 'tr')
#         id_list = [row.get_attribute('id') for row in rows if row.get_attribute('id')]
#         print(id_list)
#
#         # # Process each ID
#         # for order_id in id_list:
#         #     process_id(order_id, results)
#
#         print(f"Completed processing page {page}")
#
#     # # Save results to a JSON file
#     # import json
#     # with open("results.json", "w", encoding="utf-8") as file:
#     #     json.dump(results, file, ensure_ascii=False, indent=4)
#     # print("Results saved to 'results.json'.")
#
# finally:
#     # Close the browser
#     driver.quit()

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
#     link = f"https://vipdivision.payform.ru/paylist/?filter_date_start=03.01.2025&filter_date_end=03.01.2025&filter_text=&filter_payment_type=&filter_payment_status=&filter=&id={order_id}&page={page}"
#
#     # Navigate to the generated link
#     driver.get(link)
#
#     # Click on the specific element
#     try:
#         target_row = driver.find_element(By.XPATH, '//tr[contains(@class, "payments-item-details")]')
#
#         # Locate all rows in the table body
#         tbody = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[3]/div[1]/table/tbody')
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

# import json
#
# file_path = "results.json"
#
# # Чтение данных из файла
# with open(file_path, "r", encoding="utf-8") as file:
#     data = json.load(file)
#
# # Преобразование поля 'result' в массив
# for item in data:
#     if 'result' in item:
#         try:
#             item['result'] = json.loads(item['result'])
#         except:
#             pass
#
# # Сохранение изменений обратно в файл
# with open(file_path, "w", encoding="utf-8") as file:
#     json.dump(data, file, indent=4, ensure_ascii=False)
#
# print("Файл успешно обновлён, поля 'result' заменены на массивы.")
import csv
import psycopg2
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="2727",
        host="92.119.114.185",
        port="5432"
    )

def parse_date(date_str):
    """
    Преобразует дату из формата DD.MM.YYYY HH:MI:SS или DD.MM.YYYY HH:MI в формат YYYY-MM-DD HH:MI:SS.
    """
    for date_format in ["%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"]:
        try:
            return datetime.strptime(date_str, date_format).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    print(f"Некорректный формат даты: {date_str}")
    return None

def insert_users(cursor, user_id, full_name, username):
    cursor.execute(
        """
        INSERT INTO users (id, full_name, username)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """,
        (user_id, full_name, username)
    )

def insert_orders(cursor, user_id, start_date):
    plan_id = 1

    is_paid = True

    if start_date is not None:
        cursor.execute(
            """
            INSERT INTO orders (user_id, start_date, plan_id, total_price, is_paid)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET start_date = EXCLUDED.start_date;
            """,
            (user_id, start_date, plan_id, 1390, is_paid)
        )

def process_csv(file_path):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                with open(file_path, mode='r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)  # Используем DictReader

                    for row in reader:
                        # DictReader возвращает строки как словари
                        user_id = row['user_id']
                        full_name = row['Пользователь']
                        username = row['Юзернейм']
                        raw_date = row['Дата оплаты']

                        # Преобразуем дату
                        start_date = parse_date(raw_date)

                        # Проверяем наличие обязательных данных
                        if not user_id:
                            print(f"Пропущенные данные в строке: {row}")
                            continue

                        # Вставка данных в таблицу users
                        insert_users(cursor, user_id, full_name, username)

                conn.commit()  # Сохраняем изменения в базе данных
                print("Данные успешно загружены.")
            except Exception as e:
                conn.rollback()  # Откатить изменения при ошибке
                print(f"Ошибка при обработке файла: {e}")

if __name__ == "__main__":
    csv_file_path = "product_payments.csv"  # Укажите путь к вашему CSV-файлу
    process_csv(csv_file_path)


# import csv
#
#
# def remove_unused_columns(input_csv, output_csv, required_columns):
#     """
#     Удаляет неиспользуемые столбцы из CSV-файла.
#
#     :param input_csv: Путь к исходному CSV-файлу.
#     :param output_csv: Путь к новому CSV-файлу с выбранными столбцами.
#     :param required_columns: Список необходимых столбцов.
#     """
#     with open(input_csv, mode='r', encoding='utf-8') as infile, open(output_csv, mode='w', encoding='utf-8',
#                                                                      newline='') as outfile:
#         reader = csv.DictReader(infile)
#         # Проверяем, что все необходимые столбцы присутствуют в исходном файле
#         missing_columns = [col for col in required_columns if col not in reader.fieldnames]
#         if missing_columns:
#             raise ValueError(f"Входной CSV-файл не содержит следующих столбцов: {', '.join(missing_columns)}")
#
#         # Создаем writer только с нужными столбцами
#         writer = csv.DictWriter(outfile, fieldnames=required_columns)
#         writer.writeheader()
#
#         for row in reader:
#             # Оставляем только необходимые столбцы
#             filtered_row = {col: row[col] for col in required_columns}
#             writer.writerow(filtered_row)
#
#
# if __name__ == "__main__":
#     # Укажите пути к входному и выходному файлу
#     input_csv_path = "subs.csv"  # Путь к исходному CSV
#     output_csv_path = "filtered_data.csv"  # Путь к новому CSV
#     # Укажите столбцы, которые нужно оставить
#     columns_to_keep = ["user_id", "Пользователь", "Юзернейм", "Категория", "Вход"]
#
#     remove_unused_columns(input_csv_path, output_csv_path, columns_to_keep)
#     print(f"Новый CSV-файл создан: {output_csv_path}")
# import csv
#
#
# def clean_csv(input_csv, output_csv):
#     """
#     Обрабатывает CSV-файл, удаляя запятые из колонки 'Категория' и делая 'Юзернейм' NULL, если он содержит дефис или запятые.
#
#     :param input_csv: Путь к исходному CSV-файлу.
#     :param output_csv: Путь к новому CSV-файлу с обработанными данными.
#     """
#     with open(input_csv, mode='r', encoding='utf-8') as infile, open(output_csv, mode='w', encoding='utf-8',
#                                                                      newline='') as outfile:
#         reader = csv.DictReader(infile)
#         fieldnames = reader.fieldnames
#         writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#
#         # Записываем заголовки
#         writer.writeheader()
#
#         for row in reader:
#             # Убираем запятые из категории
#             row['Категория'] = row['Категория'].replace(',', '')
#
#             # Проверяем 'Юзернейм'
#             if '—' in row['Юзернейм'] or ',' in row['Юзернейм']:
#                 row['Юзернейм'] = None
#
#             # Записываем обработанную строку
#             writer.writerow(row)
#
#
# if __name__ == "__main__":
#     input_csv_path = "filtered_data.csv"  # Укажите путь к исходному CSV-файлу
#     output_csv_path = "cleaned_data.csv"  # Путь к обработанному CSV-файлу
#     clean_csv(input_csv_path, output_csv_path)
#     print(f"Файл успешно обработан и сохранён: {output_csv_path}")

