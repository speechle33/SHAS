from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    print("Current working directory:", os.getcwd())  # Новая строка для вывода текущего рабочего каталога
    print("Files in current directory:", os.listdir('.'))  # Новая строка для вывода всех файлов в текущем каталоге
    print("Files in templates directory:", os.listdir('templates'))  # Новая строка для вывода всех файлов в каталоге templates
    print("Files in templates directory:", os.listdir('static'))
    app.run(debug=True)