from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from db import get_connection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


@app.route('/', methods=['GET'])
def check_backend_on():
    return jsonify({"status": "success", "message": "Backend is on !"})

# Route to check DB connection
@app.route('/check-db', methods=['GET'])
def check_db_connection():
    try:
        db_name = os.getenv("DB_NAME")
        table_name = os.getenv("TABLE_NAME")

        conn = get_connection()
        cursor = conn.cursor()

        # 1. Create Database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.database = db_name  # switch to the new database

        # 2. Create Table if not exists
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            description TEXT
        )
        """
        cursor.execute(create_table_query)

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Database and table checked/created!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        db_name = os.getenv("DB_NAME")
        table_name = os.getenv("TABLE_NAME")
        conn = get_connection()
        conn.database = db_name  # use the correct DB
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/api/data', methods=['POST'])
def insert_data():
    try:
        db_name = os.getenv("DB_NAME")
        table_name = os.getenv("TABLE_NAME")

        conn = get_connection()
        conn.database = db_name
        cursor = conn.cursor()

        # Get data from request
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        if not name or not description:
            return jsonify({"error": "Missing 'name' or 'description'"}), 400

        # Insert into the table
        cursor.execute(
            f"INSERT INTO {table_name} (name, description) VALUES (%s, %s)",
            (name, description)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Item inserted successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete an item by ID
@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_data(item_id):
    try:
        db_name = os.getenv("DB_NAME")
        table_name = os.getenv("TABLE_NAME")

        conn = get_connection()
        conn.database = db_name
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Item deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

