import websocket
import json
import threading
import time


class BinanceWebSocketClient:
    def __init__(self):
        self.base_url = "wss://testnet.binance.vision/ws"
        self.ws = None
        self.ping_interval = 30  # seconds
        self.subscribed_streams = []
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def on_message(self, ws, message):
        """Handle incoming messages."""
        data = json.loads(message)
        if "stream" in data:
            print(f"Stream: {data['stream']}, Data: {data['data']}")
        elif "error" in data:
            print(f"Error received: {data['error']}")
        else:
            print("Message:", data)

    def on_error(self, ws, error):
        """Handle errors."""
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket closure."""
        print(f"WebSocket closed. Code: {close_status_code}, Message: {close_msg}")
        if self.reconnect_attempts < self.max_reconnect_attempts:
            print("Attempting to reconnect...")
            self.reconnect_attempts += 1
            time.sleep(2 ** self.reconnect_attempts)  # Exponential backoff
            self.connect()

    def on_open(self, ws):
        """Handle WebSocket connection opening."""
        print("WebSocket connection opened.")
        self.reconnect_attempts = 0
        self.resubscribe_to_streams()

    def resubscribe_to_streams(self):
        """Re-subscribe to all streams on reconnection."""
        for stream in self.subscribed_streams:
            self.subscribe_to_stream(stream)

    def connect(self):
        """Connect to the WebSocket server."""
        print("Connecting to Binance Testnet WebSocket...")
        self.ws = websocket.WebSocketApp(
            self.base_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def subscribe_to_stream(self, stream):
        """Subscribe to a specific stream."""
        if stream in self.subscribed_streams:
            print(f"Already subscribed to stream: {stream}")
            return

        self.subscribed_streams.append(stream)
        if self.ws:
            subscription_message = {"method": "SUBSCRIBE", "params": [stream], "id": 1}
            self.ws.send(json.dumps(subscription_message))
            print(f"Subscribed to stream: {stream}")

    def unsubscribe_from_stream(self, stream):
        """Unsubscribe from a specific stream."""
        if stream not in self.subscribed_streams:
            print(f"Stream not subscribed: {stream}")
            return

        self.subscribed_streams.remove(stream)
        if self.ws:
            unsubscription_message = {"method": "UNSUBSCRIBE", "params": [stream], "id": 1}
            self.ws.send(json.dumps(unsubscription_message))
            print(f"Unsubscribed from stream: {stream}")

    def start(self):
        """Start the WebSocket client."""
        try:
            self.connect()
        except KeyboardInterrupt:
            print("Exiting...")
            if self.ws:
                self.ws.close()


if __name__ == "__main__":
    client = BinanceWebSocketClient()
    client.start()

    # Example subscription to a trade stream for TRXUSDT
    time.sleep(1)  # Ensure WebSocket is connected
    client.subscribe_to_stream("trxusdt@ticker")

    # Keep the script running
    while True:
        time.sleep(1)
