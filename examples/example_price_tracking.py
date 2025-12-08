"""
Example: Price Tracking Tool Usage
Demonstrates price collection and historical tracking.
"""

import sys
sys.path.append('..')

from tools.price_data_collector import PriceDataCollectorTool
import json
import time

def main():
    print("=== Price Tracking Tool Example ===\n")
    
    # Initialize the tool
    collector = PriceDataCollectorTool(db_path="./example_prices.db")
    
    # Example 1: Collect price from a mock source
    print("Example 1: Collect price data")
    print("-" * 50)
    
    # Note: This example uses auto-detection, which may not work on all sites
    # In production, you'd provide a specific CSS selector
    result = collector.collect_price(
        source="example_store",
        item_id="product-123",
        url="https://example.com/product"
        # For real usage: selector=".price-tag"
    )
    
    if result["success"]:
        print(f"✓ Price collected successfully")
        print(f"  Item: {result['item_id']}")
        print(f"  Price: ${result['price']}")
        print(f"  Currency: {result['currency']}")
    else:
        print(f"✗ Collection failed: {result['error']}")
        print("  Note: Auto-detection may fail on some sites")
    
    print("\n")
    
    # Example 2: Simulate multiple price collections
    print("Example 2: Simulating historical data")
    print("-" * 50)
    
    # Manually insert some sample data for demonstration
    import sqlite3
    from datetime import datetime, timedelta
    
    conn = sqlite3.connect("./example_prices.db")
    cursor = conn.cursor()
    
    # Insert sample historical prices
    base_price = 99.99
    for i in range(30):
        timestamp = (datetime.now() - timedelta(days=30-i)).isoformat()
        price = base_price + (i % 10 - 5) * 2  # Simulate price variation
        
        cursor.execute('''
            INSERT INTO price_data (source, item_id, item_name, price, currency, timestamp, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("example_store", "product-456", "Sample Product", price, "USD", timestamp, ""))
    
    conn.commit()
    conn.close()
    
    print("✓ Sample historical data created")
    
    print("\n")
    
    # Example 3: Get price history
    print("Example 3: Retrieve price history")
    print("-" * 50)
    
    history = collector.get_price_history("product-456", days=30)
    
    if history["success"]:
        print(f"✓ History retrieved")
        print(f"  Data points: {history['count']}")
        print(f"\n  Statistics:")
        stats = history['statistics']
        print(f"    Current: ${stats['current_price']:.2f}")
        print(f"    Average: ${stats['average_price']:.2f}")
        print(f"    Min: ${stats['min_price']:.2f}")
        print(f"    Max: ${stats['max_price']:.2f}")
        print(f"    Range: ${stats['price_range']:.2f}")
        print(f"    Volatility: {stats['volatility']:.2f}%")
    
    print("\n")
    
    # Example 4: Price alerts
    print("Example 4: Check price alerts")
    print("-" * 50)
    
    alerts = collector.get_price_alerts(
        "product-456",
        threshold_low=95.0,
        threshold_high=105.0
    )
    
    if alerts["success"]:
        print(f"✓ Alert check complete")
        print(f"  Current price: ${alerts['current_price']:.2f}")
        print(f"  Alerts triggered: {alerts['alerts_triggered']}")
        
        if alerts['alerts']:
            for alert in alerts['alerts']:
                print(f"    {alert['type'].upper()}: {alert['message']}")
    
    print("\n")
    
    # Example 5: Batch collection
    print("Example 5: Batch price collection")
    print("-" * 50)
    
    items = [
        {
            "source": "store_a",
            "item_id": "item-001",
            "url": "https://example.com/item1"
        },
        {
            "source": "store_b",
            "item_id": "item-002",
            "url": "https://example.com/item2"
        }
    ]
    
    batch_result = collector.collect_multiple(items)
    print(f"✓ Batch collection attempted")
    print(f"  Total items: {batch_result['total_items']}")
    print(f"  Successful: {batch_result['successful']}")
    print(f"  Failed: {batch_result['failed']}")
    
    print("\n")
    print("=== Example Complete ===")
    print("\nNote: Database file created at ./example_prices.db")

if __name__ == "__main__":
    main()
