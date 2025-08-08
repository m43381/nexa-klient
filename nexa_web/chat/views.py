from django.shortcuts import render

# ⚙️ Укажи IP Go-сервера вручную
GO_SERVER_IP = "192.168.1.123"
GO_SERVER_PORT = "8080"


def chat_view(request):
    client_id = request.GET.get("id", "sss")
    go_ws_url = f"ws://{GO_SERVER_IP}:{GO_SERVER_PORT}/ws"
    return render(request, 'chat.html', {
        'client_id': client_id,
        'go_ws_url': go_ws_url,
    })