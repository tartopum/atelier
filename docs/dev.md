# Dev

## Install

First, make sure [`pipenv`](https://pipenv.readthedocs.io/en/latest/) is installed and in your PATH. Then:

```
git clone https://github.com/tartopum/atelier
cd atelier
pipenv install
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
