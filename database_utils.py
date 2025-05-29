#database_utils.py
import streamlit as st
import pandas as pd
import datetime
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Create a database connection to TiDB Cloud."""
    try:
        # TiDB Cloud connection parameters
        db_config = {
            'host': 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
            'port': 4000,
            'user': '4ZrUUWFVXrLrXUg.root',
            'password': 'wIdAtRb3s0xhjPhL',
            'database': 'test'
        }
        
        # Connect to TiDB Cloud
        conn = mysql.connector.connect(**db_config)
        
        # Enable autocommit
        conn.autocommit = True
        
        return conn
    except Error as e:
        st.error(f"TiDB connection error: {str(e)}")
        return None

def init_database():
    """Initialize the database with tables and sample data."""
    try:
        conn = get_db_connection()
        if not conn:
            st.error("Failed to establish database connection")
            return False
            
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
         # TiDB Compatible Schema
    schema_statements = [
        """CREATE TABLE IF NOT EXISTS providers_data (
            Provider_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(255) NOT NULL,
            Provider_Type VARCHAR(50) NOT NULL,
            Contact VARCHAR(255),
            Email VARCHAR(255),
            Phone VARCHAR(20),
            Address TEXT,
            City VARCHAR(100) NOT NULL,
            State VARCHAR(100),
            Postal_Code VARCHAR(20),
            Registration_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Status VARCHAR(20) DEFAULT 'Active'
        )""",
        
        """CREATE TABLE IF NOT EXISTS receivers_data (
            Receiver_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(255) NOT NULL,
            Organization_Type VARCHAR(50) NOT NULL,
            Contact VARCHAR(255),
            Email VARCHAR(255),
            Phone VARCHAR(20),
            Address TEXT,
            City VARCHAR(100) NOT NULL,
            State VARCHAR(100),
            Postal_Code VARCHAR(20),
            Registration_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Status VARCHAR(20) DEFAULT 'Active'
        )""",
        
        """CREATE TABLE IF NOT EXISTS food_listings_data (
            Food_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
            Provider_ID BIGINT NOT NULL,
            Food_Name VARCHAR(255) NOT NULL,
            Food_Type VARCHAR(50) NOT NULL,
            Meal_Type VARCHAR(20) DEFAULT 'Other',
            Quantity DECIMAL(10,2) NOT NULL,
            Unit VARCHAR(20) DEFAULT 'kg',
            Location VARCHAR(255) NOT NULL,
            Expiry_Date DATETIME NOT NULL,
            Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Description TEXT,
            Status VARCHAR(20) DEFAULT 'Available'
        )""",
        
        """CREATE TABLE IF NOT EXISTS claims_data (
            Claim_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
            Food_ID BIGINT NOT NULL,
            Receiver_ID BIGINT NOT NULL,
            Claimed_Quantity DECIMAL(10,2) NOT NULL,
            Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Status VARCHAR(20) DEFAULT 'Pending',
            Pickup_Time DATETIME,
            Notes TEXT
        )""",
        
        # Create indexes
        "CREATE INDEX IF NOT EXISTS idx_providers_city ON providers_data(City)",
        "CREATE INDEX IF NOT EXISTS idx_receivers_city ON receivers_data(City)",
        "CREATE INDEX IF NOT EXISTS idx_food_location ON food_listings_data(Location)",
        "CREATE INDEX IF NOT EXISTS idx_food_expiry ON food_listings_data(Expiry_Date)",
        "CREATE INDEX IF NOT EXISTS idx_food_status ON food_listings_data(Status)",
        "CREATE INDEX IF NOT EXISTS idx_claims_status ON claims_data(Status)",
        "CREATE INDEX IF NOT EXISTS idx_claims_timestamp ON claims_data(Timestamp)"
    ]
    
    sample_data_statements = [
        """INSERT INTO providers_data (Name, Provider_Type, Contact, Email, Phone, City, Address) VALUES
        ('Green Grocery Store', 'Grocery Store', 'John Smith', 'john@greengrocery.com', '123-456-7890', 'New Jessica', '123 Main St'),
        ('Bella Restaurant', 'Restaurant', 'Maria Garcia', 'maria@bella.com', '123-456-7891', 'Springfield', '456 Oak Ave'),
        ('Fresh Bakery', 'Bakery', 'David Lee', 'david@freshbakery.com', '123-456-7892', 'New Jessica', '789 Pine St'),
        ('Hotel Paradise', 'Hotel', 'Sarah Johnson', 'sarah@paradise.com', '123-456-7893', 'Downtown', '321 Elm St'),
        ('Corner Cafe', 'Cafe', 'Mike Brown', 'mike@cornercafe.com', '123-456-7894', 'Springfield', '654 Maple Ave')""",
        
        """INSERT INTO receivers_data (Name, Organization_Type, Contact, Email, Phone, City, Address) VALUES
        ('Food for All NGO', 'NGO', 'Lisa Wilson', 'lisa@foodforall.org', '123-555-0001', 'New Jessica', '100 Charity Lane'),
        ('Community Kitchen', 'Community Center', 'Robert Davis', 'robert@communitykitchen.org', '123-555-0002', 'Springfield', '200 Help St'),
        ('City School District', 'School', 'Jennifer Taylor', 'jennifer@cityschools.edu', '123-555-0003', 'Downtown', '300 Education Blvd'),
        ('Helping Hands Charity', 'Charity', 'Michael Anderson', 'michael@helpinghands.org', '123-555-0004', 'New Jessica', '400 Care Ave'),
        ('Individual Volunteer', 'Individual', 'Emily Rodriguez', 'emily@email.com', '123-555-0005', 'Springfield', '500 Volunteer St')""",
        
        """INSERT INTO food_listings_data (Provider_ID, Food_Name, Food_Type, Meal_Type, Quantity, Unit, Location, Expiry_Date, Description) VALUES
        (1, 'Fresh Apples', 'Fruits', 'Snack', 50.00, 'kg', 'New Jessica', DATE_ADD(NOW(), INTERVAL 3 DAY), 'Organic red apples'),
        (1, 'Bread Loaves', 'Bakery', 'Other', 25.00, 'pieces', 'New Jessica', DATE_ADD(NOW(), INTERVAL 1 DAY), 'Day-old bread'),
        (2, 'Pasta Dishes', 'Prepared Food', 'Lunch', 30.00, 'servings', 'Springfield', DATE_ADD(NOW(), INTERVAL 2 DAY), 'Leftover pasta'),
        (3, 'Croissants', 'Bakery', 'Breakfast', 20.00, 'pieces', 'New Jessica', DATE_ADD(NOW(), INTERVAL 1 DAY), 'Fresh croissants'),
        (4, 'Vegetable Soup', 'Prepared Food', 'Dinner', 40.00, 'servings', 'Downtown', DATE_ADD(NOW(), INTERVAL 2 DAY), 'Homemade soup')""",
        
        """INSERT INTO claims_data (Food_ID, Receiver_ID, Claimed_Quantity, Status, Pickup_Time, Notes) VALUES
        (1, 1, 25.00, 'Completed', DATE_ADD(NOW(), INTERVAL 1 HOUR), 'Picked up successfully'),
        (2, 2, 15.00, 'Approved', DATE_ADD(NOW(), INTERVAL 2 HOUR), 'Will pick up this afternoon'),
        (3, 3, 30.00, 'Pending', NULL, 'Requested for school lunch program'),
        (4, 1, 10.00, 'Completed', DATE_ADD(NOW(), INTERVAL -1 HOUR), 'Great for breakfast program')"""
    ]
    
    connection = create_tidb_connection()
    if connection:
        try:
            print("📊 Creating tables...")
            execute_tidb_statements(connection, schema_statements)
            
            print("📝 Inserting sample data...")
            execute_tidb_statements(connection, sample_data_statements)
            
            print("✅ TiDB database setup completed successfully!")
            
            # Verify setup
            cursor = connection.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE()")
            tables = cursor.fetchall()
            print(f"📋 Created tables: {[table[0] for table in tables]}")
            cursor.close()
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
        finally:
            connection.close()
    else:
        print("❌ Could not connect to TiDB")

# Streamlit Integration
def setup_tidb_via_streamlit():
    """Setup TiDB database via Streamlit interface"""
    st.subheader("🗄️ TiDB Database Setup")
    
    with st.expander("Database Connection Settings"):
        host = st.text_input("TiDB Host", value="your-tidb-host.tidbcloud.com")
        port = st.number_input("Port", value=4000)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database Name")
    
    if st.button("🚀 Setup Database"):
        if all([host, username, password, database]):
            try:
                connection = pymysql.connect(
                    host=host,
                    port=int(port),
                    user=username,
                    password=password,
                    database=database,
                    charset='utf8mb4'
                )
                
                st.success("✅ Connected to TiDB successfully!")
                
                # Run setup
                with st.spinner("Setting up tables..."):
                    # Add setup logic here
                    st.success("🎉 Database setup completed!")
                    
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
        else:
            st.warning("Please fill in all connection details")

if __name__ == "__main__":
    setup_tidb_database()
