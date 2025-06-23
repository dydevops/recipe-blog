# Recipe Management System

A comprehensive recipe management system built with Django that includes:

- Recipe categories
- Hierarchical glossary using MPTT
- Recipe ingredients with fractional quantities
- Recipe-glossary linkages
- Modern and user-friendly interface

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Features

- Hierarchical category management
- MPTT-based glossary for efficient tree structures
- Recipe management with ingredients
- Support for fractional quantities
- Image upload support for recipes
- Cross-referencing between recipes and glossary terms
