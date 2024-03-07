from flask import Flask, render_template, request
import yfinance as yf
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

app = Flask(__name__)

class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = pd.DataFrame()
    def fetch_data(self):
        ticker = yf.Ticker(self.symbol)
        self.price = ticker.info['currentPrice']
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        self.data = yf.download(self.symbol, start=start_date, end=end_date)
        self.data.reset_index(inplace=True)
        conexion = sqlite3.connect('stocks.db')
        cursor = conexion.cursor()
        cursor.execute('INSERT INTO search_history (symbol, current_price) VALUES (?, ?)', (self.symbol, self.price))
        conexion.commit()
        conexion.close()
    def plot_data(self):
        fig = px.line(self.data, x='Date', y='Close', title=f'{self.symbol} Stock Price')
        return fig

@app.route('/')
def index():
    conexion = sqlite3.connect('stocks.db')
    cursor = conexion.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS search_history (id INTEGER PRIMARY KEY AUTOINCREMENT, search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, symbol TEXT, current_price INTEGER)''')
    conexion.commit()
    cursor.execute('SELECT * FROM search_history ORDER BY search_time DESC')
    search_history = cursor.fetchall()
    conexion.close()
    return render_template('index.html', search_history=search_history)

@app.route('/stock', methods=['POST'])
def stock():
    symbol = request.form['symbol']
    stock = Stock(symbol)
    stock.fetch_data()
    plot = stock.plot_data()
    plot_html = plot.to_html(full_html=False)
    return render_template('stock.html', current_price=stock.price, plot_html=plot_html, symbol=symbol)

if __name__ == '__main__':
    app.run(debug=True)