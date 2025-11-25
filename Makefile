VENV = venv
PYTHON = $(VENV)/bin/python

# Если окружения нет — создаём
$(VENV)/bin/activate:
	python3 -m venv $(VENV)

# Установка зависимостей
install: $(VENV)/bin/activate
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# Запуск бота — всегда через venv
run: $(VENV)/bin/activate
	. $(VENV)/bin/activate && $(PYTHON) main.py

# Обновление списка зависимостей
freeze:
	$(PYTHON) -m pip freeze > requirements.txt

# Очистка окружения
clean:
	rm -rf $(VENV)


# source venv/bin/activate
