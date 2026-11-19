"""Gunicorn loads this file automatically from the working directory (/app)."""


def post_fork(server, worker):
    from outbox_worker import start_outbox_worker
    if start_outbox_worker():
        server.log.info("Payment outbox worker started in worker %s", worker.pid)
