Django 2025, осень

Магазин (енотов?)
Статус: 

Данное приложение реализует простую версию интернет-магазина с описанием проекта, каталогом и главной страницей

Установка через bash

0. Prerequisites
Версии python: 3.10, 3.11, 3.12, 3.13, 3.14
Версии gettextx: 0.26
Версии git: 2.x

sudo apt update
sudo apt install python3
python --version
git --version



1. Клонирование репозитория (git status)

git clone https://gitlab.crja72.ru/django/2025/autumn/course/students/265200-D-murm-course-1474.git
cd 265200-D-murm-course-1474



2. Виртуальное окружение

При наличии python >= 3.10

python3 -m venv venv



Linux-оиды:

source venv/bin/activate



Windows

venv\Scripts\activate



3. Зависимости

Для продакшна:

pip3 install -r requirements/prod.txt



Для разработки:

pip3 install -r requirements/dev.txt



4. Настройка переменных окружения

cp template.env lyceum/.env




Переменные будут браться из скопированного template.env в .env

5. Настройки через manage.

cd lyceum



5.1 Миграции

python3 manage.py migrate



5.2 Языки

django-admin -l <код языка>
django-admin compilemessages


доступные языки: ru, en

5.3 Загрузка фикстур

python3 manage.py loaddata fixtures/data.json



5.4 Создание админа

python3 manage.py createsuperuser


Следовать указаниям терминала.

6. Запуск сервера

python3 manage.py runserver <порт, по умолчанию 8000>



Приложение будет заущено на указанный порт

ER.jpg - логическая схема баз данных (будет обновляться и дополняться).
