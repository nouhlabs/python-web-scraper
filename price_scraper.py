"""
Professional Web Scraper with Data Visualization
Author: Nouh Mannsfeld - nouhlabs.github.io
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

class PriceScraper:
    """Web scraping tool that collects product data and generates reports"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.products = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        
    def scrape_products(self, max_pages=3):
        """Scrape product data from multiple pages"""
        print(f"\n{'='*60}")
        print(f"🚀 STARTING WEB SCRAPER")
        print(f"{'='*60}\n")
        print(f"Target: {self.base_url}")
        print(f"Pages to scrape: {max_pages}\n")
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/catalogue/page-{page}.html"
            print(f"Scraping page {page}...", end=" ")
            
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                products = soup.find_all('article', class_='product_pod')
                
                for product in products:
                    title = product.h3.a['title']
                    price_text = product.find('p', class_='price_color').text
                    price = float(price_text.replace('£', '').replace('€', '').replace('$', ''))
                    
                    rating_class = product.find('p', class_='star-rating')['class'][1]
                    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
                    rating = rating_map.get(rating_class, 0)
                    
                    availability = product.find('p', class_='instock availability').text.strip()
                    
                    self.products.append({
                        'title': title,
                        'price': price,
                        'rating': rating,
                        'availability': availability,
                        'page': page,
                        'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                print(f"✓ Found {len(products)} products")
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                continue
        
        print(f"\n✓ Total products scraped: {len(self.products)}")
        return self.products
    
    def analyze_data(self):
        """Perform statistical analysis"""
        if not self.products:
            print("No data to analyze!")
            return None
        
        df = pd.DataFrame(self.products)
        
        print(f"\n{'='*60}")
        print(f"📊 DATA ANALYSIS RESULTS")
        print(f"{'='*60}\n")
        
        print("💰 Price Statistics:")
        print(f"  • Average Price: ${df['price'].mean():.2f}")
        print(f"  • Median Price: ${df['price'].median():.2f}")
        print(f"  • Lowest Price: ${df['price'].min():.2f}")
        print(f"  • Highest Price: ${df['price'].max():.2f}")
        print(f"  • Price Range: ${df['price'].max() - df['price'].min():.2f}")
        
        print(f"\n⭐ Rating Statistics:")
        print(f"  • Average Rating: {df['rating'].mean():.2f} stars")
        
        print(f"\n📈 Average Price by Rating:")
        price_by_rating = df.groupby('rating')['price'].mean().sort_index()
        for rating, price in price_by_rating.items():
            print(f"  • {rating} stars: ${price:.2f}")
        
        return df
    
    def save_to_csv(self, filename=None):
        """Save data to CSV file"""
        if not self.products:
            print("No data to save!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_products_{timestamp}.csv"
        
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False)
        print(f"\n✓ Data saved to: {filename}")
        return filename
    
    def create_visualizations(self, output_dir="charts"):
        """Generate visualization charts"""
        if not self.products:
            print("No data to visualize!")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        df = pd.DataFrame(self.products)
        
        print(f"\n{'='*60}")
        print(f"📊 GENERATING VISUALIZATIONS")
        print(f"{'='*60}\n")
        
        # Price Distribution
        plt.figure(figsize=(10, 6))
        plt.hist(df['price'], bins=20, color='#6366f1', alpha=0.7, edgecolor='black')
        plt.title('Price Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Price ($)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        chart1 = f"{output_dir}/price_distribution.png"
        plt.savefig(chart1, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {chart1}")
        
        # Average Price by Rating
        plt.figure(figsize=(10, 6))
        price_by_rating = df.groupby('rating')['price'].mean()
        bars = plt.bar(price_by_rating.index, price_by_rating.values, 
                       color='#8b5cf6', alpha=0.7, edgecolor='black')
        plt.title('Average Price by Rating', fontsize=16, fontweight='bold')
        plt.xlabel('Rating (Stars)', fontsize=12)
        plt.ylabel('Average Price ($)', fontsize=12)
        plt.xticks(range(1, 6))
        plt.grid(axis='y', alpha=0.3)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.2f}', ha='center', va='bottom')
        
        chart2 = f"{output_dir}/price_by_rating.png"
        plt.savefig(chart2, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {chart2}")
        
        # Top 10 Expensive Products
        plt.figure(figsize=(12, 6))
        top_products = df.nlargest(10, 'price')
        plt.barh(range(len(top_products)), top_products['price'].values, color='#f59e0b', alpha=0.7)
        plt.yticks(range(len(top_products)), 
                   [title[:40] + '...' if len(title) > 40 else title 
                    for title in top_products['title'].values])
        plt.xlabel('Price ($)', fontsize=12)
        plt.title('Top 10 Most Expensive Products', fontsize=16, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        chart3 = f"{output_dir}/top_expensive.png"
        plt.savefig(chart3, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {chart3}")
        
        print(f"\n✓ All charts saved to '{output_dir}/' directory")
        return [chart1, chart2, chart3]
    
    def generate_html_report(self, csv_file, charts, output_file="report.html"):
        """Generate HTML report"""
        df = pd.DataFrame(self.products)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Web Scraping Report - nouhlabs</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        h1 {{ margin: 0; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .chart {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart img {{
            width: 100%;
            height: auto;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128202; Web Scraping Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        <p>Total Products Analyzed: {len(self.products)}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div>Average Price</div>
            <div class="stat-value">${df['price'].mean():.2f}</div>
        </div>
        <div class="stat-card">
            <div>Lowest Price</div>
            <div class="stat-value">${df['price'].min():.2f}</div>
        </div>
        <div class="stat-card">
            <div>Highest Price</div>
            <div class="stat-value">${df['price'].max():.2f}</div>
        </div>
        <div class="stat-card">
            <div>Average Rating</div>
            <div class="stat-value">{df['rating'].mean():.1f} &#9733;</div>
        </div>
    </div>
    
    <div class="chart">
        <h2>Price Distribution</h2>
        <img src="{charts[0]}" alt="Price Distribution">
    </div>
    
    <div class="chart">
        <h2>Average Price by Rating</h2>
        <img src="{charts[1]}" alt="Price by Rating">
    </div>
    
    <div class="chart">
        <h2>Top 10 Most Expensive Products</h2>
        <img src="{charts[2]}" alt="Top Expensive">
    </div>
    
    <div class="footer">
        <p>Report generated by nouhlabs Web Scraper</p>
        <p>Created by Nouh Mannsfeld | <a href="https://nouhlabs.github.io">nouhlabs.github.io</a></p>
    </div>
</body>
</html>"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"\n✓ HTML report saved: {output_file}")
        return output_file


def main():
    """Main execution"""
    print("\n🚀 Professional Web Scraper by nouhlabs")
    print("=" * 60)
    
    scraper = PriceScraper("https://books.toscrape.com")
    products = scraper.scrape_products(max_pages=3)
    
    if products:
        df = scraper.analyze_data()
        csv_file = scraper.save_to_csv()
        charts = scraper.create_visualizations()
        report = scraper.generate_html_report(csv_file, charts)
        
        print(f"\n{'='*60}")
        print(f"✅ SCRAPING COMPLETED!")
        print(f"{'='*60}")
        print(f"\n📁 Files created:")
        print(f"  • CSV: {csv_file}")
        print(f"  • Charts: charts/ directory")
        print(f"  • Report: {report}")
        print(f"\n💡 Open '{report}' in your browser to view results!")
    else:
        print("\n❌ No data scraped.")


if __name__ == "__main__":
    main()
