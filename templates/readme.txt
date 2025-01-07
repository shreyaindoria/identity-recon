# Identity Reconciliation Service

## Overview
This project implements an **Identity Reconciliation Service** using Flask and MySQL. It accepts email and phone number inputs, identifies matching records in the database, and associates related data by designating them as primary or secondary contacts.

The service also includes a simple web interface to submit requests and view responses.

---

## Features
1. **REST API Endpoint**: `/identity`
   - Accepts `POST` requests with JSON payloads containing `email` and `phoneNumber`.
   - Processes the request to find and link related contacts based on matching email or phone numbers.
   - Returns a JSON response containing primary and secondary contact details.
   - Running on http://127.0.0.1:5000

2. **Web Interface**:
   - A basic HTML form for testing the service.
   - Allows users to submit email and phone number data and displays the JSON response.

3. **Logging**:
   - Saves both request and response data to separate JSON files in a `logs/` directory for auditing.

4. **Database**:
   - Uses MySQL for persistent data storage.
   - Auto-creates a `contact` table if it doesn't exist.

---

## Setup Instructions

### Prerequisites
- Python 3.7 or above
- MySQL Server
- Flask and required Python dependencies
- Internet browser for web interface testing


