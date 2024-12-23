# Human Resource Management

## Document

- Clone the repository
- Create a `.env` file
- Make a virtualenv and install all requirements
- Create a database and add configuration to the `.env` file from `.env.example`
- Run Django migrate commands
- Run the project with `runserver` command

---

# Project ERD Diagram

<img src="https://github.com/sakilanasrinsetu/human_resource_management/blob/main/erd.png?raw=true" width="100%">

---

# Project API Diagrams

### API Setup Diagrams

<div style="display: flex; justify-content: space-around;">
    <img src="https://github.com/sakilanasrinsetu/human_resource_management/blob/main/static/image/all-api.png?raw=true" width="45%">
    <img src="https://github.com/sakilanasrinsetu/human_resource_management/blob/main/static/image/all-data.png?raw=true" width="45%">
</div>

### Error Response and Input Diagrams

<div style="display: flex; justify-content: space-around;">
    <img src="https://github.com/sakilanasrinsetu/human_resource_management/blob/main/static/image/error-responce.png?raw=true" width="45%">
    <img src="https://github.com/sakilanasrinsetu/human_resource_management/blob/main/static/image/input.png?raw=true" width="45%">
</div>

### Retrieve and Search Diagrams

<div style="display: flex; justify-content: space-around;">
    <img src="https://github.com/sakilanasrinsetu/human_resource_management/blob/main/static/image/retrieve.png?raw=true" width="45%">
    <img src="https://github.com/sakilanasrinsetu/human_resource_management/blob/main/static/image/search.png?raw=true" width="45%">
</div>

---

# Project requirement setup

```bash
pip install -r requirements.txt
```


# Project Run Command

```python
python manage.py runserver


Project API Url
Main API: http://127.0.0.1:8000
API Documentation (Redoc): http://127.0.0.1:8000/redoc/

```

# For Dump Project Data

```
python manage.py dumpdata > hr.json employee

```

# License

### Key Elements:

- **Document Section**: Lists the steps for setting up the project (cloning, virtual environment, database, etc.).
- **ERD and API Diagrams**: Includes links to images hosted on GitHub for the ERD and API documentation.
- **Requirements Setup**: Command to install required dependencies.
- **Run Command**: Command to start the Django server.
- **API URL**: Lists the URL for the main API and Redoc API documentation.
- **Data Dump**: Command to dump the project's data.
