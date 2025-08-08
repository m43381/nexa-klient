import asyncio
import websockets
import sys
from datetime import datetime

# Опционально: установи через `pip install colorama`, если хочешь цвета
try:
    from colorama import Fore, Style, init
    init()  # инициализация colorama (нужно для Windows)
    COLORS = True
except ImportError:
    COLORS = False


def get_time():
    """Возвращает текущее время в формате ЧЧ:ММ:СС"""
    return datetime.now().strftime("%H:%M:%S")


async def chat_client():
    uri = "ws://192.168.1.123:8080/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{get_time()}] ✅ Подключено к серверу WebSocket")

            async def send_messages():
                while True:
                    try:
                        prompt = f"[{get_time()}] ➤ Отправить: "
                        if COLORS:
                            prompt = Fore.BLUE + prompt + Style.RESET_ALL
                        message = await asyncio.get_event_loop().run_in_executor(None, input, prompt)
                        timestamp = get_time()
                        # Добавляем время к сообщению при отправке
                        await websocket.send(f"[{timestamp}] {message}")
                    except EOFError:
                        break
                    except Exception as e:
                        print(f"[{get_time()}] ❌ Ошибка отправки: {e}")
                        break

            async def receive_messages():
                while True:
                    try:
                        response = await websocket.recv()
                        timestamp = get_time()
                        msg = f"[{timestamp}] ← Получено: {response}"
                        if COLORS:
                            print(Fore.GREEN + msg + Style.RESET_ALL)
                        else:
                            print(msg)
                    except websockets.ConnectionClosed:
                        print(f"[{get_time()}] ⚠️ Соединение закрыто сервером")
                        break
                    except Exception as e:
                        print(f"[{get_time()}] ❌ Ошибка приёма: {e}")
                        break

            # Параллельно слушаем ввод и получаем сообщения
            await asyncio.gather(send_messages(), receive_messages())

    except ConnectionRefusedError:
        print(f"[{get_time()}] ❌ Не удалось подключиться к серверу. Убедись, что сервер запущен.")
    except Exception as e:
        print(f"[{get_time()}] ❌ Ошибка подключения: {e}")


# Запуск
if __name__ == "__main__":
    try:
        asyncio.run(chat_client())
    except KeyboardInterrupt:
        print(f"\n[{get_time()}] 👋 Соединение закрыто пользователем.")
        sys.exit(0)