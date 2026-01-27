from src.services.data_fetcher import fetch_proposicoes_task, fetch_votacoes_task
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.manual_ingest [proposicoes|votacoes] [days_back]")
        return

    target = sys.argv[1]
    days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    if target == "proposicoes":
        print(f"Triggering fetch_proposicoes_task for last {days_back} days...")
        # Using .delay() sends it to Celery worker
        fetch_proposicoes_task.delay(days_back=days_back)
        print("Task queued! Check Celery logs.")
        
    elif target == "votacoes":
        print(f"Triggering fetch_votacoes_task for last {days_back} days...")
        fetch_votacoes_task.delay(days_back=days_back)
        print("Task queued! Check Celery logs.")
        
    else:
        print("Unknown target. Use 'proposicoes' or 'votacoes'.")

if __name__ == "__main__":
    main()
