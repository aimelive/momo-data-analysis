# dsa/parse_xml.py
# Usage: python dsa/parse_xml.py ../modified_sms_v2.xml ../data/transactions.json

import sys
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

TXID_RE = re.compile(r'(?:TxId[:\s]*|Financial Transaction Id[:\s]*)([A-Za-z0-9\-]+)', re.IGNORECASE)
AMOUNT_RE = re.compile(r'([0-9]{1,3}(?:[,\.][0-9]{3})*(?:\.\d+)?)[\s]*RWF', re.IGNORECASE)
SENDER_RE = re.compile(r'from\s+([A-Za-z0-9 \-\.\']+?)\s*(?:\(|on|TxId|has|to)', re.IGNORECASE)
RECEIVER_RE = re.compile(r'to\s+([A-Za-z0-9 \-\.\']+?)\s*(?:\d+|\(|has|at)', re.IGNORECASE)
DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})')

def parse_sms_body(body):
    # Extract tx id
    txid = None
    m = TXID_RE.search(body)
    if m:
        txid = m.group(1).strip().rstrip('.')
    # amount
    amount = None
    m = AMOUNT_RE.search(body.replace(',', ''))
    if m:
        try:
            amount = float(m.group(1).replace(',', ''))
        except:
            amount = None
    # sender
    sender = None
    m = SENDER_RE.search(body)
    if m:
        sender = m.group(1).strip()
    # receiver
    receiver = None
    m = RECEIVER_RE.search(body)
    if m:
        receiver = m.group(1).strip()
    # timestamp from body
    tx_time = None
    m = DATE_RE.search(body)
    if m:
        try:
            tx_time = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S').isoformat()
        except:
            tx_time = None

    # fallback tx_id generate short id using timestamp if missing
    return {
        'transaction_id': txid,
        'amount': amount,
        'sender': sender,
        'receiver': receiver,
        'tx_timestamp': tx_time
    }

def parse_xml_to_json(xml_path, out_json):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    records = []
    for sms in root.findall('sms'):
        attrs = sms.attrib
        body = attrs.get('body', '')
        parsed = parse_sms_body(body)
        # construct transaction object combining attributes and parsed fields
        tx = {
            'sms_id': int(attrs.get('protocol', '0')) ^ 0,   # placeholder mapping (keep sms meta)
            'raw_address': attrs.get('address'),
            'raw_date': attrs.get('date'),
            'readable_date': attrs.get('readable_date'),
            'service_center': attrs.get('service_center'),
            'body': body,
            'contact_name': attrs.get('contact_name')
        }
        # attach parsed
        tx.update(parsed)
        if not tx['transaction_id']:
            tx['transaction_id'] = f"GEN-{tx['raw_date']}-{len(records)+1}"
        if tx['amount'] is None:
            # try to find digits in body if earlier failed
            nums = re.findall(r'([0-9]{1,3}(?:[,\.][0-9]{3})*(?:\.\d+)?)', body)
            if nums:
                try:
                    tx['amount'] = float(nums[0].replace(',', ''))
                except:
                    tx['amount'] = None
        records.append(tx)
    # write JSON
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(records)} records to {out_json}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python dsa/parse_xml.py path/to/modified_sms_v2.xml path/to/out_transactions.json")
        sys.exit(1)
    parse_xml_to_json(sys.argv[1], sys.argv[2])
