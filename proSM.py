import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import pytesseract
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class StockAnalysisApp:
    def __init__(self, master):
        self.master = master
        master.title("Stock Analysis and Trading Signal Generator")
        master.geometry("1200x800")

        # Initialize variables
        self.screenshot_path = None
        self.stock_data = None
        self.indicators = {}

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Upload Screenshot Button
        upload_button = tk.Button(self.master, text="Upload Screenshot", command=self.upload_screenshot)
        upload_button.pack(pady=10)

        # Result Display Frame
        self.result_frame = tk.Frame(self.master)
        self.result_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    def upload_screenshot(self):
        """Upload and process stock screenshot"""
        self.screenshot_path = filedialog.askopenfilename(
            title="Select Stock Screenshot",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if self.screenshot_path:
            try:
                # Use Tesseract OCR to extract text from image
                image = cv2.imread(self.screenshot_path)
                text = pytesseract.image_to_string(image)

                # Extract potential stock symbol and date
                lines = text.split('\n')
                potential_symbol = [line for line in lines if len(line) <= 5 and line.isalpha()]
                potential_date = [line for line in lines if '/' in line or '-' in line]

                if potential_symbol:
                    self.get_indicator_values(potential_symbol[0].upper(), potential_date)
                else:
                    messagebox.showerror("Error", "Could not extract stock symbol from the screenshot.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not process screenshot: {str(e)}")

    def get_indicator_values(self, symbol, date_string):
        """Fetch stock data and calculate indicator values"""
        try:
            # Convert date string to datetime object
            date = datetime.strptime(date_string[0], '%Y-%m-%d')

            # Fetch stock data
            self.stock_data = yf.download(symbol, start=date - pd.Timedelta(days=60), end=date)

            # Calculate indicator values
            self.indicators = {
                "Price": self.stock_data['Close'].iloc[-1],
                "Moving Average (20-day)": self.stock_data['Close'].rolling(window=20).mean().iloc[-1],
                "RSI": self.calculate_rsi(self.stock_data['Close'], 14).iloc[-1],
                "MACD": self.calculate_macd(self.stock_data['Close']).iloc[-1],
                "Bollinger Bands": {
                    "Middle": self.stock_data['Close'].rolling(window=20).mean().iloc[-1],
                    "Upper": self.stock_data['Close'].rolling(window=20).mean().iloc[-1] + 2 * self.stock_data['Close'].rolling(window=20).std().iloc[-1],
                    "Lower": self.stock_data['Close'].rolling(window=20).mean().iloc[-1] - 2 * self.stock_data['Close'].rolling(window=20).std().iloc[-1]
                }
            }

            self.display_results()
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch stock data: {str(e)}")

    def calculate_rsi(self, prices, periods=14):
        """Calculate Relative Strength Index (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices, fast_period=12, slow_period=26, signal_period=9):
        """Calculate Moving Average Convergence Divergence (MACD)"""
        exp1 = prices.ewm(span=fast_period, adjust=False).mean()
        exp2 = prices.ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        return macd - signal

    def display_results(self):
        """Display the calculated indicator values and trading signals"""
        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(self.stock_data.index, self.stock_data['Close'])
        ax.plot(self.stock_data.index, self.indicators['Moving Average (20-day)'], label='20-day MA')
        ax.set_title("Stock Price and Moving Average")
        ax.legend()

        # Embed matplotlib figure in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()

        # Display indicator values
        indicator_text = tk.Text(self.result_frame, height=10, width=50)
        indicator_text.pack(pady=10)
        indicator_text.insert(tk.END, "Indicator Values:\n")
        for indicator, value in self.indicators.items():
            if isinstance(value, dict):
                for sub_indicator, sub_value in value.items():
                    indicator_text.insert(tk.END, f"{indicator} - {sub_indicator}: {sub_value:.2f}\n")
            else:
                indicator_text.insert(tk.END, f"{indicator}: {value:.2f}\n")

        # Generate and display trading signals
        trading_signals = self.generate_trading_signals()
        signal_text = tk.Text(self.result_frame, height=5, width=50)
        signal_text.pack(pady=10)
        signal_text.insert(tk.END, "Trading Signals:\n")
        for signal, value in trading_signals.items():
            signal_text.insert(tk.END, f"{signal}: {value}\n")

    def generate_trading_signals(self):
        """Generate trading signals based on the calculated indicator values"""
        signals = {}

        # Moving Average Signal
        if self.indicators['Price'] > self.indicators['Moving Average (20-day)']:
            signals['Moving Average'] = 'Bullish (Buy Signal)'
        else:
            signals['Moving Average'] = 'Bearish (Sell Signal)'

        # RSI Signal
        rsi = self.indicators['RSI']
        if rsi > 70:
            signals['RSI'] = 'Overbought (Potential Sell)'
        elif rsi < 30:
            signals['RSI'] = 'Oversold (Potential Buy)'
        else:
            signals['RSI'] = 'Neutral'

        # MACD Signal
        macd = self.indicators['MACD']
        if macd > 0:
            signals['MACD'] = 'Bullish (Buy Signal)'
        else:
            signals['MACD'] = 'Bearish (Sell Signal)'

        # Bollinger Bands Signal
        price = self.indicators['Price']
        bb_middle = self.indicators['Bollinger Bands']['Middle']
        bb_upper = self.indicators['Bollinger Bands']['Upper']
        bb_lower = self.indicators['Bollinger Bands']['Lower']
        if price > bb_upper:
            signals['Bollinger Bands'] = 'Overbought (Potential Sell)'
        elif price < bb_lower:
            signals['Bollinger Bands'] = 'Oversold (Potential Buy)'
        else:
            signals['Bollinger Bands'] = 'Neutral'

        return signals

def main():
    root = tk.Tk()
    app = StockAnalysisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 