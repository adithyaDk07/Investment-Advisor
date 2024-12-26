import cv2
import numpy as np

def analyze_candlestick_chart(image_path):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Unable to load image.")
        return
    
    # Convert to grayscale for processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect edges using Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours (candlestick bodies and wicks)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    bullish_count = 0
    bearish_count = 0
    candle_bodies = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h > 10 and w > 5:  # Filter out small/noisy contours
            roi = img[y:y+h, x:x+w]  # Region of interest
            avg_color = np.mean(roi, axis=(0, 1))  # Average color (BGR)

            if avg_color[1] > avg_color[2]:  # Green (bullish)
                bullish_count += 1
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                candle_bodies.append((x, y, h, "bullish"))
            else:  # Red (bearish)
                bearish_count += 1
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
                candle_bodies.append((x, y, h, "bearish"))

    # Find support and resistance zones
    y_levels = [y for _, y, _, _ in candle_bodies]
    support_level = min(y_levels) if y_levels else None
    resistance_level = max(y_levels) if y_levels else None

    # Identify trend
    trend = "Unknown"
    if bullish_count > bearish_count:
        trend = "Uptrend (Bullish)"
    elif bearish_count > bullish_count:
        trend = "Downtrend (Bearish)"

    # Set entry and exit points
    if trend == "Uptrend (Bullish)":
        entry_point = resistance_level - 10
        target_point = resistance_level - 50
        stop_loss = resistance_level + 20
    elif trend == "Downtrend (Bearish)":
        entry_point = support_level + 10
        target_point = support_level + 50
        stop_loss = support_level - 20
    else:
        entry_point = target_point = stop_loss = "No clear trend"

    # Print results
    print(f"Trend: {trend}")
    print(f"Support Level: {support_level}")
    print(f"Resistance Level: {resistance_level}")
    print(f"Entry Point: {entry_point}")
    print(f"Target Point: {target_point}")
    print(f"Stop Loss: {stop_loss}")

    # Display results on the image
    if support_level:
        cv2.line(img, (0, support_level), (img.shape[1], support_level), (255, 0, 0), 2)
    if resistance_level:
        cv2.line(img, (0, resistance_level), (img.shape[1], resistance_level), (255, 0, 0), 2)
    cv2.imshow("Candlestick Analysis", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    image_path = r"/home/adithyadk/Desktop/new-projSM/Screenshot from 2024-12-14 23-25-47.png"  # Replace with your image path
    analyze_candlestick_chart(image_path)


#instead of converting the chart into grey instead try to find the green and red color shapes and fonts use fill function to filter the red and green candles 