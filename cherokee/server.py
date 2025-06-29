"""Entry point for running the Cherokee Flask API."""

import os

from .web import create_app

app = create_app()


def run() -> None:
    """Run the Flask app with sane defaults for start_services.sh."""
    debug = os.getenv("CHEROKEE_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=5000, debug=debug, use_reloader=False)


if __name__ == "__main__":
    run()
