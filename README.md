# ZeroTier Network Member Manager Script Documentation

This Python script manages ZeroTier network members using the ZeroTier API. It allows fetching network members, editing member details, and updating member authorization statuses via the command line.

----------

## Components

### 1. **API Token and Network ID**

-   `API_TOKEN` and `NETWORK_ID` are required to authenticate and interact with the ZeroTier API.

### 2. **Headers Setup**

-   Sets the `Authorization` header using the API token for secure API requests.

### 3. **Fetch Members** (`fetch_members`)

-   Sends a `GET` request to retrieve all network members.
-   Handles HTTP errors and exceptions.

### 4. **Update Member** (`update_member`)

-   Sends a `POST` request to update member details such as name, description, and authorization status.
-   Accepts parameters like `address`, `name`, `description`, and `authorized`.

### 5. **Main Function** (`main`)

-   Parses command-line arguments using `argparse`.
-   Provides options to:
    -   Fetch and display network members.
    -   Edit member details (name, description).
    -   Authorize or deauthorize members.
-   Outputs network member details such as address, name, managed IPs, last seen time, version, and authorization status in a formatted table.

----------

## Usage

### Command-line Arguments:

-   `--address`: Specify member address.
-   `--edit`: Edit member details.
-   `--auth`: Set authorization status (`true` or `false`).
-   `--name`: New name for the member.
-   `--description`: New description.

### Example Commands:

```bash
# Fetch all members
python script.py

# Edit member name and description
python script.py --address <member_address> --edit --name "New Name" --description "New Description"

# Authorize a member
python script.py --address <member_address> --auth true

```

----------

## Output Example:

```
Network 41d49af6c2cb4b82:

Address              Name/Desc                     Managed IPs           Last Seen                Version   Authorization
=========================================================================================================
abc123456789         Server Node                   192.168.192.1         2025-02-13 12:34:56 UTC  1.10.0    Authorized

```

----------

## Improvements and Considerations

-   **Security:** Store API tokens securely (e.g., environment variables).
-   **Enhancements:** Add more member management features (e.g., removal).
-   **Error Handling:** Improve error handling for different API failure scenarios.

----------

This script simplifies the management of ZeroTier networks, making it an essential tool for network administrators and engineers.
