import requests

url = "http://127.0.0.1:8001/tpdf/generate/409f05934Rtyh"
headers = {"Content-Type": "application/json"}
data = {"data": [{"lastname": "artem"}]}

response = requests.post(url, json=data, headers=headers)

# Проверка, что запрос прошел успешно
if response.status_code == 200:
    with open("certificate_409f05934Rtyh.pdf", "wb") as f:
        f.write(response.content)
    print("PDF файл сохранен как certificate_409f05934Rtyh.pdf")
else:
    print(f"Ошибка: {response.status_code}")
    print(response.json())
