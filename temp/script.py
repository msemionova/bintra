import time
from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np
import websocket
import json
from datetime import datetime, timedelta
import asyncio
import websockets
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('TESTNET_API_KEY')
API_SECRET = os.getenv('TESTNET_API_SECRET')

# Подключение к клиенту Binance
client = Client(API_KEY, API_SECRET, testnet=True)

# Константы
SYMBOL = 'TRXUSDT'  # Торгуем TRX против USDT
ORDER_SIZE = 20  # Покупаем/продаем TRX на 20 штук (можно изменить)
TIMEFRAME = '1m'  # Свечи по 1 минуте

# Константы для ордеров
SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'
ORDER_TYPE_MARKET = 'MARKET'
ORDER_TYPE_LIMIT = 'LIMIT'
ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'

# Функция для получения данных свечей
def fetch_price_data(symbol, interval, limit=10):
    """Получает данные свечей для пары"""
    candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    prices = [float(candle[4]) for candle in candles]  # Цена закрытия
    return prices

# Определение тренда
def detect_trend(prices, threshold=0.001):
    """Определяет тренд на основе порога изменений"""
    changes = np.diff(prices) / prices[:-1]  # Относительное изменение
    avg_change = np.mean(changes)  # Среднее изменение

    if avg_change > threshold:
        return 'UP'
    elif avg_change < -threshold:
        return 'DOWN'
    return 'NEUTRAL'

# Размещение рыночного ордера
def place_order(symbol, side, quantity):
    """Размещает рыночный ордер"""
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print(f"Успешно размещён {side} ордер: {order}")
        return order
    except Exception as e:
        print(f"Ошибка размещения ордера: {e}")
        return None

# Рассчёт RSI
def calculate_rsi(prices, period=14):
    """Вычисляет RSI"""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:  # Чтобы избежать деления на 0
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Проверка статуса ордера
def check_order_status(order_id):
    """Проверяет статус ордера"""
    try:
        # Получаем информацию о конкретном ордере
        order = client.get_order(symbol=SYMBOL, orderId=order_id)
        print(f"Статус ордера: {order['status']}")  # Возможные статусы: NEW, FILLED, PARTIALLY_FILLED, CANCELED
        return order['status']
    except Exception as e:
        print(f"Ошибка при проверке статуса ордера: {e}")
        return None

