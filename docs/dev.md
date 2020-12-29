# Dev

## Install

First, make sure [poetry](https://python-poetry.org/docs/) is installed and in your PATH. Then:

```
git clone https://github.com/tartopum/atelier
cd atelier
poetry install
```

## Usage

The application can be tested without an Arduino. To do so:

```bash
make fake_arduino
```

In another terminal, edit the `config.json` with Arduino IP set to `127.0.0.1`
and Arduino port set to `5001`. Then:

```
make
```

Find the server at `localhost:5000`.
