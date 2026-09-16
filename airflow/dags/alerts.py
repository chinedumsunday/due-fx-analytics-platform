import os
import requests


def notify_failure(context):
    """DAG-level failure callback. Posts to Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    ti = context.get("task_instance")
    dag_id = context.get("dag").dag_id if context.get("dag") else "unknown"
    task_id = ti.task_id if ti else "unknown"
    run_id = context.get("run_id", "unknown")
    exception = context.get("exception", "no exception detail")

    text = (
        f"🔴 *Due FX pipeline failure*\n\n"
        f"*DAG:* `{dag_id}`\n"
        f"*Task:* `{task_id}`\n"
        f"*Run:* `{run_id}`\n"
        f"*Error:* `{str(exception)[:300]}`"
    )

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )


def notify_sla_miss(dag, task_list, blocking_task_list, slas, blocking_tis):
    """SLA miss callback."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    text = f"⚠️ *SLA miss*\n\n*DAG:* `{dag.dag_id}`\n*Tasks:* `{task_list}`"
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )