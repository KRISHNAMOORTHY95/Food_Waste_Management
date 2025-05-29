import streamlit as st
import pandas as pd
from database_utils import run_query

# SQL Queries for reports - 21 comprehensive queries
queries = {
    
Number of food providers in each city
SELECT City, COUNT(*) AS Provider_Count FROM providers_data GROUP BY City;

Number of food receivers in each city
SELECT City, COUNT(*) AS Receiver_Count FROM receivers_data GROUP BY City;

Provider type contributing most food
SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
FROM food_listings_data
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC
LIMIT 1;

Contact info of providers in a specific city (e.g., 'New Jessica')
SELECT Name, Contact FROM providers_data WHERE City = 'New Jessica';

 Receiver with the most food claims
SELECT Receiver_ID, COUNT(*) AS Total_Claims
FROM claims_data
GROUP BY Receiver_ID
ORDER BY Total_Claims DESC
LIMIT 1;

Total quantity of food available
SELECT SUM(Quantity) AS Total_Quantity FROM food_listings_data;

City with the highest number of food listings
SELECT Location AS City, COUNT(*) AS Listing_Count
FROM food_listings_data
GROUP BY Location
ORDER BY Listing_Count DESC
LIMIT 1;

 Most commonly available food types
SELECT Food_Type, COUNT(*) AS Frequency
FROM food_listings_data
GROUP BY Food_Type
ORDER BY Frequency DESC;

Number of food claims per food item
SELECT Food_ID, COUNT(*) AS Claims_Count
FROM claims_data
GROUP BY Food_ID
ORDER BY Claims_Count DESC;

Provider with the highest number of completed food claims
SELECT fl.Provider_ID, COUNT(*) AS Completed_Claims
FROM claims_data c
JOIN food_listings_data fl ON c.Food_ID = fl.Food_ID
WHERE c.Status = 'Completed'
GROUP BY fl.Provider_ID
ORDER BY Completed_Claims DESC
LIMIT 1;

Percentage of food claims by status
SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data) AS Percentage
FROM claims_data
GROUP BY Status;

Average quantity of food claimed per receiver
SELECT c.Receiver_ID, AVG(fl.Quantity) AS Avg_Quantity_Claimed
FROM claims_data c
JOIN food_listings_data fl ON c.Food_ID = fl.Food_ID
GROUP BY c.Receiver_ID;

Most claimed meal type
SELECT fl.Meal_Type, COUNT(*) AS Claim_Count
FROM claims_data c
JOIN food_listings_data fl ON c.Food_ID = fl.Food_ID
GROUP BY fl.Meal_Type
ORDER BY Claim_Count DESC;

 Most frequently claimed food items
SELECT fl.Food_Name, COUNT(*) AS Claim_Count
FROM claims_data c
JOIN food_listings_data fl ON c.Food_ID = fl.Food_ID
GROUP BY fl.Food_Name
ORDER BY Claim_Count DESC;

 Busiest days for food claims
SELECT DATE(Timestamp) AS Claim_Date, COUNT(*) AS Total_Claims
FROM claims_data
GROUP BY Claim_Date
ORDER BY Total_Claims DESC;

 Peak hours for food claims
SELECT STRFTIME('%H', Timestamp) AS Hour, COUNT(*) AS Claims
FROM claims_data
GROUP BY Hour
ORDER BY Claims DESC;

Claim-to-donation ratio by city
WITH Claims AS (
  SELECT fl.Location AS City, COUNT(*) AS Total_Claims
  FROM claims_data c
  JOIN food_listings_data fl ON c.Food_ID = fl.Food_ID
  GROUP BY fl.Location
),
Listings AS (
  SELECT Location AS City, COUNT(*) AS Total_Listings
  FROM food_listings_data
  GROUP BY Location
)
SELECT c.City, Total_Claims, l.Total_Listings,
       ROUND(Total_Claims * 1.0 / Total_Listings, 2) AS Claim_To_Listing_Ratio
FROM Claims c
JOIN Listings l ON c.City = l.City
ORDER BY Claim_To_Listing_Ratio DESC;

Average days between listing and claim (assuming both timestamps are valid)
SELECT AVG(JULIANDAY(c.Timestamp) - JULIANDAY(fl.Expiry_Date)) AS Avg_Days_To_Claim
FROM claims_data c
JOIN food_listings_data fl ON c.Food_ID = fl.Food_ID
WHERE c.Status = 'Completed';

Provider type effectiveness (highest claim rate)
WITH Total_Listings AS (
  SELECT Provider_Type, COUNT(*) AS Listings
  FROM food_listings_data
  GROUP BY Provider_Type
),
Claimed AS (
  SELECT fl.Provider_Type, COUNT(*) AS Claims
  FROM claims_data c
  JOIN food_listings_data fl ON c.Food_ID = fl.Food_ID
  WHERE c.Status = 'Completed'
  GROUP BY fl.Provider_Type
)
SELECT t.Provider_Type, t.Listings, c.Claims,
       ROUND(c.Claims * 1.0 / t.Listings, 2) AS Effectiveness_Rate
FROM Total_Listings t
JOIN Claimed c ON t.Provider_Type = c.Provider_Type
ORDER BY Effectiveness_Rate DESC;

Average days to expiry for listed food
SELECT AVG(JULIANDAY(Expiry_Date) - JULIANDAY('now')) AS Avg_Days_To_Expire
FROM food_listings_data;

Top 5 providers with most food variety
SELECT Provider_ID, COUNT(DISTINCT Food_Name) AS Unique_Food_Items
FROM food_listings_data
GROUP BY Provider_ID
ORDER BY Unique_Food_Items DESC
LIMIT 5;
}

def show_queries():
    """Run predefined SQL queries for analysis."""
    st.subheader("📊 Query-Based Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        option = st.selectbox("Choose a report", list(queries.keys()))
    
    with col2:
        run_button = st.button("Run Query", use_container_width=True)
    
    if run_button:
        try:
            result = run_query(queries[option])
            if not result.empty:
                st.dataframe(result, use_container_width=True)
                
                # Offer to download results as CSV
                csv = result.to_csv(index=False)
                st.download_button(
                    label="Download Results",
                    data=csv,
                    file_name=f"{option}_report.csv",
                    mime="text/csv",
                )
            else:
                st.info("No data available for this query.")
        except Exception as e:
            st.error(f"Error running query: {str(e)}")
            st.code(queries[option])
