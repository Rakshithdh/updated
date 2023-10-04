import hashlib
import json
from time import time
from flask import Flask, request, render_template, session, redirect, url_for


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash="1", proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block in the blockchain.

        :param proof: The proof of work for this block
        :param previous_hash: Hash of the previous block (optional)
        :return: New block
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]) if self.chain else None,
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, Patient_Name,Gender,DOB,Address, Mail, Mobile_Number, Blood_Grp,Medical_History,Current_Illness):
        """
        Create a new transaction to be added to the next mined block.


   
        """
        self.current_transactions.append({
            "sender": sender,
            "Patient_Name": Patient_Name,
            "Gender": Gender,
            "DOB": DOB,
            "Address": Address,
            "Mail": Mail,
            "Mobile_Number": Mobile_Number,
            "Blood_Group": Blood_Grp,
            "Medical_History": Medical_History,
            "Current_Illness": Current_Illness,

        })

        return self.last_block["index"] + 1

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a block.

        :param block: Block
        :return: Hash in hexadecimal format
        """
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    @property
    def last_block(self):
        """
        Return the last block in the blockchain.

        :return: Last block
        """
        return self.chain[-1]

# Initialize Flask
app = Flask(__name__)

# Initialize the blockchain
blockchain = Blockchain()
app.secret_key = 'your_secret_key'
users = {"rakshith": "qwerty", "Dhiviyaa":"blockchain"}

@app.route("/", methods=["GET"])
def index():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session['username'] = username  # Store the username in the session
            return redirect(url_for('index'))

        return "Invalid login credentials. Please try again."

    return render_template('login.html')


@app.route("/logout", methods=["GET"])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
            

@app.route("/mine", methods=["GET"])
def mine():
    # Proof of work algorithm (for simplicity, we'll use a fixed value here)
    proof = 12345

    # Check if there are transactions to include in the block
    if not blockchain.current_transactions:
        return "No blocks to mine", 400

    # Create a new block and add it to the blockchain
    previous_hash = blockchain.hash(blockchain.last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "New block mined",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }
    return json.dumps(response), 200

@app.route("/mineblock", methods=["GET"])
def mine_block():
    return render_template('mineblock.html')

@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    if 'username' not in session:
        return "You must be logged in to create a transaction.", 401

    # Use the logged-in username as both sender and recipient
    username = session['username']

    if request.is_json:
        # Handle JSON request
        data = request.get_json()
        data['sender'] = username
    else:
        # Handle form data request
        data = {
            'sender': username,
            'Patient_Name': request.form.get("Patient_Name"),
            'Gender':request.form.get("Gender"),
            'DOB':request.form.get("DOB"),
            'Address':request.form.get("Address"),
            'Mail': request.form.get("Mail"),
            'Mobile_Number': request.form.get("Mobile_Number"),
            'Blood_Group': request.form.get("Blood_group"),
            'Medical_History':request.form.get("Medical_History"),
            'Current_Illness':request.form.get("Current_Illness"),
        
        }

    # if not data['data']:
    #     return "Missing required data field", 400

    index = blockchain.new_transaction(data['sender'], data['Patient_Name'], data['Gender'],data['DOB'],data['Address'],data['Mail'],data['Mobile_Number'],data['Blood_Group'],data['Medical_History'],data['Current_Illness'],)
    # response = {"message": f"Transaction will be added to block {index}",}
    # return json.dumps(response), 201
    return render_template('transaction_details.html', transaction_data=data, index=index)



@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return json.dumps(response), 200

@app.route("/block", methods=["GET"])
def get_block_data_ui():
    """
    Retrieve data from a specific block by its index and display it on the UI.
    """
    block_index = int(request.args.get("block_index", -1))

    if block_index < 1 or block_index > len(blockchain.chain):
        return "Block not found", 404

    block = blockchain.chain[block_index - 1]  # Adjust the index to match Python's zero-based indexing
    block_data = {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }

    # Generate an HTML response to display the block data
    response_html = f"""
    <html>
        <head>
        <style>
        </head>
        <body>
            <h1>Data from Block {block_index}</h1>
            <pre>{json.dumps(block_data, indent=4)}</pre>
            <p><a href="/retrieve">Back to Retrieve Data</a></p>
        </body>
    </html>"""

    return response_html, 200


@app.route("/retrieve", methods=["GET"])
def retrieve_data_page():
    return render_template('retrieve.html')



if __name__ == "__main__":
    app.run(host="192.168.0.8", port=5000, debug=True)
