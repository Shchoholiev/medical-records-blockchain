# medical-records-blockchain
Blockchain implementation for securely storing medical data, ensuring data integrity and privacy. Developed in Python with FastAPI for integration, it focuses on a custom blockchain solution to protect sensitive health records.

## Table of Contents
- [Features](#features)
- [Stack](#stack)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)

## Features
- Custom blockchain implementation for immutable medical record storage
- Secure storage and retrieval of medical data on CosmosDB
- FastAPI backend with REST API endpoints for blockchain operations
- JWT-based authentication and authorization with OAuth2 and RS256 keys
- Validator management to control authorized entities modifying the blockchain
- User authentication with password hashing and role-based access
- Logging and error handling for robust API interactions

## Stack
- **Programming Language:** Python 3.12
- **Web Framework:** FastAPI
- **Database:** Azure Cosmos DB (NoSQL)

## Installation

### Prerequisites
- Python 3.12 or higher installed
- [Azure Cosmos DB Account](https://azure.microsoft.com/en-us/services/cosmos-db/) with access credentials
- (Optional) Docker and VSCode with Remote Containers extension for devcontainer usage

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/Shchoholiev/medical-records-blockchain
   cd medical-records-blockchain
   ```

2. (Optional) Use the provided devcontainer for consistent environment setup:
   - Open the repository folder in VSCode.
   - Use the "Reopen in Container" command to build and enter the devcontainer.

3. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Set up the environment variables by creating a `.env.local` file in the project root (see Configuration below).

5. Run the FastAPI application locally:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

6. For production or other deployment environments, adjust host and port as needed:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

## Configuration

Create a `.env.local` file in the root directory with the following environment variables:

```text
COSMOSDB_ENDPOINT=<your-cosmosdb-endpoint>
COSMOSDB_KEY=<your-cosmosdb-primary-key>
COSMOSDB_DATABASE=<your-database-name>

JWT_PRIVATE_KEY=<your-RSA-private-key-contents>
JWT_PUBLIC_KEY=<your-RSA-public-key-contents>
```

- **COSMOSDB_ENDPOINT, COSMOSDB_KEY, COSMOSDB_DATABASE**: Provide your Azure Cosmos DB account connection details.
- **JWT_PRIVATE_KEY, JWT_PUBLIC_KEY**: Provide the RSA keys used for signing and verifying JWT access tokens. These should be in PEM format and properly multiline escaped if set in the `.env.local` file.

Ensure the keys and sensitive values are kept secure and not shared publicly.
