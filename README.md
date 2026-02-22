# How Is My Investment Doing (himid) project by julestristan

[ticker list from yfinance website](https://finance.yahoo.com/lookup/)

## 1 - How to install

```bash
uv pip install -r requirements
```

### Using docker

```bash
docker build -t himid .
```

Make sure you have a .env file in the root folder of the repo with:

- EMAIL_SENDER
- EMAIL_PASSWORD
- MISTRALAI_API_KEY or OPENAI_API_KEY

```bash
docker run -p 8501:8501 --env-file .env himid
```

## 2 - How to use

## 3 - Example

Notes:

- Implement a table to be informed about upcoming annual results
- Volumetry as a 3rd dimension for CorMatrix
- Check what to do to improve LLM answer for daily variations (currently not insightful)
- add streamlit interface
- Other Cron option ?
