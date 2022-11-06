# API для просмотра, изменения, добавления конфигов приложений

1. Опишите самую интересную задачу в программировании, которую вам приходилось решать?

Кастомизация админки джанго, встраивание сторонней библиотеки, которая не предполагалась использоваться в админке. 

2. Расскажите о своем самом большом факапе? Что вы предприняли для решения проблемы?

Создал тестовую запись в боевой базе. Стал внимательнее относится к переменным окружения

3. Каковы ваши ожидания от участия в буткемпе?

Стажировка на новом языке, в известной компании. Я думаю, что будет нереально круто. Хочу обрести новые компетенции.

API поддерживает версионирование.

## Стек:

Django 4.1.2

Django REST framework 3.14.0

PostgreSQL 13

protobuf

python 3.8

## Инструкция по использованию

git clone git@github.com:Konstantin8891/sber_config.git

### Создание сообщения protobuf

cd protobuf

PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python3 write_record.py

Следуйте инструкциям в консоли

### Запуск проекта

cd infra

docker-compose up --build

docker-compose exec api python manage.py migrate

### Примеры запросов

Примеры запросов указаны при условии использования Postman

При отправке файлов необходимо указать в headers: 

1) ключ Content-Disposition
2) значение attachment; filename=data.bin

Запрос GET

http://localhost/config

Выводит полный список приложений, версий конфигов и значений ключей

[

    {
    
        "service": {
        
            "name": "managed-k5s"
            
        },
        
        "version": "1.0",
        
        "is_used": true,
        
        "keys": [
        
            {
            
                "key1": "value1"
                
            },
            
            {
            
                "key2": "value2"
                
            }
            
        ]
        
    },
    
    {
    
        "service": {
        
            "name": "managed-k6s"
            
        },
        
        "version": "1.0",
        
        "is_used": true,
        
        "keys": [
        
            {
            
                "key1": "value2"
                
            },
            
            {
            
                "key2": "value2"
                
            },
            
            {
            
                "key3": "value3"
                
            }
            
        ]
        
    }
    
]

http://localhost/config?service=имя_сервиса&version=версия

Выводит список ключей и значений для запрашиваемой версии конфига приложения

[
    {
        "key1": "value2"
    },
    {
        "key2": "value2"
    },
    {
        "key3": "value3"
    }
]

Запрос PATCH

http://localhost/config

Изменяет значения ключей, параметра использования конфига

Запрос PUT

http://localhost/config

Изменяет или создаёт конфиг

Запрос POST

http://localhost/config

Создаёт конфиг

Запрос DELETE 

http://localhost/config?service=имя_сервиса&version=версия

Удаляет конфиг, если он неиспользуется.
