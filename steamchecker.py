import requests
import time

WEBHOOK_URL = 'https://discord.com/api/webhooks/1301846714063519804/9xwDhWC_czb-yLZWXlW21wSUzxXYOxHO2cz_5djcFjgSwSwxi_qXbFyFw5rrEIH4bfql'  # Coloque aqui sua URL do webhook do Discord
STEAM_API_KEY = 'BBB8C5C8765A5C1D6965257EDEB86696'   # Coloque aqui sua chave de API do Steam
STEAM_ID = 'https://steamcommunity.com/profiles/76561199153599439/'      # Coloque aqui o ID do usuário Steam que você deseja monitorar

def obter_status_steam():
    """Obtém o status e o jogo do usuário no Steam."""
    response = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={STEAM_ID}')
    data = response.json()
    
    if data['response']['players']:
        player_data = data['response']['players'][0]
        status = player_data['personastate']
        game_info = player_data.get('gameid', None)  # ID do jogo, se houver
        game_name = player_data.get('gameextrainfo', 'Não está jogando nada')  # Nome do jogo jogado, se houver
        profile_picture = player_data.get('avatar', None)  # URL da imagem do perfil
        return status, game_name, game_info, profile_picture
    else:
        return None, None, None, None  # Retorna None se o jogador não for encontrado

def obter_imagem_jogo(app_id):
    """Obtém a imagem do jogo com base no ID do aplicativo."""
    if app_id is not None:
        response = requests.get(f'http://store.steampowered.com/api/appdetails?appids={app_id}')
        data = response.json()
        
        if str(app_id) in data and data[str(app_id)]['success']:
            return data[str(app_id)]['data'].get('header_image', None)  # URL da imagem do jogo
    return None  # Retorna None se não encontrar a imagem

def enviar_mensagem_discord(status, game_name, image_url, profile_picture):
    """Envia uma mensagem embed ao Discord com o status, o jogo do usuário e a foto do perfil."""
    mensagens_status = {
        0: "Offline",
        1: "Online",
        2: "Ocupado",
        3: "Ausente",
        4: "Soneca",
        5: "Procurando negociar",
        6: "Procurando jogar",
    }
    
    mensagem = mensagens_status.get(status, "Status desconhecido")
    jogo_mensagem = game_name if game_name else "Nenhum jogo em andamento."

    embed = {
        "embeds": [
            {
                "title": "Status do Usuário Steam",
                "description": f"O usuário está agora: **{mensagem}**\n**Jogando:** {jogo_mensagem}",
                "color": 5814783,  # Cor do embed
                "footer": {
                    "text": "Atualização de Status",
                },
                "image": {
                    "url": image_url  # URL da imagem do jogo
                },
                "thumbnail": {
                    "url": profile_picture  # URL da imagem do perfil
                }
            }
        ]
    }
    
    requests.post(WEBHOOK_URL, json=embed)

def main():
    status_anterior = None  # Armazena o status anterior do usuário
    jogo_anterior = None    # Armazena o jogo anterior do usuário

    while True:
        status_atual, jogo_atual, app_id, profile_picture = obter_status_steam()  # Obtém o status e o jogo atual
        imagem_jogo = obter_imagem_jogo(app_id)  # Obtém a imagem do jogo

        # Verifica se o status ou o jogo atual é diferente do anterior
        if status_atual is not None and (status_atual != status_anterior or jogo_atual != jogo_anterior):
            enviar_mensagem_discord(status_atual, jogo_atual, imagem_jogo, profile_picture)  # Envia a mensagem ao Discord
            status_anterior = status_atual  # Atualiza o status anterior
            jogo_anterior = jogo_atual        # Atualiza o jogo anterior

        time.sleep(30)  # Espera 60 segundos antes da próxima verificação

if __name__ == "__main__":
    main()  # Executa a função principal
