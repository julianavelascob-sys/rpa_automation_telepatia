# Refund Request RPA Automation

This project simulates a small internal operations workflow that processes refund requests from a CSV file and submits them automatically into a local web portal using Python and Playwright. 

---

## Project Structure

```
/project-folder
│
├── automation.py          # Main RPA automation script
├── internal_portal.html   # Local internal portal (fake web form)
├── data.csv               # Sample input file with refund requests
├── results.csv            # Automatically generated output file
├── automation.log         # Detailed runtime log
└── README.md              # Documentation (this file)
```

---

## Tools & Versions Used

- Python 3.10+
- Playwright for Python (sync API)
- Browser engine: WebKit (Safari equivalent)
- macOS + zsh terminal
- Visual Studio Code

Install dependencies:

```bash
pip install playwright
python3 -m playwright install
python3 -m playwright install-deps
```

---

## Input File: `data.csv`

Your CSV must contain the following columns:

| Column          | Description                              |
|------------------|------------------------------------------|
| RequestId        | Unique refund request ID                 |
| CustomerName     | Customer full name                       |
| CustomerEmail    | Email address                            |
| Amount           | Refund amount                            |
| Status           | Pending, Approved, Rejected              |

Only **Pending** rows are processed. Invalid rows are skipped but logged.

---

## Internal Portal (`internal_portal.html`)

A simple HTML page acting as the internal "refund portal."

It contains fields for:

- Request ID
- Customer Name
- Email
- Amount
- Decision (Approved / Manual Review)

Upon clicking **Submit**, the page:

- Prints the submitted data inside a result box  
- Logs the data in the browser console  
- Requires no backend  

The automation fills this form and submits it for each pending request.

---

## Automation Workflow (`automation.py`)

### 1. Load and validate the CSV

- Reads all rows from `data.csv`
- Checks for missing fields
- Ensures Amount is numeric and non-negative
- Ensures Status is valid

Invalid rows:
- Are logged
- Are skipped

### 2. Open the internal portal

Using Playwright + WebKit:
- A visible browser window opens  
- The local HTML file is loaded  

### 3. Process Pending requests

For each valid pending row:

- Fills the form fields  
- Applies decision logic:

```
if amount <= 100 → Approved
else → Manual Review
```

- Clicks Submit  
- Portal displays the submitted data  
- Logs appear in console and automation.log  
- The result is stored in memory  

### 4. Save results

After processing everything, the automation generates:

```
results.csv
```

Containing:

```
RequestId,Decision
```

### 5. Full Logging

A detailed file is generated:

```
automation.log
```

Containing:
- INFO events  
- ERROR events  
- Invalid data warnings  
- Submission confirmations  

---

### Note on Timing (Deliberate Delays)

The automation includes small `time.sleep()` delays between each field interaction.

These pauses were added intentionally so the reviewer can clearly see every step of the automation inside the browser (filling fields, selecting a decision, and submitting the form).

In a production-grade RPA process, these delays would be removed to maximize speed and efficiency, since programmatic interactions do not require visual confirmation.

## Running the Automation

1. Open a terminal inside the project folder:

```bash
cd /path/to/project
```

2. Run:

```bash
python3 automation.py
```

3. A Safari/WebKit browser will open. You will see each row being filled in real time.

4. When complete, the following files will be created/updated:
- `results.csv`
- `automation.log`

---

## Error Handling Demonstration

The automation was designed to behave safely with incorrect CSV data.

Below are real examples from the provided `data.csv`.

### Console Output:

```
[ERROR] Amount is not numeric → Skipping row: {'RequestId': '1009', 'CustomerName': 'Camila Rojas', 'CustomerEmail': 'camila.rojas@example.com', 'Amount': 'forty', 'Status': 'Pending'}

[ERROR] Missing field 'CustomerEmail' → Skipping row: {'RequestId': '1007', 'CustomerName': 'María Diaz', 'CustomerEmail': '', 'Amount': '55', 'Status': 'Pending'}

```

### Log File (`automation.log`):

```
2025-02-18 15:22:11 | ERROR | Amount is not numeric → Skipping row: {…}
2025-02-18 15:22:13 | ERROR | Missing field 'CustomerEmail' → Skipping row: {…}
```

### Behavior Summary

| Issue Type                | Example            | Bot Behavior |
|---------------------------|---------------------|--------------|
| Missing field             | Empty email         | Skip + log   |
| Amount not numeric        | `"forty"`           | Skip + log   |
| Negative amount           | `-10`               | Skip + log   |
| Invalid status            | `"WAITING"`         | Skip + log   |
| Already approved/rejected | Status ≠ Pending    | Skip cleanly |

---

## Deliverables Included

- `automation.py`  
- `internal_portal.html`  
- `data.csv`  
- `results.csv`  
- `automation.log`  
- `README.md`

This fulfills all requirements of the assignment.

---

## Final Notes

This project demonstrates:

- RPA fundamentals  
- Browser automation  
- Data validation  
- Error handling  
- Logging  
- CSV processing  
- UI interaction  

Thank you!
