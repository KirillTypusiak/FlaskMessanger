from app.settings import main_app
import app.urls
import app.database
import app.models
import app.login

def main():
    try:
        
        main_app.run(
            port = 8000,
            debug = True,
        )
    except Exception as err:
        print(f"Помилка під час запуску проєкта: {err}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()