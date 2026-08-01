# AI_NOTES

## AI Tools Used

I used **Gemini** and **GitHub Copilot** during this assignment.

- **Gemini** was mainly used to discuss implementation choices, review edge cases, and check whether the solution covered the assignment requirements.
- **GitHub Copilot** was used as an in-editor assistant for code completion, repetitive test code, and small implementation suggestions.

I treated AI suggestions as inputs to review rather than assuming they were correct. I made the final implementation decisions and verified the resulting behavior manually and through automated tests.

---

## 1. Which Parts Were AI-Assisted vs. Written by Me

### AI-Assisted

Gemini was useful for reviewing and discussing:

- the initial FastAPI project structure;
- separation between API routes, validation models, and JSON persistence;
- validation and error-handling scenarios;
- possible issues with ID generation;
- edge cases worth covering in the test suite;
- ways to keep the implementation within the intended scope of the assignment.

GitHub Copilot was mainly used while coding for:

- in-editor code completion;
- completing repetitive FastAPI and Pydantic code;
- completing similar pytest assertions and test cases;
- small implementation suggestions based on the surrounding code.

### Written, Reviewed, and Decided by Me

I assembled and reviewed the final implementation and made the final decisions regarding:

- the API endpoint structure;
- JSON-file persistence;
- server-generated expense IDs;
- input validation rules;
- case-insensitive category filtering;
- HTTP status and error behavior;
- test isolation;
- the choice of OpenAPI/Swagger documentation as the optional bonus.

I also manually ran the application, exercised the API endpoints, checked JSON persistence, tested invalid inputs and edge cases, and ran the automated test suite before finalizing the solution.

---

## 2. What I Validated, Tested, or Changed

### ID Generation

I specifically reviewed how expense IDs should be generated.

A simple approach such as:

`len(expenses) + 1`

can generate duplicate IDs after deletion. For example, if IDs 1, 2, and 3 exist and ID 2 is deleted, there are two stored expenses and `len + 1` would produce ID 3 even though that ID already exists.

I therefore used the highest existing ID plus one.

I manually verified this by creating multiple expenses, deleting one, and then creating another expense. I also added an automated test for this case.

### Input Validation

I tested the API with invalid input instead of only checking successful requests.

I tested:

- negative amounts;
- an amount of zero;
- empty and whitespace-only titles;
- empty and whitespace-only categories;
- invalid date formats.

These requests correctly return HTTP 422 responses.

I also verified that surrounding whitespace in valid titles and categories is removed before the expense is stored.

### Category Filtering

I chose to make category matching case-insensitive so that values such as `Food`, `food`, and `FOOD` behave consistently.

I verified this manually and added automated test coverage for it.

If a category has no matching expenses, the API returns an empty list rather than treating it as an error.

### Expense Totals

I created expenses across multiple categories and manually checked:

- the overall expense total
- the total for a specific category.

I also checked the behavior for a category containing no expenses, which returns a total of zero.

These cases are covered by automated tests as well.

### Delete Behavior

I tested deletion for both existing and non-existing expenses.

Deleting an existing expense returns HTTP 200 and removes it from storage. Attempting to delete the same ID again returns HTTP 404.

Both scenarios are included in the automated test suite.

### Test Isolation

I did not want automated tests to modify the application's actual `src/expenses.json` file or depend on data created by another test.

The test suite therefore uses pytest temporary directories and monkeypatching to redirect persistence to a fresh JSON file for each test.

I ran the test suite multiple times to confirm that the results were repeatable and that `src/expenses.json` remained unchanged.

---

## 3. AI Suggestions or Alternatives I Decided Not to Use

### Database Storage

I considered using a database but decided not to introduce one.

The assignment explicitly allows local JSON storage, and a database would add setup and complexity without being necessary for the required functionality.

I used JSON persistence instead and kept the persistence logic separate from the API routes so that the storage implementation could be replaced later if needed.

### Additional Architecture Layers

I considered adding service and repository layers but decided that they were unnecessary for an API of this size.

Instead, I kept responsibilities separated between:

- `routes.py` for HTTP/API handling;
- `schemas.py` for request/response models and validation;
- `storage.py` for persistence.

This gives the project separation of concerns without adding unnecessary abstraction.

### Additional Bonus Features

The assignment specifies that at most one optional bonus should be implemented.

I selected **OpenAPI/Swagger documentation** because it is directly useful for a REST API and integrates naturally with FastAPI.

I intentionally did not add search, monthly summaries, or Docker support so that I could focus on making the required functionality reliable and well tested.

### Monetary Representation

I considered using `Decimal` for expense amounts because fixed-precision values are preferable for monetary data.

For the scope of this assignment, I kept the simpler numeric representation and round calculated totals to two decimal places.

For a production financial application, I would use fixed-precision decimal values to avoid floating-point precision issues.

---

## Final Verification

Before finalizing the assignment, I:

- started the API locally using Uvicorn;
- tested the endpoints through Swagger UI;
- verified that expenses were persisted to the JSON file;
- tested adding and viewing expenses;
- tested case-insensitive category filtering;
- verified overall and category-specific totals;
- tested successful deletion and HTTP 404 behavior;
- tested invalid input and HTTP 422 responses;
- verified ID generation after deleting an expense;
- ran the automated test suite multiple times;
- confirmed all 21 tests passed;
- confirmed that the tests did not modify `src/expenses.json`.

AI was useful for reviewing approaches, identifying edge cases, and speeding up repetitive development work. I still validated the behavior myself and made the final implementation decisions before including them in the submission.