# Установка тейк-профита и стоп-лосса
def place_take_profit_and_stop_loss(order_side, entry_price, take_profit_percent, stop_loss_percent):
    try:
        # Рассчитываем тейк-профит и стоп-лосс
        if order_side == SIDE_BUY:
            take_profit_price = entry_price * (1 + take_profit_percent)
            stop_loss_price = entry_price * (1 - stop_loss_percent)
        else:
            take_profit_price = entry_price * (1 - take_profit_percent)
            stop_loss_price = entry_price * (1 + stop_loss_percent)

        # Шаг цены для торговой пары TRX/USDT
        tick_size = 0.00010000  # Этот шаг пришел из фильтра PRICE_FILTER

        # Округляем цены до 5 знаков после запятой и применяем шаг цены
        take_profit_price = round(take_profit_price, 5)
        stop_loss_price = round(stop_loss_price, 5)

        # Применяем шаг цены (например, 0.00010000)
        take_profit_price = (take_profit_price // tick_size) * tick_size
        stop_loss_price = (stop_loss_price // tick_size) * tick_size

        # Преобразуем в строку и удаляем лишние нули
        take_profit_price_str = f"{take_profit_price:.5f}".rstrip('0').rstrip('.')
        stop_loss_price_str = f"{stop_loss_price:.5f}".rstrip('0').rstrip('.')

        # Логируем перед отправкой
        print(f"Take Profit Price: {take_profit_price_str}")
        print(f"Stop Loss Price: {stop_loss_price_str}")

        # Размещение ордеров
        take_profit_order = client.create_order(
            symbol=SYMBOL,
            side=SIDE_SELL if order_side == SIDE_BUY else SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            price=take_profit_price_str,
            quantity=ORDER_SIZE,
            timeInForce='GTC'
        )

        stop_loss_order = client.create_order(
            symbol=SYMBOL,
            side=SIDE_SELL if order_side == SIDE_BUY else SIDE_BUY,
            type=ORDER_TYPE_STOP_LOSS_LIMIT,
            price=stop_loss_price_str,
            stopPrice=stop_loss_price_str,
            quantity=ORDER_SIZE,
            timeInForce='GTC'
        )
        print("Тейк-профит и стоп-лосс установлены!")
    except Exception as e:
        print(f"Ошибка при установке тейк-профита или стоп-лосса: {e}")

# Мониторинг позиции
def monitor_position(entry_price, side, take_profit_percent, stop_loss_percent):
    """Следит за позицией и закрывает её при достижении условий"""
    while True:
        try:
            current_price = fetch_price_data(SYMBOL, TIMEFRAME, limit=1)[-1]
            if side == SIDE_BUY:
                # Условие тейк-профита
                if current_price >= entry_price * (1 + take_profit_percent):
                    print(f"Цена достигла тейк-профита: {current_price}. Закрываем позицию.")
                    place_order(SYMBOL, SIDE_SELL, ORDER_SIZE)
                    break
                # Условие стоп-лосса
                elif current_price <= entry_price * (1 - stop_loss_percent):
                    print(f"Цена достигла стоп-лосса: {current_price}. Закрываем позицию.")
                    place_order(SYMBOL, SIDE_SELL, ORDER_SIZE)
                    break
            else:  # Если позиция SELL
                if current_price <= entry_price * (1 - take_profit_percent):
                    print(f"Цена достигла тейк-профита: {current_price}. Закрываем позицию.")
                    place_order(SYMBOL, SIDE_BUY, ORDER_SIZE)
                    break
                elif current_price >= entry_price * (1 + stop_loss_percent):
                    print(f"Цена достигла стоп-лосса: {current_price}. Закрываем позицию.")
                    place_order(SYMBOL, SIDE_BUY, ORDER_SIZE)
                    break

            time.sleep(5)  # Проверяем каждые 5 секунд
        except Exception as e:
            print(f"Ошибка при мониторинге позиции: {e}")
            break

# Логика торговли
def trade_logic():
    """Логика торговли"""
    prices = fetch_price_data(SYMBOL, TIMEFRAME, limit=5)
    trend = detect_trend(prices)
    rsi = calculate_rsi(prices)

    print(f"Текущий тренд: {trend}. Последняя цена: {prices[-1]}")
    print(f"RSI: {rsi}")

    if rsi < 30:  # Перепродан, сигнал на покупку
        print("Покупаем TRX...")
        order = place_order(SYMBOL, SIDE_BUY, ORDER_SIZE)
        if order:
            entry_price = float(order['fills'][0]['price'])
            place_take_profit_and_stop_loss(SIDE_BUY, entry_price, 0.02, 0.01)  # Тейк-профит 2%, стоп-лосс 1%
            monitor_position(entry_price, SIDE_BUY, 0.02, 0.01)
    elif rsi > 70:  # Перекуплен, сигнал на продажу
        print("Продаём TRX...")
        order = place_order(SYMBOL, SIDE_SELL, ORDER_SIZE)
        if order:
            entry_price = float(order['fills'][0]['price'])
            place_take_profit_and_stop_loss(SIDE_SELL, entry_price, 0.02, 0.01)  # Тейк-профит 2%, стоп-лосс 1%
            monitor_position(entry_price, SIDE_SELL, 0.02, 0.01)
    else:
        print("RSI в нейтральной зоне. Ждём...")

last_price = None  # Хранит предыдущую цену
TRADE_VOLUME_THRESHOLD = 1000  # Минимальный объем сделки

def on_message(ws, message):
    global last_price
    data = json.loads(message)

    if data.get("e") == "24hrTicker":
        current_price = float(data["c"])

        # Фильтрация неизменной цены
        if current_price != last_price:
            last_price = current_price
            update_price_stats(current_price)
            print(f"Symbol: {data['s']}, Current Price: {current_price}")

    elif data.get("e") == "trade":  # Если отслеживаем сделки
        trade_volume = float(data["q"])
        if trade_volume < TRADE_VOLUME_THRESHOLD:
            return

        print(f"Trade: {data['s']}, Price: {data['p']}, Volume: {trade_volume}")

def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed: {close_status_code} - {close_msg}")


def on_open(ws):
    print("WebSocket connection opened (Testnet)")

    # Подписываемся на 24hr Ticker и сделки
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [
            "trxusdt@ticker",  # Информация о 24 часах
            "trxusdt@trade"    # Информация о сделках
        ],
        "id": 1
    }
    ws.send(json.dumps(subscribe_message))

# Для хранения минимальных и максимальных цен за минуту
price_stats = {
    "min_price": float('inf'),
    "max_price": float('-inf'),
    "last_updated": datetime.now(),
}

async def process_message(message):
    global price_stats
    data = json.loads(message)

    if data.get("e") == "24hrTicker":
        current_price = float(data["c"])
        now = datetime.now()

        # Сброс статистики, если новая минута
        if now - price_stats["last_updated"] >= timedelta(minutes=1):
            print(f"Min Price Last Minute: {price_stats['min_price']}")
            print(f"Max Price Last Minute: {price_stats['max_price']}")
            price_stats["min_price"] = float('inf')
            price_stats["max_price"] = float('-inf')
            price_stats["last_updated"] = now

        # Обновление минимальной и максимальной цены
        if current_price < price_stats["min_price"]:
            price_stats["min_price"] = current_price
            print(f"New Minimum Price: {price_stats['min_price']}")

        if current_price > price_stats["max_price"]:
            price_stats["max_price"] = current_price
            print(f"New Maximum Price: {price_stats['max_price']}")

        print(f"Symbol: {data['s']}, Current Price: {current_price}")

async def websocket_listener():
    url = "wss://testnet.binance.vision/ws/trxusdt@ticker"  # Подключение к потоку сделок
    async with websockets.connect(url) as ws:
        print("WebSocket connection opened (Testnet)")
        while True:
            message = await ws.recv()
            await process_message(message)

# WebSocket URL
WEBSOCKET_URL = "wss://testnet.binance.vision/ws/trxusdt@ticker"
async def websocket_listener2():
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("WebSocket connection opened.")
        while True:
            message = await ws.recv()  # Получить сообщение
            # Если нужно парсить JSON
            data = json.loads(message)
            print(f"Parsed Data: {data}")


def update_price_stats(current_price):
    """
    Обновляет минимальную и максимальную цену в реальном времени.
    """
    global price_stats
    now = datetime.now()

    # Если текущая минута изменилась, сбросить статистику
    if now - price_stats["last_updated"] >= timedelta(minutes=1):
        print(f"Min Price Last Minute: {price_stats['min_price']}")
        print(f"Max Price Last Minute: {price_stats['max_price']}")
        # Сброс для новой минуты
        price_stats["min_price"] = float('inf')
        price_stats["max_price"] = float('-inf')
        price_stats["last_updated"] = now

    # Постоянное обновление минимальной и максимальной цены
    if current_price < price_stats["min_price"]:
        price_stats["min_price"] = current_price
        print(f"New Minimum Price: {price_stats['min_price']}")

    if current_price > price_stats["max_price"]:
        price_stats["max_price"] = current_price
        print(f"New Maximum Price: {price_stats['max_price']}")

# Запуск скрипта
if __name__ == "__main__":
    # trade_logic()

    # Получение исторических данных (OHLCV) за последний час
    klines = client.get_historical_klines(SYMBOL, Client.KLINE_INTERVAL_1MINUTE, "1 minute ago UTC")

    # Извлекаем минимальную и максимальную цену за последний час
    low_price = float(klines[0][3])  # Минимальная цена (Low)
    high_price = float(klines[0][2])  # Максимальная цена (High)

    print(f"Минимальная цена за последнюю минуту: {low_price}")
    print(f"Максимальная цена за последнюю минуту: {high_price}")

    # ################## ОРДЕРА
    ################## Получаем баланс USDT
    # usdt_balance = client.get_asset_balance(asset='USDT')
    # print(f"Баланс USDT: {usdt_balance}")

    # # ################## Получаем баланс TRX
    # trx_balance = client.get_asset_balance(asset='TRX')
    # print(f"Баланс TRX: {trx_balance}")

    # orders = client.get_all_orders(symbol="TRXUSDT")
    # # Фильтруем только открытые ордера (статус "NEW" или "PARTIALLY_FILLED")
    # open_orders = [order for order in orders if order['status'] in ['NEW', 'PARTIALLY_FILLED']]

    # # Выводим открытые ордера
    # if open_orders:
    #     print(f"Открытые ордера: {open_orders}")
    # else:
    #     print("Нет открытых ордеров.")

    # ################## Отмена ордера
    # order_id1 = 1666352  # ID ордера, который вы хотите отменить
    # order_id2 = 1666353  # ID ордера, который вы хотите отменить
    # symbol = 'TRXUSDT'  # Торговая пара

    # response1 = client.cancel_order(symbol=symbol, orderId=order_id1)
    # print(response1)

    # response2 = client.cancel_order(symbol=symbol, orderId=order_id2)
    # print(response2)

    # ################## Подробности
    # symbol_info = client.get_symbol_info('TRXUSDT')
    # filters = symbol_info['filters']
    # price_filter = next(filter for filter in filters if filter['filterType'] == 'PRICE_FILTER')
    # print(price_filter)

    # websocket.enableTrace(False)
    # socket = 'wss://testnet.binance.vision/ws'
    # ws = websocket.WebSocketApp(socket,
    #                             on_message=on_message,
    #                             on_error=on_error,
    #                             on_close=on_close,
    #                             on_open=on_open)
    # ws.run_forever()

    asyncio.run(websocket_listener2())
