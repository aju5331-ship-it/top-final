"""
📖 Blockchain Ticketing System (Streamlit Compatible)

- Issue, transfer, redeem, and verify tickets
- Blockchain ledger prevents duplication/fraud
- Fully interactive using Streamlit UI
"""

import streamlit as st
import hashlib
import json
import time
import uuid

# ---------------- Blockchain Classes ----------------
class TicketTransaction:
    def __init__(self, tx_type, ticket_id, owner, event=None, new_owner=None):
        self.tx_type = tx_type
        self.ticket_id = ticket_id
        self.owner = owner
        self.event = event
        self.new_owner = new_owner
        self.timestamp = time.time()

    def to_dict(self):
        return self.__dict__

class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class TicketBlockchain:
    difficulty = 2

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.tickets = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine(self):
        if not self.pending_transactions:
            return None
        new_block = Block(len(self.chain), self.pending_transactions, self.chain[-1].compute_hash())
        new_block.hash = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0" * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def issue_ticket(self, owner, event):
        ticket_id = str(uuid.uuid4())
        tx = TicketTransaction("issue", ticket_id, owner, event)
        self.add_transaction(tx)
        self.tickets[ticket_id] = {"owner": owner, "status": "valid", "event": event}
        return ticket_id

    def transfer_ticket(self, ticket_id, new_owner):
        ticket = self.tickets.get(ticket_id)
        if not ticket or ticket["status"] != "valid":
            return False
        tx = TicketTransaction("transfer", ticket_id, ticket["owner"], new_owner=new_owner)
        self.add_transaction(tx)
        ticket["owner"] = new_owner
        return True

    def redeem_ticket(self, ticket_id):
        ticket = self.tickets.get(ticket_id)
        if not ticket or ticket["status"] != "valid":
            return False
        tx = TicketTransaction("redeem", ticket_id, ticket["owner"])
        self.add_transaction(tx)
        ticket["status"] = "redeemed"
        return True

    def verify_ticket(self, ticket_id):
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return None
        return ticket

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="Blockchain Ticketing System", layout="wide")
st.title("🎫 Blockchain Ticketing System")

blockchain = TicketBlockchain()

# Demo flow on startup
if "demo_done" not in st.session_state:
    st.session_state.demo_done = True
    st.subheader("Demo Flow:")
    demo_ticket = blockchain.issue_ticket("Alice", "Rock Concert")
    blockchain.mine()
    blockchain.transfer_ticket(demo_ticket, "Bob")
    blockchain.mine()
    blockchain.redeem_ticket(demo_ticket)
    blockchain.mine()
    st.write(f"Demo ticket ID: {demo_ticket} was issued, transferred, and redeemed.")

# ---------------- Issue Ticket ----------------
st.subheader("Issue Ticket")
owner = st.text_input("Owner Name", key="issue_owner")
event_name = st.text_input("Event Name", key="issue_event")
if st.button("Issue Ticket"):
    if owner and event_name:
        ticket_id = blockchain.issue_ticket(owner, event_name)
        blockchain.mine()
        st.success(f"Ticket issued! Ticket ID: {ticket_id}")
    else:
        st.warning("Please enter Owner and Event Name.")

# ---------------- Transfer Ticket ----------------
st.subheader("Transfer Ticket")
transfer_ticket_id = st.text_input("Ticket ID to Transfer", key="transfer_id")
new_owner = st.text_input("New Owner", key="transfer_owner")
if st.button("Transfer Ticket"):
    if blockchain.transfer_ticket(transfer_ticket_id, new_owner):
        blockchain.mine()
        st.success(f"Ticket {transfer_ticket_id} transferred to {new_owner}.")
    else:
        st.error("Ticket not found or already redeemed.")

# ---------------- Redeem Ticket ----------------
st.subheader("Redeem Ticket")
redeem_ticket_id = st.text_input("Ticket ID to Redeem", key="redeem_id")
if st.button("Redeem Ticket"):
    if blockchain.redeem_ticket(redeem_ticket_id):
        blockchain.mine()
        st.success(f"Ticket {redeem_ticket_id} redeemed successfully.")
    else:
        st.error("Ticket not found or already redeemed.")

# ---------------- Verify Ticket ----------------
st.subheader("Verify Ticket")
verify_ticket_id = st.text_input("Ticket ID to Verify", key="verify_id")
if st.button("Verify Ticket"):
    ticket = blockchain.verify_ticket(verify_ticket_id)
    if ticket:
        st.json(ticket)
        st.info(f"Ticket status: {ticket['status']}, Owner: {ticket['owner']}, Event: {ticket['event']}")
    else:
        st.error("Ticket not found.")

# ---------------- View Blockchain ----------------
st.subheader("Blockchain Ledger")
for block in blockchain.chain:
    st.write(f"Block Index: {block.index}, Previous Hash: {block.previous_hash}")
    st.json([tx.to_dict() for tx in block.transactions])
