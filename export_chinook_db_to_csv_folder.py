#!/usr/bin/env python3
"""
Chinook Database - Pandas Integration Demo

This script demonstrates how to connect to the Chinook database using SQLite
and perform various data analysis operations with pandas.

The Chinook database represents a digital media store, including tables for
artists, albums, media tracks, invoices, and customers.
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

# Database configuration
DB_PATH = "chinook-database/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"


def connect_to_chinook():
    """Establish connection to the Chinook SQLite database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    print(f"✓ Connected to Chinook database at {DB_PATH}")
    return conn


def get_table_info(conn):
    """Get information about all tables in the database."""
    tables_query = """
    SELECT name FROM sqlite_master 
    WHERE type='table' 
    ORDER BY name;
    """
    tables = pd.read_sql_query(tables_query, conn)
    print("\n📊 Available Tables:")
    print(tables["name"].tolist())
    return tables


def load_basic_tables(conn):
    """Load main tables into pandas DataFrames."""
    tables = {}

    # Core tables to load
    table_names = [
        "Artist",
        "Album",
        "Track",
        "Customer",
        "Invoice",
        "InvoiceLine",
        "Genre",
        "MediaType",
    ]

    for table_name in table_names:
        try:
            query = f"SELECT * FROM {table_name} LIMIT 1000"  # Limit for demo purposes
            df = pd.read_sql_query(query, conn)
            tables[table_name] = df
            print(f"✓ Loaded {table_name}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading {table_name}: {e}")

    return tables


def explore_data_structure(tables):
    """Explore the structure of loaded tables."""
    print("\n🔍 Data Structure Analysis:")

    for table_name, df in tables.items():
        print(f"\n--- {table_name} ---")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

        # Show data types
        print("Data Types:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")


def basic_analytics(tables):
    """Perform basic analytics on the Chinook data."""
    print("\n📈 Basic Analytics:")

    if "Track" in tables:
        tracks = tables["Track"]
        print(f"\n🎵 Track Analysis:")
        print(f"Total tracks: {len(tracks)}")
        print(f"Average track length: {tracks['Milliseconds'].mean()/1000:.2f} seconds")
        print(f"Total tracks size: {tracks['Bytes'].sum()/(1024**3):.2f} GB")

    if "Customer" in tables:
        customers = tables["Customer"]
        print(f"\n👥 Customer Analysis:")
        print(f"Total customers: {len(customers)}")
        print("Customers by Country:")
        country_counts = customers["Country"].value_counts().head(10)
        for country, count in country_counts.items():
            print(f"  {country}: {count}")

    if "Invoice" in tables:
        invoices = tables["Invoice"]
        print(f"\n💰 Invoice Analysis:")
        print(f"Total invoices: {len(invoices)}")
        print(f"Total revenue: ${invoices['Total'].sum():.2f}")
        print(f"Average invoice amount: ${invoices['Total'].mean():.2f}")


def advanced_analytics(conn):
    """Perform advanced analytics using SQL joins with pandas."""
    print("\n🚀 Advanced Analytics:")

    # Top artists by sales
    top_artists_query = """
    SELECT 
        ar.Name as Artist,
        SUM(il.UnitPrice * il.Quantity) as TotalSales,
        COUNT(DISTINCT i.InvoiceId) as TotalInvoices,
        COUNT(il.TrackId) as TracksSOld
    FROM Artist ar
    JOIN Album al ON ar.ArtistId = al.ArtistId
    JOIN Track t ON al.AlbumId = t.AlbumId
    JOIN InvoiceLine il ON t.TrackId = il.TrackId
    JOIN Invoice i ON il.InvoiceId = i.InvoiceId
    GROUP BY ar.ArtistId, ar.Name
    ORDER BY TotalSales DESC
    LIMIT 10
    """

    top_artists = pd.read_sql_query(top_artists_query, conn)
    print("\n🎤 Top 10 Artists by Sales:")
    for _, row in top_artists.iterrows():
        print(
            f"  {row['Artist']}: ${row['TotalSales']:.2f} ({row['TracksSOld']} tracks sold)"
        )

    # Genre popularity
    genre_popularity_query = """
    SELECT 
        g.Name as Genre,
        COUNT(il.TrackId) as TracksSold,
        SUM(il.UnitPrice * il.Quantity) as Revenue
    FROM Genre g
    JOIN Track t ON g.GenreId = t.GenreId
    JOIN InvoiceLine il ON t.TrackId = il.TrackId
    GROUP BY g.GenreId, g.Name
    ORDER BY TracksSold DESC
    LIMIT 10
    """

    genre_stats = pd.read_sql_query(genre_popularity_query, conn)
    print("\n🎶 Genre Popularity:")
    for _, row in genre_stats.iterrows():
        print(
            f"  {row['Genre']}: {row['TracksSold']} tracks sold, ${row['Revenue']:.2f} revenue"
        )

    # Monthly sales trend
    monthly_sales_query = """
    SELECT 
        strftime('%Y-%m', InvoiceDate) as Month,
        SUM(Total) as MonthlySales,
        COUNT(*) as InvoiceCount
    FROM Invoice
    GROUP BY strftime('%Y-%m', InvoiceDate)
    ORDER BY Month
    """

    monthly_sales = pd.read_sql_query(monthly_sales_query, conn)
    print(f"\n📅 Monthly Sales Trend (Last 5 months):")
    for _, row in monthly_sales.tail().iterrows():
        print(
            f"  {row['Month']}: ${row['MonthlySales']:.2f} ({row['InvoiceCount']} invoices)"
        )


