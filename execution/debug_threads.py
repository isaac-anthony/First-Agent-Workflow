import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add execution to path
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from gmail_client import GmailClient
from google_sheets_client import GoogleSheetsClient

def debug_threads(tab_name):
    sheets = GoogleSheetsClient(os.getenv('GOOGLE_SHEETS_ID'))
    gmail = GmailClient()
    
    rows = sheets.get_all_values(tab_name)
    headers = rows[0]
    lead_rows = rows[1:]
    
    biz_col = headers.index('Business Name')
    email_col = headers.index('Email')
    status_col = headers.index('Status')
    
    print(f"--- DEBUGGING THREADS FOR {tab_name} ---")
    for row in lead_rows:
        biz = row[biz_col]
        email = row[email_col]
        status = row[status_col] if len(row) > status_col else ""
        
        short_biz = " ".join(biz.split()[:3]).replace("|", "").strip()
        query = f'"{short_biz}"'
        threads = gmail.search_threads(query)
        print(f"Lead: {biz}")
        print(f"  Threads Found: {len(threads)}")
        
        if threads:
            thread_id = threads[0]['id']
            details = gmail.get_thread_details(thread_id)
            messages = details.get('messages', [])
            print(f"  Messages in latest thread: {len(messages)}")
            for i, msg in enumerate(messages):
                m_headers = msg.get('payload', {}).get('headers', [])
                sender = next((h['value'] for h in m_headers if h['name'].lower() == 'from'), "Unknown")
                print(f"    Message {i}: From {sender}")
                if i >= len(messages) - 2: # Show last two messages (reply + agent draft)
                    snippet = msg.get('snippet', '')
                    print(f"      Snippet: {snippet}")
        print("-" * 30)

if __name__ == "__main__":
    debug_threads("Real_Estate_Riverside")
