import streamlit as st
import pandas as pd
import datetime
from database_utils import get_db_connection, load_food_data
from mysql.connector import Error
import traceback

# ─────────────────────────────────────────────────────────────────────────────
# CRUD OPERATIONS - DEBUGGED VERSION
# ─────────────────────────────────────────────────────────────────────────────

def add_food():
    """Add a new food listing to the database."""
    st.subheader("➕ Add New Food Listing")

    with st.form("add_food_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            food_name = st.text_input("Food Name*", help="Required field")
            quantity = st.number_input("Quantity", min_value=1, value=1)
            expiry = st.date_input("Expiry Date", min_value=datetime.date.today())
            provider_id = st.number_input("Provider ID", min_value=1, value=1)
        
        with col2:
            provider_type = st.selectbox("Provider Type", 
                ["Restaurant", "Grocery Store", "Supermarket", "Bakery", "Hotel", "Farm"])
            location = st.text_input("Location*", help="Required field")
            food_type = st.selectbox("Food Type", 
                ["Vegetarian", "Non-Vegetarian", "Vegan", "Dairy", "Gluten-Free", "Organic"])
            meal_type = st.selectbox("Meal Type", 
                ["Breakfast", "Lunch", "Dinner", "Snacks", "Dessert", "Beverage"])

        submit_button = st.form_submit_button("Add Food", use_container_width=True)

        if submit_button:
            # Debug: Show what data we're trying to insert
            st.write("**Debug Info:**")
            debug_data = {
                "Food Name": food_name,
                "Quantity": quantity,
                "Expiry Date": expiry,
                "Provider ID": provider_id,
                "Provider Type": provider_type,
                "Location": location,
                "Food Type": food_type,
                "Meal Type": meal_type
            }
            st.json(debug_data)
            
            # Validation
            if not food_name or not food_name.strip():
                st.error("❌ Food name is required!")
                return
            
            if not location or not location.strip():
                st.error("❌ Location is required!")
                return
            
            try:
                with st.spinner("Adding food item..."):
                    conn = get_db_connection()
                    if not conn:
                        st.error("❌ Failed to connect to database")
                        return
                    
                    cursor = conn.cursor()
                    
                    # Check if the table exists and show its structure
                    cursor.execute("DESCRIBE food_listings")
                    table_structure = cursor.fetchall()
                    with st.expander("Database Table Structure (Debug)"):
                        st.write(table_structure)
                    
                    # Insert the data
                    insert_query = """
                        INSERT INTO food_listings 
                        (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_query, 
                        (food_name.strip(), quantity, expiry, provider_id, 
                         provider_type, location.strip(), food_type, meal_type))
                    
                    conn.commit()
                    new_id = cursor.lastrowid
                    
                    cursor.close()
                    conn.close()
                    
                    st.success(f"✅ Food item added successfully! New ID: {new_id}")
                    
                    # Clear cached data
                    if "food_data" in st.session_state:
                        del st.session_state["food_data"]
                    
                    # Wait a moment then rerun
                    st.balloons()
                    st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
                    
            except Error as e:
                st.error(f"❌ Database Error: {str(e)}")
                st.code(f"Error Code: {e.errno}\nSQL State: {e.sqlstate}")
            except Exception as e:
                st.error(f"❌ Unexpected Error: {str(e)}")
                st.code(traceback.format_exc())

def update_food():
    """Update an existing food listing."""
    st.subheader("✏️ Update Existing Food Listing")
    
    try:
        # Load fresh data
        with st.spinner("Loading food data..."):
            food_data = load_food_data()
        
        # Debug: Show data loading status
        st.write(f"**Debug:** Loaded {len(food_data)} food items")
        
        if food_data.empty:
            st.info("📝 No food listings available to update.")
            return
        
        # Show current data
        with st.expander("📋 Current Food Listings", expanded=False):
            st.dataframe(food_data, use_container_width=True)
        
        # Clean and prepare data
        food_data = food_data.copy()
        food_data['Food_ID'] = pd.to_numeric(food_data['Food_ID'], errors='coerce')
        food_data = food_data.dropna(subset=['Food_ID'])
        food_data['Food_ID'] = food_data['Food_ID'].astype(int)
        
        if len(food_data) == 0:
            st.error("❌ No valid food items found (Food_ID issues)")
            return
        
        # Create selection options
        food_options = {}
        for _, row in food_data.iterrows():
            key = f"ID: {int(row['Food_ID'])} - {row['Food_Name']}"
            food_options[key] = int(row['Food_ID'])
        
        selected_option = st.selectbox(
            "Select Food to Update", 
            list(food_options.keys()),
            key="update_selectbox"
        )
        
        selected_id = food_options[selected_option]
        selected_item = food_data[food_data["Food_ID"] == selected_id].iloc[0]
        
        # Show current details
        st.write("### 📝 Current Details:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Food Name:** {selected_item['Food_Name']}")
            st.info(f"**Quantity:** {selected_item['Quantity']}")
        with col2:
            st.info(f"**Expiry Date:** {selected_item['Expiry_Date']}")
            st.info(f"**Location:** {selected_item.get('Location', 'N/A')}")
        with col3:
            st.info(f"**Food Type:** {selected_item.get('Food_Type', 'N/A')}")
            st.info(f"**Meal Type:** {selected_item.get('Meal_Type', 'N/A')}")
        
        st.divider()
        
        # Update form
        with st.form(key=f"update_form_{selected_id}"):
            st.write("### ✏️ Update Details:")
            update_col1, update_col2 = st.columns(2)
            
            with update_col1:
                updated_name = st.text_input(
                    "Food Name*", 
                    value=str(selected_item.get("Food_Name", "")),
                    key=f"name_{selected_id}"
                )
                
                current_quantity = int(selected_item.get("Quantity", 1))
                updated_quantity = st.number_input(
                    "Quantity", 
                    min_value=1, 
                    value=current_quantity,
                    key=f"qty_{selected_id}"
                )
                
                # Handle expiry date
                try:
                    if pd.isna(selected_item["Expiry_Date"]):
                        current_expiry = datetime.date.today()
                    elif isinstance(selected_item["Expiry_Date"], str):
                        current_expiry = datetime.datetime.strptime(
                            selected_item["Expiry_Date"], "%Y-%m-%d"
                        ).date()
                    else:
                        current_expiry = selected_item["Expiry_Date"]
                except:
                    current_expiry = datetime.date.today()
                
                updated_expiry = st.date_input(
                    "Expiry Date", 
                    value=current_expiry,
                    key=f"exp_{selected_id}"
                )
            
            with update_col2:
                updated_location = st.text_input(
                    "Location*", 
                    value=str(selected_item.get("Location", "")),
                    key=f"loc_{selected_id}"
                )
                
                food_types = ["Vegetarian", "Non-Vegetarian", "Vegan", "Dairy", "Gluten-Free", "Organic"]
                current_food_type = str(selected_item.get("Food_Type", "Vegetarian"))
                food_type_index = food_types.index(current_food_type) if current_food_type in food_types else 0
                updated_food_type = st.selectbox(
                    "Food Type", 
                    food_types, 
                    index=food_type_index,
                    key=f"ftype_{selected_id}"
                )
                
                meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks", "Dessert", "Beverage"]
                current_meal_type = str(selected_item.get("Meal_Type", "Breakfast"))
                meal_type_index = meal_types.index(current_meal_type) if current_meal_type in meal_types else 0
                updated_meal_type = st.selectbox(
                    "Meal Type", 
                    meal_types, 
                    index=meal_type_index,
                    key=f"mtype_{selected_id}"
                )
            
            update_button = st.form_submit_button("🔄 Update Food Item", use_container_width=True)
            
            if update_button:
                # Validation
                if not updated_name or not updated_name.strip():
                    st.error("❌ Food name is required!")
                    return
                
                if not updated_location or not updated_location.strip():
                    st.error("❌ Location is required!")
                    return
                
                try:
                    with st.spinner("Updating food item..."):
                        conn = get_db_connection()
                        if not conn:
                            st.error("❌ Failed to connect to database")
                            return
                        
                        cursor = conn.cursor()
                        
                        update_query = """
                            UPDATE food_listings 
                            SET Food_Name = %s, Quantity = %s, Expiry_Date = %s, 
                                Location = %s, Food_Type = %s, Meal_Type = %s
                            WHERE Food_ID = %s
                        """
                        
                        cursor.execute(update_query, (
                            updated_name.strip(), updated_quantity, updated_expiry, 
                            updated_location.strip(), updated_food_type, updated_meal_type, 
                            selected_id
                        ))
                        
                        rows_affected = cursor.rowcount
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        if rows_affected > 0:
                            st.success(f"✅ Food item #{selected_id} updated successfully!")
                            if "food_data" in st.session_state:
                                del st.session_state["food_data"]
                            st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
                        else:
                            st.warning(f"⚠️ No changes made to food item #{selected_id}")
                        
                except Error as e:
                    st.error(f"❌ Database Error: {str(e)}")
                    st.code(f"Error Code: {e.errno}\nSQL State: {e.sqlstate}")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {str(e)}")
                    st.code(traceback.format_exc())
    
    except Exception as e:
        st.error(f"❌ Error in update function: {str(e)}")
        st.code(traceback.format_exc())

def delete_food():
    """Delete a food listing from the database."""
    st.subheader("🗑️ Delete Food Listing")
    
    try:
        # Load fresh data
        with st.spinner("Loading food data..."):
            food_data = load_food_data()
        
        st.write(f"**Debug:** Loaded {len(food_data)} food items")
        
        if food_data.empty:
            st.info("📝 No food listings available to delete.")
            return
        
        # Show current data
        with st.expander("📋 Current Food Listings", expanded=False):
            st.dataframe(food_data, use_container_width=True)
        
        # Clean data
        food_data = food_data.copy()
        food_data['Food_ID'] = pd.to_numeric(food_data['Food_ID'], errors='coerce')
        food_data = food_data.dropna(subset=['Food_ID'])
        food_data['Food_ID'] = food_data['Food_ID'].astype(int)
        
        if len(food_data) == 0:
            st.error("❌ No valid food items found")
            return
        
        # Create selection options
        food_options = {}
        for _, row in food_data.iterrows():
            key = f"ID: {int(row['Food_ID'])} - {row['Food_Name']}"
            food_options[key] = int(row['Food_ID'])
        
        selected_option = st.selectbox(
            "Select Food to Delete", 
            list(food_options.keys()),
            key="delete_selectbox"
        )
        
        selected_id = food_options[selected_option]
        selected_item = food_data[food_data["Food_ID"] == selected_id].iloc[0]
        
        # Show details
        st.write("### 📋 Food Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Food Name:** {selected_item['Food_Name']}")
            st.info(f"**Quantity:** {selected_item['Quantity']}")
        with col2:
            st.info(f"**Expiry Date:** {selected_item['Expiry_Date']}")
            st.info(f"**Location:** {selected_item.get('Location', 'N/A')}")
        with col3:
            st.info(f"**Food Type:** {selected_item.get('Food_Type', 'N/A')}")
            st.info(f"**Meal Type:** {selected_item.get('Meal_Type', 'N/A')}")
        
        st.divider()
        
        # Confirmation
        st.error("⚠️ **WARNING:** This action cannot be undone!")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ Yes, Delete This Item", type="primary", use_container_width=True):
                try:
                    with st.spinner("Deleting food item..."):
                        conn = get_db_connection()
                        if not conn:
                            st.error("❌ Failed to connect to database")
                            return
                        
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM food_listings WHERE Food_ID = %s", (selected_id,))
                        
                        rows_affected = cursor.rowcount
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        if rows_affected > 0:
                            st.success(f"✅ Food item #{selected_id} deleted successfully!")
                            if "food_data" in st.session_state:
                                del st.session_state["food_data"]
                            st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
                        else:
                            st.warning(f"⚠️ No food item with ID #{selected_id} found")
                            
                except Error as e:
                    st.error(f"❌ Database Error: {str(e)}")
                    st.code(f"Error Code: {e.errno}\nSQL State: {e.sqlstate}")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {str(e)}")
                    st.code(traceback.format_exc())
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.info("Delete operation cancelled")
    
    except Exception as e:
        st.error(f"❌ Error in delete function: {str(e)}")
        st.code(traceback.format_exc())

# ─────────────────────────────────────────────────────────────────────────────
# DEBUGGING HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def test_database_connection():
    """Test database connection and show table info."""
    st.subheader("🔧 Database Connection Test")
    
    try:
        conn = get_db_connection()
        if conn:
            st.success("✅ Database connection successful!")
            
            cursor = conn.cursor()
            
            # Show table structure
            cursor.execute("DESCRIBE food_listings")
            table_structure = cursor.fetchall()
            
            st.write("**Table Structure:**")
            df = pd.DataFrame(table_structure, columns=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra'])
            st.dataframe(df)
            
            # Show record count
            cursor.execute("SELECT COUNT(*) FROM food_listings")
            count = cursor.fetchone()[0]
            st.write(f"**Total Records:** {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute("SELECT * FROM food_listings LIMIT 5")
                sample_data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                sample_df = pd.DataFrame(sample_data, columns=columns)
                st.write("**Sample Data:**")
                st.dataframe(sample_df)
            
            cursor.close()
            conn.close()
        else:
            st.error("❌ Failed to connect to database")
            
    except Exception as e:
        st.error(f"❌ Database test failed: {str(e)}")
        st.code(traceback.format_exc())
