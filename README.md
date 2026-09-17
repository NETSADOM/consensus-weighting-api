# Consensus Weighting API

A simple backend service that calculates allocation weights while prioritizing **broad participation over concentrated capital**.

The goal is to prevent a single participant with a large allocation from easily overpowering a larger group of participants making smaller allocations.

## Overview

Traditional allocation systems based only on raw totals treat these two scenarios equally:

* One user allocates `10,000`.
* One hundred users each allocate `100`.

Both have a raw total of `10,000`.

However, they represent very different levels of participation. The Consensus Weighting API applies a dampening formula so that broader participation receives greater weight than capital concentrated in a single user.

## Weighting Approach

Allocations are processed in three stages:

1. Group allocations by `targetId`.
2. Aggregate multiple allocations from the same `userId` to the same target.
3. Apply the consensus weighting formula to the aggregated contribution of each unique user.

The weighting formula is:

```text
weight = (Σ √userTotal)²
```

Where `userTotal` is the total amount contributed by one unique user to a particular target.

The square-root transformation creates diminishing influence for additional capital contributed by the same participant while allowing participation from additional unique users to increase the final weight.

### Concentrated vs. Distributed Example

Consider two targets with the same raw allocation total.

**Target A — Concentrated**

```text
1 user × 10,000

weight = (√10,000)²
       = 100²
       = 10,000
```

**Target B — Distributed**

```text
100 unique users × 100

weight = (100 × √100)²
       = (100 × 10)²
       = 1,000,000
```

Both targets receive a raw total of `10,000`, but:

```text
Target A weight = 10,000
Target B weight = 1,000,000
```

Therefore:

```text
Target B weight = 100 × Target A weight
```

This ensures that distributed participation receives substantially greater weight than concentrated capital.

## Multiple Allocations From the Same User

A user may submit multiple allocations to the same target.

For example:

```json
[
  {
    "userId": "user_1",
    "targetId": "A",
    "amount": 50
  },
  {
    "userId": "user_1",
    "targetId": "A",
    "amount": 50
  }
]
```

These allocations are first aggregated:

```text
user_1 → Target A → 100
```

The weighting formula is then applied:

```text
√100
```

rather than:

```text
√50 + √50
```

This is important because multiple allocation records from the same user represent **one participant**, not multiple participants.

It also prevents a user from gaining additional consensus weight simply by splitting one allocation into several requests using the same `userId`.

> The API assumes that each `userId` represents a unique participant. Identity verification and protection against users creating multiple identities are outside the scope of this challenge.

## API

### Calculate Consensus Weights

```http
POST /weights
```

The endpoint accepts an array of raw allocations.

### Request

Each allocation contains:

| Field      | Description                                       |
| ---------- | ------------------------------------------------- |
| `userId`   | Identifier of the participant                     |
| `targetId` | Identifier of the target receiving the allocation |
| `amount`   | Positive amount allocated to the target           |

Example:

```json
[
  {
    "userId": "user_1",
    "targetId": "A",
    "amount": 10000
  },
  {
    "userId": "user_2",
    "targetId": "B",
    "amount": 100
  },
  {
    "userId": "user_3",
    "targetId": "B",
    "amount": 100
  }
]
```

### Response

Each target returns:

* `targetId` — target being evaluated
* `rawTotal` — total amount allocated to the target before weighting
* `uniqueUserCount` — number of unique users who allocated to the target
* `weight` — final consensus-adjusted weight

Example result:

```json
[
  {
    "targetId": "A",
    "rawTotal": 10000,
    "uniqueUserCount": 1,
    "weight": 10000
  },
  {
    "targetId": "B",
    "rawTotal": 200,
    "uniqueUserCount": 2,
    "weight": 400
  }
]
```

## Validation and Edge Cases

The API validates incoming allocations before performing calculations.

The implementation considers the following cases:

* Multiple allocations from the same user to the same target are aggregated.
* The same user may allocate to different targets independently.
* Multiple targets can be processed in one request.
* `userId` and `targetId` must be valid non-empty identifiers.
* Zero and negative allocation amounts are rejected.
* Positive decimal allocation amounts are supported.
* Unique-user counts are based on unique `userId` values rather than the number of allocation records.

The final implementation should also define consistent behavior for an empty allocation array and malformed request data.

## Technology Stack

The backend is built using:

* **Python** — application and weighting logic
* **FastAPI** — REST API framework
* **Pydantic** — request and response validation
* **pytest** — automated testing
* **Uvicorn** — local ASGI server

