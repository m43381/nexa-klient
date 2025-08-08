import asyncio
import websockets
import sys
import json
import base64
from datetime import datetime

# Опционально: цвета
try:
    from colorama import Fore, Style, init
    init()
    COLORS = True
except ImportError:
    COLORS = False


def get_time():
    return datetime.now().strftime("%H:%M:%S")


async def chat_client():
    SERVER_IP = "192.168.1.123"
    PORT = "8080"
    CLIENT_ID = input("Введите ваш ID (публичный ключ): ").strip()
    if not CLIENT_ID:
        print("❌ ID не может быть пустым.")
        return

    uri = f"ws://{SERVER_IP}:{PORT}/ws?id={CLIENT_ID}"
    print(f"[{get_time()}] 🌐 Подключаюсь к {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{get_time()}] ✅ Успешно подключён как '{CLIENT_ID}'")

            # === Отправка сообщений ===
            async def send_messages():
                while True:
                    try:
                        prompt = f"[{get_time()}] ➤ Отправить [кому:сообщение]: "
                        if COLORS:
                            prompt = Fore.BLUE + prompt + Style.RESET_ALL
                        user_input = await asyncio.get_event_loop().run_in_executor(None, input, prompt)

                        if not user_input.strip():
                            continue

                        if ':' not in user_input:
                            print(f"[{get_time()}] ❌ Формат: 'id_получателя: сообщение'")
                            continue

                        to_id, message = user_input.split(':', 1)
                        to_id = to_id.strip()
                        message = message.strip()

                        # Добавляем временную метку
                        text_with_time = f"[{get_time()}] {message}"

                        # Кодируем в байты (не в base64!)
                        data_bytes = text_with_time.encode('utf-8')  # → bytes

                        # Отправляем как JSON: {"to": "...", "from": "...", "data": [104,101,108,108,111]}
                        payload = {
                            "to": to_id,
                            "from": CLIENT_ID,
                            "data": list(data_bytes)  # ← преобразуем bytes в list[int]
                        }

                        await websocket.send(json.dumps(payload))
                        print(f"[{get_time()}] ✉️  Отправлено -> {to_id}")

                    except Exception as e:
                        print(f"[{get_time()}] ❌ Ошибка отправки: {e}")
                        break

            # === Приём сообщений ===
            async def receive_messages():
                while True:
                    try:
                        raw = await websocket.recv()

                        try:
                            msg = json.loads(raw)
                            sender = msg.get("from", "unknown")
                            data = msg.get("data", "")

                            # === Случай 1: data — массив чисел (байты) [104, 101, ...]
                            if isinstance(data, list):
                                try:
                                    text = bytes(data).decode('utf-8')
                                    output = f"[{get_time()}] 🔔 ОТ {sender}: {text}"
                                except Exception:
                                    output = f"[{get_time()}] 🔹 Получено (не UTF-8): {bytes(data)}"

                            # === Случай 2: data — строка в base64
                            elif isinstance(data, str):
                                try:
                                    text = base64.b64decode(data).decode('utf-8')
                                    output = f"[{get_time()}] 🔔 ОТ {sender}: {text}"
                                except Exception:
                                    output = f"[{get_time()}] 🔹 Получено (ошибка base64): {data}"

                            # === Случай 3: неизвестный формат
                            else:
                                output = f"[{get_time()}] 📡 Неизвестный формат данных: {data}"

                        except json.JSONDecodeError:
                            # Если не JSON — выводим как есть
                            output = f"[{get_time()}] 📡 RAW: {raw}"

                        if COLORS:
                            print(Fore.GREEN + output + Style.RESET_ALL)
                        else:
                            print(output)

                    except websockets.ConnectionClosed:
                        print(f"[{get_time()}] ⚠️ Соединение закрыто сервером")
                        break
                    except Exception as e:
                        print(f"[{get_time()}] ❌ Ошибка приёма: {e}")
                        break

            await asyncio.gather(send_messages(), receive_messages())

    except ConnectionRefusedError:
        print(f"[{get_time()}] ❌ Не удалось подключиться. Сервер не отвечает.")
    except Exception as e:
        print(f"[{get_time()}] ❌ Ошибка подключения: {e}")


# Запуск
if __name__ == "__main__":
    try:
        asyncio.run(chat_client())
    except KeyboardInterrupt:
        print(f"\n[{get_time()}] 👋 Соединение закрыто пользователем.")
        sys.exit(0)