FROM python:3.12

# Копирование нужных файлов в контейнер
WORKDIR /app
COPY ./raket_utils.py .
COPY ./temps_files ./temps_files

# Установка PyInstaller
RUN pip install pyinstaller python-gitlab logging typer

# Сборка исполняемого файла
RUN pyinstaller --onefile --add-data "temps_files:temps_files" raket_utils.py

# ENTRYPOINT ["pyinstaller", "--onefile", "--add-data", "temps_files:temps_files", "raket_utils.py"]
# ENTRYPOINT ["./dist/raket_utils", "--help"]
ENTRYPOINT ["bash"]
# CMD []