## Project Structure

The application separates HTTP handling, data validation, business logic, and testing.

```text
consensus-weighting-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── services.py
├── tests/
│   └── ...
├── .gitignore
├── requirements.txt
└── README.md
```

> The final project structure should be updated to match the completed repository exactly.

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd consensus-weighting-api
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

FastAPI's interactive API documentation can then be used to test the available endpoints.

```text
http://127.0.0.1:8000/docs
```

## Running the Tests

Run the complete automated test suite with:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

### Critical Consensus Test

The test suite includes the comparison required by the challenge.

**Concentrated allocation**

```text
Target A
1 user × 10,000
Raw total = 10,000
```

**Distributed allocation**

```text
Target B
100 unique users × 100
Raw total = 10,000
```

The test uses the actual weighting implementation and programmatically verifies:

```python
assert weight_b >= 2 * weight_a
```

Additional tests verify grouping, duplicate-user aggregation, unique-user counting, input validation, and API behavior.

## AI-Assisted Development Process

### AI Tool

**Claude** was used as the AI coding agent during development.

Instead of asking the agent to generate the entire solution at once, development was divided into small, independently reviewed stages:

1. Initialize the FastAPI project.
2. Define allocation models and input validation.
3. Implement grouping by `targetId` and `userId`.
4. Implement the consensus weighting formula.
5. Expose the calculation through the REST endpoint.
6. Add automated tests.
7. Review edge cases and code quality.
8. Complete the project documentation.

This approach made each generated change easier to inspect, test, and commit independently.

### Prompting for the Grouping Logic

The AI was explicitly instructed to first group allocations by `targetId` and then aggregate allocations by `userId` within each target.

Special attention was given to repeated allocations such as:

```text
user_1 → A → 40
user_1 → A → 60
```

The AI was instructed to treat these as:

```text
user_1 → A → 100
```

before applying the weighting formula.

This ensures that the number of allocation records is not incorrectly treated as the number of unique participants.

### Prompting for the Weighting Logic

The AI was given the required comparison:

```text
1 user × 10,000
```

versus:

```text
100 unique users × 100
```

and instructed to implement the selected formula:

```text
(Σ √userTotal)²
```

The calculation was then manually checked against the required scenarios and verified through automated tests.

### AI Limitations

Three areas required particular attention when reviewing AI-assisted code:

* **Aggregation order:** The square-root transformation must be applied after allocations belonging to the same user and target have been combined. Applying it before aggregation would incorrectly reward a user for splitting an allocation into multiple entries.

* **Unique-user counting:** Multiple allocation records do not necessarily represent multiple participants. The grouping logic must count unique `userId` values rather than allocation objects.

* **Test correctness:** The required distributed test must create 100 genuinely distinct user IDs and execute the real weighting implementation. A test based on hard-coded results or repeated user IDs would not properly verify the requirement.

AI-generated changes were therefore treated as implementation proposals and verified through code review, manual mathematical checks, API testing, and automated tests before being committed.

## Design Decisions

### Why FastAPI?

FastAPI provides a lightweight way to build the single REST endpoint required by the challenge while also providing automatic request validation and interactive API documentation.

### Why Aggregate by User First?

The challenge allows one user to submit multiple allocations to the same target.

Aggregating those allocations before weighting ensures that repeated submissions from the same participant do not artificially appear as broader consensus.

### Why Square-Root Weighting?

The square-root transformation provides diminishing marginal influence for increasingly large allocations from one participant.

At the same time, contributions distributed among multiple users produce a greater combined weight, directly supporting the goal of prioritizing broad consensus over concentrated capital.

## Limitations

This implementation intentionally focuses on the scope of the take-home challenge.

* `userId` is assumed to represent a unique participant; the service does not perform identity verification or Sybil detection.
* The weighting strategy is currently fixed rather than configurable.
* The service performs calculations from the submitted request and does not provide persistent allocation storage.

## Future Improvements

Possible extensions include:

* Persistent storage for allocations and calculated results.
* Authentication and stronger participant identity verification.
* Additional protection against Sybil behavior.
* Configurable consensus-weighting strategies.
* Rate limiting for a production deployment.

## Summary

The Consensus Weighting API demonstrates how allocation influence can account for both **capital and breadth of participation**.

By aggregating allocations at the user level and applying a square-root-based weighting mechanism, the API ensures that a large group of participants making smaller allocations can receive substantially greater consensus weight than a single participant providing the same total amount.
