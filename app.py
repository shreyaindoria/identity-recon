from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Shreeshyam@localhost/identitydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress warning messages
db = SQLAlchemy(app)

# Ensure the folder for storing logs exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Define Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    linkedId = db.Column(db.Integer, nullable=True)
    linkPrecedence = db.Column(db.Enum('primary', 'secondary', name='link_precedence'), default='primary')
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletedAt = db.Column(db.DateTime, nullable=True)

@app.route('/')
def index():
    return render_template('index.html')  # This serves the HTML file

@app.route('/identity', methods=['POST'])
@app.route('/identity', methods=['POST'])
def identify():
    data = request.get_json()

    # Check if required parameters are present
    if not data.get('email') and not data.get('phoneNumber'):
        response_data = {
            "error": "Invalid JSON data. Missing Parameters"
        }
        return jsonify(response_data), 400

    email = data.get('email')
    phoneNumber = data.get('phoneNumber')

    # Query all matching contacts
    matches = Contact.query.filter(
        (Contact.email == email) | (Contact.phoneNumber == phoneNumber)
    ).all()

    if not matches:
        # No matches, create a new primary contact
        new_contact = Contact(email=email, phoneNumber=phoneNumber, linkPrecedence='primary')
        db.session.add(new_contact)
        db.session.commit()

        response_data = {
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [email] if email else [],
                "phoneNumbers": [phoneNumber] if phoneNumber else [],
                "secondaryContactIds": []  # Empty list for secondary contacts
            }
        }
        save_request_response(data, response_data)
        return jsonify(response_data), 200

    # Handle primary and secondary contacts
    primary_contact = next((contact for contact in matches if contact.linkPrecedence == 'primary'), matches[0])

    emails = {contact.email for contact in matches if contact.email}
    phoneNumbers = {contact.phoneNumber for contact in matches if contact.phoneNumber}
    
    # Make sure secondary contacts are properly identified
    secondaryContactIds = [contact.id for contact in matches if contact.linkPrecedence == 'secondary' and contact.id != primary_contact.id]

    # Update linkPrecedence for secondary contacts
    for contact in matches:
        if contact.id != primary_contact.id:
            contact.linkPrecedence = 'secondary'
            contact.linkedId = primary_contact.id
            db.session.add(contact)

    db.session.commit()

    response_data = {
        "primaryContactId": primary_contact.id,
        "emails": list(emails),
        "phoneNumbers": list(phoneNumbers),
        "secondaryContactIds": secondaryContactIds  # List of secondary contact IDs
    }

    save_request_response(data, response_data)
    return jsonify(response_data), 200



# Function to save request and response to separate JSON files
def save_request_response(request_data, response_data):
    # Generate unique filenames using timestamps
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')

    # Define file paths
    request_file_path = os.path.join('logs', f'request_{timestamp}.json')
    response_file_path = os.path.join('logs', f'response_{timestamp}.json')

    # Save the request data as a JSON file
    with open(request_file_path, 'w') as request_file:
        json.dump(request_data, request_file, indent=4)
    
    # Save the response data as a JSON file
    with open(response_file_path, 'w') as response_file:
        json.dump(response_data, response_file, indent=4)

if __name__ == '__main__':
    # Ensure the tables are created within the app context
    with app.app_context():
        db.create_all()  # This will create the tables in the database
    app.run(debug=True)


