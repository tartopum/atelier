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

In another terminal:

```
make # Or: make dev_fake
```

Find the server at `localhost:5000`.
