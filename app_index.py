from flask import Flask, request, jsonify, render_template, make_response
import mysql.connector
import csv
from io import StringIO
from flask_cors import CORS

# Initialize Flask app (ONCE)
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Test@123',
    'database': 'zomato'
}

def create_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/orders_page')
def orders_page():
    connection = None
    cursor = None
    try:
        # Test database connection first
        connection = create_connection()
        if not connection.is_connected():
            return "Failed to connect to database", 500
            
        cursor = connection.cursor(dictionary=True)
        
        # First check if tables exist
        cursor.execute("SHOW TABLES LIKE 'orders'")
        if not cursor.fetchone():
            return "Orders table doesn't exist", 500
            
        cursor.execute("SHOW TABLES LIKE 'items'")
        if not cursor.fetchone():
            return "Items table doesn't exist", 500
            
        # Count orders to verify data exists
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        order_count = cursor.fetchone()['count']
        print(f"Found {order_count} orders in database")  # Check console
        
        # Modified query with simpler fields for testing
        cursor.execute("""
            SELECT 
                o.order_id, 
                o.order_date, 
                o.delivery_address, 
                i.item_name, 
                i.price, 
                o.quantity,
                (i.price * o.quantity) as total_price
            FROM orders o
            JOIN items i ON o.item_id = i.item_id
            ORDER BY o.order_id DESC
            LIMIT 10
        """)
        orders = cursor.fetchall()
        
        print("Sample orders:", orders)  # Check console for this output
        
        if not orders:
            return render_template('orders.html', orders=None, error="No orders found in database")
            
        return render_template('orders.html', orders=orders)
        
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return render_template('orders.html', orders=None, error=f"Database error: {err}")
    except Exception as e:
        print("General Error:", e)
        return render_template('orders.html', orders=None, error=f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/place_order', methods=['POST'])
def place_order():
    cursor = None
    connection = None
    try:
        order_data = request.get_json()
        cart = order_data['cart']
        address = order_data['address']

        if not cart or not address:
            return jsonify({"error": "Cart is empty or address is missing."}), 400

        connection = create_connection()
        cursor = connection.cursor()

        for item in cart:
            cursor.execute("SELECT item_id FROM items WHERE item_name = %s", (item['name'],))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": f"Item {item['name']} not found."}), 400

            item_id = result[0]
            user_id = 1  # Default user for demo

            sql = """
                INSERT INTO orders (user_id, item_id, quantity, delivery_address)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, item_id, item['quantity'], address))

        connection.commit()
        return jsonify({"message": "Order placed successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/orders', methods=['GET'])
def get_orders():
    cursor = None
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                o.order_id, 
                o.order_date, 
                o.delivery_address, 
                i.item_name, 
                CAST(i.price AS DECIMAL(10,2)) as price, 
                o.quantity, 
                CAST((i.price * o.quantity) AS DECIMAL(10,2)) as total_price
            FROM orders o
            JOIN items i ON o.item_id = i.item_id
            ORDER BY o.order_id DESC
        """)
        orders = cursor.fetchall()
        return jsonify({"orders": orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    cursor = None
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        connection.commit()
        return jsonify({"message": "Order deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/export_orders_csv')
def export_orders_csv():
    cursor = None
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                o.order_id, 
                o.order_date, 
                o.delivery_address, 
                i.item_name, 
                CAST(i.price AS DECIMAL(10,2)) as price, 
                o.quantity, 
                CAST((i.price * o.quantity) AS DECIMAL(10,2)) as total_price
            FROM orders o
            JOIN items i ON o.item_id = i.item_id
            ORDER BY o.order_id DESC
        """)
        orders = cursor.fetchall()

        # Create CSV in memory
        si = StringIO()
        cw = csv.writer(si)
        
        # Write header
        cw.writerow(['Order ID', 'Order Date', 'Delivery Address', 
                    'Item Name', 'Price', 'Quantity', 'Total Price'])
        
        # Write data
        for order in orders:
            cw.writerow([
                order['order_id'],
                order['order_date'].strftime('%Y-%m-%d %H:%M:%S'),
                order['delivery_address'],
                order['item_name'],
                order['price'],
                order['quantity'],
                order['total_price']
            ])

        # Create response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=orders_export.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/test_orders')
def test_orders():
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders LIMIT 5")
        orders = cursor.fetchall()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)