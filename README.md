# Simple Django REST API

## Database structure

### id (UUID)

Unique transaction ID.

### date (YYYY-MM-DD)

Transaction date.

### expense_type ([invoice | salary | services | office-supplies | travel]

Expense type.

### account_id (UUID)

Account ID of expense.

### amount (Float with max two decimal places)

Transaction amount.

## Endpoints

### 'admin/'

Yes, it is also exposed.

### 'transactions/'

#### POST

Adds new transaction to database. 201 if successful, 422 if data is not valid. Returns new object's UUID. Expects:
```
{
	'expense_type' : [invoice | salary | services | office-supplies | travel],
	'amount' : FLOAT,
	'expense_date' : YYYY-MM-DD,
	'account_id' : UUID
}
```

#### GET

200 if successful. Returns a JSON of all available records.

### 'transactions/<transaction_id>/'

#### GET

Returns a JSON of transaction. 200 if successful, 400 if object not found.

#### DELETE

SOFT deletes object in database. 204 if successful, 400 if object not found. Returns nothing.

### 'accounts/<account_id>/'

#### GET

Returns account's summary by expense types.

### 'accounts/<account_id>/<date_from>/'

#### GET

Returns account's summary by expense types starting (incl.) with the given date.

### 'accounts/<account_id>/<date_from>/<date_to>/'

#### GET

Returns account's summary by expense types starting (incl.) with the given date and ending (incl.) given date.

## How to run

1. ```pip install -r requirements.txt```
2. ```python3 manage.py migrate```
3. (optional) ```python3 manage.py migrate --run-syncdb```
4. ```gunicorn prodsight.wsgi```
5. You might want to use the postman collection.

## Live test

You can test the app at https://simple-django-rest-api.herokuapp.com/. URLs included in the postman collection.
