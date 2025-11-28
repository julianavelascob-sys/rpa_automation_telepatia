import csv
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

CSV_FILE = "data.csv"
RESULTS_FILE = "results.csv"
LOG_FILE = "automation.log"
PORTAL_URL = "file://" + str(Path("internal_portal.html").resolve())  # Local HTML portal

# Stores: {"RequestId": "...", "Decision": "..."}
decision_log = []

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("=== Automation Script Started ===")


# -----------------------------------------------------
# Validate row
# -----------------------------------------------------
def is_valid_row(row):
    required = ["RequestId", "CustomerName", "CustomerEmail", "Amount", "Status"]

    # Missing fields
    for field in required:
        if row.get(field) is None or row[field].strip() == "":
            msg = f"Missing field '{field}' → Skipping row: {row}"
            print("[ERROR]", msg)
            logging.error(msg)
            return False

    # Amount numeric
    try:
        amount = float(row["Amount"])
        if amount < 0:
            msg = f"Negative amount → Skipping row: {row}"
            print("[ERROR]", msg)
            logging.error(msg)
            return False
    except ValueError:
        msg = f"Amount is not numeric → Skipping row: {row}"
        print("[ERROR]", msg)
        logging.error(msg)
        return False

    # Status valid?
    valid_status = ["Pending", "Approved", "Rejected"]
    if row["Status"] not in valid_status:
        msg = f"Invalid status '{row['Status']}' → Skipping row: {row}"
        print("[ERROR]", msg)
        logging.error(msg)
        return False

    return True


# -----------------------------------------------------
# Save results
# -----------------------------------------------------
def save_results_csv():
    if not decision_log:
        print("[INFO] No decisions to save.")
        logging.info("No decisions to save.")
        return

    try:
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["RequestId", "Decision"])
            for entry in decision_log:
                writer.writerow([entry["RequestId"], entry["Decision"]])

        print(f"[OK] Results saved to {RESULTS_FILE}")
        logging.info(f"Results saved to {RESULTS_FILE}")

    except Exception as e:
        print("[ERROR] Failed to save results CSV:", e)
        logging.error(f"Failed to save results CSV: {e}")


# -----------------------------------------------------
# Main automation
# -----------------------------------------------------
def run_automation():
    print("=== Starting Refund Automation ===")
    logging.info("Refund automation started.")

    # Load CSV
    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            data = list(csv.DictReader(f))
        logging.info(f"Loaded {len(data)} rows from {CSV_FILE}")
    except Exception as e:
        print("[FATAL] Could not read CSV:", e)
        logging.critical(f"Could not read CSV file: {e}")
        return

    # Start Playwright
    with sync_playwright() as pw:
        browser = pw.webkit.launch(headless=False)
        page = browser.new_page()

        # Open portal
        try:
            page.goto(PORTAL_URL)
            logging.info("Portal loaded successfully.")
        except Exception as e:
            print("[FATAL] Could not load portal:", e)
            logging.critical(f"Failed to load portal: {e}")
            browser.close()
            return

        # Process each row
        for row in data:
            print("\n-----------------------------------")
            print(f"Processing RequestId: {row.get('RequestId')}")
            logging.info(f"Processing row: {row}")

            # Validate row
            if not is_valid_row(row):
                logging.warning(f"Skipping invalid row: {row}")
                continue

            # Only Pending
            if row["Status"] != "Pending":
                print("Skipping (Status != Pending)")
                logging.info(f"Skipping row {row['RequestId']} (Status = {row['Status']})")
                continue

            # Extract data
            req_id = row["RequestId"]
            name = row["CustomerName"]
            email = row["CustomerEmail"]
            amount = float(row["Amount"])

            # Decision logic
            decision = "Approved" if amount <= 100 else "Manual Review"

            # Record decision
            decision_log.append({"RequestId": req_id, "Decision": decision})

            try:
                # Fill form
                page.fill("#reqId", req_id); time.sleep(0.4)
                page.fill("#name", name); time.sleep(0.4)
                page.fill("#email", email); time.sleep(0.4)
                page.fill("#amount", str(amount)); time.sleep(0.4)
                page.select_option("#decision", decision); time.sleep(0.4)

                # Submit
                page.click("button")
                time.sleep(0.4)

                print(f"[OK] Submitted → {req_id} ({decision})")
                logging.info(f"Submitted RequestId {req_id} with decision '{decision}'")

            except Exception as e:
                print(f"[ERROR] Failed to submit row {req_id}:", e)
                logging.error(f"Error submitting row {req_id}: {e}")
                continue

        print("\n=== Automation Complete ===")
        logging.info("Automation completed successfully.")
        browser.close()

    save_results_csv()
    logging.info("=== Script finished ===")


if __name__ == "__main__":
    run_automation()
