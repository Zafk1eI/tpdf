# Документация

Модуль предназначен для генерации pdf сертификатов

## Endpoints

### Создание директории для работы с шаблоном

```
Endpoint: "/tpdf/create_directory/<string:certificate_id>"
Method: "POST"
```

*Params:*

`certificate_id`: используется для доступа к директории, а также индентификации шаблона

*headers:* `"Content-Type": "multipart/form-data"`

*Request body:*

```json
{
"file": "Pdf-файл, представляющий шаблон сертификата"
}
```

**Описание:** Этот эндпоинт используется для создания директории, необходимой для работы с шаблоном сертификата. Директория создается на основе переданного `certificate_id`. В эту директорию загружается .pdf и создается fields.json с данными о полях.

**Response**

* status: `200 OK`

    * Всё ОК. Директория была создана
    ```json
    {
        "message": "Upload seccessfully"
    }
    ```

* status `400 BAD REQUEST`

    * Нет ключа `'file'`
    ```json
    {
        "error": "No file"
    }
    ``` 
    * Не поддерживаемый формат (не pdf)
    ```json
    {
        "error": "File type not allowed"
    }
    ```
    * Сертификат с таким id уже существует
    ```json
    {
        "error": "dir exist"
    }
    ```

---

### Позиционирование полей (positioning.html)

```
Endpoint: "/tpdf/positioning/<string:certificate_id>"
Method: "GET"
```

*Params:* 

`certificate_id`: используется для доступа к директории, а также индентификации шаблона

**Описание:** Этот эндпоинт используется для позиционирование полей и изменения их размера. Это html cтраница, где пользователь размещает поля на шаблоне.

---

### Предпросмотр шаблона с данными

```
Endpoint: "/tpdf/example/<certificate_id>"
Method: "GET"
```

*Params:* 
`certificate_id`: используется для доступа к директории, а также индентификации шаблона

**Описание**: Дает возможность посмотреть на готовый сертификат с таким набором данных: 
```json
{
    "data": {
        "full_name": "Иван Иванов",
        "event_title": "Чемпионат по программированию",
        "stage": "Финал",
        "team_name": "Команда А",
        "organization_name": "ООО Программирование",
        "end_date": "2024-12-31"
    }
}
```

---

### Генерация одного сертификата

```
Endpoint: "/tpdf/generate/<certificate_id>"
Method: "POST"
```

*Params:* 
`certificate_id`: используется для доступа к директории, а также индентификации шаблона

*Headers*: `"Content-Type": "application/json"`

*Request Body*
```json
{
    "data": {
        "full_name": "Иван Иванов",
        "event_title": "Чемпионат по программированию",
        "stage": "Финал",
        "team_name": "Команда А",
        "organization_name": "ООО Программирование",
        "end_date": "2024-12-31"
    }
}
```

**Описание:** Этот эндпоинт используется для генерации одного сертификата. При этом поля уже должны быть расположены. При изменении расположения сертификат сгенерируется некоректно. Возвращает бинарный файл.

**Response**

* status: `200 OK`

    * Всё ОК.
    ```json
    {
        "file": "pdf-файл" 
    }
    ```

* status `400 BAD REQUEST`

    * Нет данных в запросе
    ```json
    {
        "error": "invalid data"
    }
    ``` 
    * Нет ключа `data`
    ```json
    {
        "error": "missing data key"
    }
    ```
    * Отсутствует обязательное поле
    ```json
    {
        "error": "missing fields", "fields": "fields_name"
    }
    ```