def pandas_operations_demo(tables):
    """Demonstrate various pandas operations on the loaded data."""
    print("\n🐼 Pandas Operations Demo:")

    if "Track" in tables and "Album" in tables and "Artist" in tables:
        tracks = tables["Track"]
        albums = tables["Album"]
        artists = tables["Artist"]

        # Merge operations
        print("\n🔗 Merging DataFrames:")
        tracks_with_albums = pd.merge(tracks, albums, on="AlbumId", how="left")
        tracks_with_artists = pd.merge(
            tracks_with_albums, artists, on="ArtistId", how="left"
        )

        print(f"Merged dataset shape: {tracks_with_artists.shape}")

        # Groupby operations
        print("\n📊 Group By Operations:")
        artist_stats = (
            tracks_with_artists.groupby("Name_y")
            .agg(
                {
                    "TrackId": "count",
                    "Milliseconds": ["mean", "sum"],
                    "UnitPrice": "mean",
                }
            )
            .round(2)
        )

        print("Top 5 Artists by Track Count:")
        top_artists = artist_stats.sort_values(
            ("TrackId", "count"), ascending=False
        ).head()
        print(top_artists)

        # Data filtering and analysis
        print("\n🔍 Data Filtering:")
        long_tracks = tracks_with_artists[
            tracks_with_artists["Milliseconds"] > 300000
        ]  # > 5 minutes
        print(f"Tracks longer than 5 minutes: {len(long_tracks)}")

        if len(long_tracks) > 0:
            print("Longest tracks:")
            longest = long_tracks.nlargest(5, "Milliseconds")[
                ["Name_x", "Name_y", "Milliseconds"]
            ]
            longest["Minutes"] = longest["Milliseconds"] / 60000
            for _, row in longest.iterrows():
                print(
                    f"  '{row['Name_x']}' by {row['Name_y']}: {row['Minutes']:.2f} min"
                )


def data_quality_check(tables):
    """Perform data quality checks."""
    print("\n🔍 Data Quality Check:")

    for table_name, df in tables.items():
        print(f"\n--- {table_name} ---")

        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.any():
            print("Missing values:")
            for col, count in missing_values[missing_values > 0].items():
                print(f"  {col}: {count} missing")
        else:
            print("✓ No missing values")

        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            print(f"⚠️  {duplicates} duplicate rows found")
        else:
            print("✓ No duplicate rows")


def export_sample_data(tables):
    """Export sample data to CSV files for further analysis."""
    print("\n💾 Exporting Sample Data:")

    output_dir = Path("chinook_exports")
    output_dir.mkdir(exist_ok=True)

    for table_name, df in tables.items():
        # Export first 100 rows as sample
        sample_df = df.head(100)
        output_path = output_dir / f"{table_name.lower()}_sample.csv"
        sample_df.to_csv(output_path, index=False)
        print(f"✓ Exported {table_name} sample to {output_path}")


def main():
    """Main function to run the Chinook-Pandas demo."""
    print("🎵 Chinook Database - Pandas Integration Demo")
    print("=" * 50)

    try:
        # Connect to database
        conn = connect_to_chinook()

        # Get table information
        get_table_info(conn)

        # Load main tables
        tables = load_basic_tables(conn)

        # Explore data structure
        explore_data_structure(tables)

        # Basic analytics
        basic_analytics(tables)

        # Advanced analytics
        advanced_analytics(conn)

        # Pandas operations demo
        pandas_operations_demo(tables)

        # Data quality check
        data_quality_check(tables)

        # Export sample data
        export_sample_data(tables)

        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("- Explore the exported CSV files")
        print("- Modify queries for your specific analysis needs")
        print("- Use pandas visualization libraries (matplotlib, seaborn) for charts")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        if "conn" in locals():
            conn.close()
            print("🔒 Database connection closed")


if __name__ == "__main__":
    main()
