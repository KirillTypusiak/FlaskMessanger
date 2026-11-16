from app.settings import main_app
import app.urls

def main():
    try:
        main_app.run(
            port = 8000,
            debug = True,
        )
    except Exception as err:
        print(f"Помилка під час запуску проєкта: {err}")

if __name__ == "__main__":
    main()