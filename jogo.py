import pygame
import numpy as np
import matplotlib.pyplot as plt
import random
import io
import sys
import os

# Configurar o matplotlib para funcionar melhor com pygame
plt.switch_backend('Agg')

class CorridaEstatistica:
    def __init__(self):
        pygame.init()
        
        # Configurar tela
        self.largura, self.altura = 1400, 800
        self.tela = pygame.display.set_mode((self.largura, self.altura), pygame.RESIZABLE)
        pygame.display.set_caption("Corrida Estatística - Duelo de Distribuições")
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        # Cores - TODAS UNIFORMIZADAS
        self.cor_fundo = (30, 30, 60)           # Azul escuro uniforme
        self.cor_area_principal = (40, 40, 80)  # Azul médio
        self.cor_tabuleiro = (50, 50, 100)      # Azul mais claro para contraste
        self.cor_borda_tabuleiro = (80, 80, 140)
        self.cor_texto = (255, 255, 255)
        self.cor_jogador1 = (255, 100, 100)     # Vermelho
        self.cor_jogador2 = (100, 180, 255)     # Azul claro
        self.cor_meta = (255, 215, 0)           # Dourado
        self.cor_botao = (0, 180, 0)
        self.cor_botao_hover = (0, 220, 0)
        self.cor_botao_reiniciar = (180, 0, 0)      # Vermelho para reiniciar
        self.cor_botao_reiniciar_hover = (220, 0, 0) # Vermelho mais claro
        self.cor_casa_sorte = (100, 255, 100)       # Verde para casas de sorte
        self.cor_casa_azar = (255, 100, 100)        # Vermelho para casas de azar
        
        # Fontes
        self.fonte = pygame.font.SysFont('Arial', 20)
        self.fonte_pequena = pygame.font.SysFont('Arial', 16)
        self.fonte_titulo = pygame.font.SysFont('Arial', 28, bold=True)
        self.fonte_vencedor = pygame.font.SysFont('Arial', 32, bold=True)
        self.fonte_evento = pygame.font.SysFont('Arial', 18, bold=True)
        
        # Dados dos jogadores
        self.jogadores = {
            1: {'posicao': 0, 'dados': [], 'cor': self.cor_jogador1, 'nome': 'Jogador 1'},
            2: {'posicao': 0, 'dados': [], 'cor': self.cor_jogador2, 'nome': 'Jogador 2'}
        }
        
        self.jogador_atual = 1
        self.vencedor = None
        self.meta = 30
        
        # Histórico para gráficos
        self.historico_medias = {1: [], 2: []}
        
        # Estado dos botões
        self.botao_jogar_hover = False
        self.botao_reiniciar_hover = False
        
        # Casas com consequências (avançar/voltar)
        self.casas_consequencia = {
            # Casas de SORTE (avançar)
            3: {"tipo": "SORTE", "valor": 2, "mensagem": "Atalho encontrado! Avance 2 casas!"},
            8: {"tipo": "SORTE", "valor": 3, "mensagem": "Vento a favor! Avance 3 casas!"},
            12: {"tipo": "SORTE", "valor": 1, "mensagem": "Passo rápido! Avance 1 casa!"},
            18: {"tipo": "SORTE", "valor": 2, "mensagem": "Escada mágica! Avance 2 casas!"},
            22: {"tipo": "SORTE", "valor": 4, "mensagem": "Super impulso! Avance 4 casas!"},
            28: {"tipo": "SORTE", "valor": 2, "mensagem": "Quase lá! Avance 2 casas!"},
            
            # Casas de AZAR (voltar)
            4: {"tipo": "AZAR", "valor": 2, "mensagem": "Queda! Volte 2 casas!"},
            7: {"tipo": "AZAR", "valor": 3, "mensagem": "Armadilha! Volte 3 casas!"},
            11: {"tipo": "AZAR", "valor": 1, "mensagem": "Escorregão! Volte 1 casa!"},
            14: {"tipo": "AZAR", "valor": 2, "mensagem": "Teletransporte reverso! Volte 2 casas!"},
            17: {"tipo": "AZAR", "valor": 4, "mensagem": "Buracão! Volte 4 casas!"},
            21: {"tipo": "AZAR", "valor": 2, "mensagem": "Falso avanço! Volte 2 casas!"},
            26: {"tipo": "AZAR", "valor": 3, "mensagem": "Ultimo obstáculo! Volte 3 casas!"}
        }
        
        self.evento_ativado = None
        self.mensagem_evento = ""
        self.tempo_evento = 0

    def reiniciar_jogo(self):
        """Reinicia todo o jogo para o estado inicial"""
        self.jogadores = {
            1: {'posicao': 0, 'dados': [], 'cor': self.cor_jogador1, 'nome': 'Jogador 1'},
            2: {'posicao': 0, 'dados': [], 'cor': self.cor_jogador2, 'nome': 'Jogador 2'}
        }
        self.jogador_atual = 1
        self.vencedor = None
        self.historico_medias = {1: [], 2: []}
        self.evento_ativado = None
        self.mensagem_evento = ""
        print("Jogo reiniciado!")

    def ativar_consequencia(self, casa, jogador_id):
        """Ativa consequência de sorte ou azar baseada na casa"""
        if casa in self.casas_consequencia:
            consequencia = self.casas_consequencia[casa]
            jogador = self.jogadores[jogador_id]
            
            if consequencia["tipo"] == "SORTE":
                # Avançar casas
                movimento_extra = consequencia["valor"]
                jogador['posicao'] += movimento_extra
                self.mensagem_evento = f"SORTE! {consequencia['mensagem']}"
                
            elif consequencia["tipo"] == "AZAR":
                # Voltar casas
                movimento_negativo = consequencia["valor"]
                jogador['posicao'] = max(0, jogador['posicao'] - movimento_negativo)
                self.mensagem_evento = f"AZAR! {consequencia['mensagem']}"
            
            self.evento_ativado = f"CONSEQUENCIA_{consequencia['tipo']}"
            self.tempo_evento = 180  # 3 segundos

    def lancar_dados_jogador(self, jogador_id):
        """Lança dados para um jogador e move o peão"""
        if self.vencedor:
            return None
            
        jogador = self.jogadores[jogador_id]
        
        # Lançamento normal de 2 dados
        resultado = sum(random.randint(1, 6) for _ in range(2))
        self.jogadores[jogador_id]['dados'].append(resultado)
        
        # Movimento base (máximo 5 casas por turno para balancear)
        movimento_base = min(resultado, 5)
        
        posicao_anterior = jogador['posicao']
        self.jogadores[jogador_id]['posicao'] += movimento_base
        
        # Atualizar histórico de médias
        dados_jogador = self.jogadores[jogador_id]['dados']
        if dados_jogador:
            media_atual = np.mean(dados_jogador)
            self.historico_medias[jogador_id].append(media_atual)
        
        # Verificar casas com consequências
        posicao_atual = jogador['posicao']
        
        # Verificar se passou por alguma casa de consequência
        for casa in range(posicao_anterior + 1, posicao_atual + 1):
            if casa in self.casas_consequencia:
                self.ativar_consequencia(casa, jogador_id)
        
        # Verificar se ganhou
        if self.jogadores[jogador_id]['posicao'] >= self.meta:
            self.jogadores[jogador_id]['posicao'] = self.meta
            self.vencedor = jogador_id
        
        return resultado

    def alternar_jogador(self):
        """Alterna para o próximo jogador"""
        self.jogador_atual = 3 - self.jogador_atual  # Alterna entre 1 e 2

    def calcular_estatisticas_jogador(self, jogador_id):
        """Calcula estatísticas para um jogador"""
        dados = self.jogadores[jogador_id]['dados']
        if not dados:
            return None
            
        return {
            'total_lancamentos': len(dados),
            'media': np.mean(dados),
            'mediana': np.median(dados),
            'moda': max(set(dados), key=dados.count) if dados else 0,
            'desvio_padrao': np.std(dados),
            'variancia': np.var(dados),
            'minimo': min(dados),
            'maximo': max(dados),
            'soma_total': sum(dados)
        }

    def calcular_distribuicao_teorica(self):
        """Calcula distribuição teórica para soma de 2 dados"""
        teorica = {}
        for i in range(1, 7):
            for j in range(1, 7):
                soma = i + j
                teorica[soma] = teorica.get(soma, 0) + 1/36
        return teorica

    def desenhar_tabuleiro_corrida(self):
        """Desenha o mini-tabuleiro de corrida BONITINHO"""
        # Área do tabuleiro (canto superior direito)
        tab_x = self.largura * 0.65
        tab_y = 50
        tab_largura = self.largura * 0.3
        tab_altura = 220
        
        # Fundo do tabuleiro com borda elegante
        pygame.draw.rect(self.tela, self.cor_tabuleiro, 
                        (tab_x, tab_y, tab_largura, tab_altura), border_radius=12)
        pygame.draw.rect(self.tela, self.cor_borda_tabuleiro, 
                        (tab_x, tab_y, tab_largura, tab_altura), 3, border_radius=12)
        
        # Título
        titulo = self.fonte_titulo.render("CORRIDA ESTATÍSTICA", True, (255, 255, 0))
        self.tela.blit(titulo, (tab_x + (tab_largura - titulo.get_width()) // 2, tab_y + 15))
        
        # Pista de corrida
        pista_y = tab_y + 60
        pista_altura = 100
        
        # Desenhar pista com linhas de marcação
        pygame.draw.rect(self.tela, (60, 60, 100), 
                        (tab_x + 40, pista_y, tab_largura - 80, pista_altura))
        
        # Linhas da pista
        for i in range(1, 3):
            pygame.draw.rect(self.tela, (100, 100, 160), 
                           (tab_x + 40, pista_y + i * pista_altura//3, 
                            tab_largura - 80, 2))
        
        # Marcar casas de sorte (verde)
        for casa in [c for c in self.casas_consequencia.keys() if self.casas_consequencia[c]["tipo"] == "SORTE"]:
            if casa <= self.meta:
                casa_x = tab_x + 50 + (tab_largura - 120) * (casa / self.meta)
                pygame.draw.circle(self.tela, self.cor_casa_sorte, (int(casa_x), pista_y - 10), 4)
        
        # Marcar casas de azar (vermelho)
        for casa in [c for c in self.casas_consequencia.keys() if self.casas_consequencia[c]["tipo"] == "AZAR"]:
            if casa <= self.meta:
                casa_x = tab_x + 50 + (tab_largura - 120) * (casa / self.meta)
                pygame.draw.circle(self.tela, self.cor_casa_azar, (int(casa_x), pista_y + pista_altura + 10), 4)
        
        # Linha de meta
        meta_x = tab_x + tab_largura - 70
        pygame.draw.line(self.tela, self.cor_meta, 
                        (meta_x, pista_y), (meta_x, pista_y + pista_altura), 4)
        
        # Texto da meta
        texto_meta = self.fonte_pequena.render("META", True, self.cor_meta)
        self.tela.blit(texto_meta, (meta_x - 20, pista_y - 25))
        
        # Legenda das casas especiais
        legenda_y = pista_y + pista_altura + 30
        pygame.draw.circle(self.tela, self.cor_casa_sorte, (tab_x + 40, legenda_y), 4)
        texto_sorte = self.fonte_pequena.render("= Sorte (Avançar)", True, self.cor_texto)
        self.tela.blit(texto_sorte, (tab_x + 50, legenda_y - 8))
        
        pygame.draw.circle(self.tela, self.cor_casa_azar, (tab_x + 200, legenda_y), 4)
        texto_azar = self.fonte_pequena.render("= Azar (Voltar)", True, self.cor_texto)
        self.tela.blit(texto_azar, (tab_x + 210, legenda_y - 8))
        
        # Desenhar peões dos jogadores
        for jogador_id in [1, 2]:
            jogador = self.jogadores[jogador_id]
            progresso = min(jogador['posicao'] / self.meta, 1.0)
            peao_x = tab_x + 50 + (tab_largura - 120) * progresso
            peao_y = pista_y + 25 + (jogador_id - 1) * 35
            
            # Desenhar peão (agora mais bonito)
            pygame.draw.circle(self.tela, jogador['cor'], (int(peao_x), peao_y), 10)
            pygame.draw.circle(self.tela, (255, 255, 255), (int(peao_x), peao_y), 10, 2)
            
            # Sombra do peão
            pygame.draw.circle(self.tela, (0, 0, 0, 100), (int(peao_x) + 2, peao_y + 2), 10)
            
            # Nome e posição
            texto_pos = self.fonte_pequena.render(
                f"{jogador['nome']}: {jogador['posicao']}/{self.meta}", True, jogador['cor']
            )
            self.tela.blit(texto_pos, (tab_x + 20, peao_y - 25))
            
            # Destacar jogador atual
            if jogador_id == self.jogador_atual and not self.vencedor:
                pygame.draw.circle(self.tela, (255, 255, 0), (int(peao_x), peao_y), 14, 2)

    def desenhar_mensagem_evento(self):
        """Desenha mensagem de evento especial"""
        if self.tempo_evento > 0 and self.mensagem_evento:
            # Fundo da mensagem de evento
            msg_x = self.largura * 0.65
            msg_y = 280
            msg_largura = self.largura * 0.3
            msg_altura = 60
            
            # Cor do fundo baseada no tipo de evento
            if "SORTE" in self.mensagem_evento:
                cor_fundo = (40, 100, 40)  # Verde escuro para sorte
                cor_borda = self.cor_casa_sorte
            elif "AZAR" in self.mensagem_evento:
                cor_fundo = (100, 40, 40)  # Vermelho escuro para azar
                cor_borda = self.cor_casa_azar
            
            pygame.draw.rect(self.tela, cor_fundo, 
                            (msg_x, msg_y, msg_largura, msg_altura), border_radius=10)
            pygame.draw.rect(self.tela, cor_borda, 
                            (msg_x, msg_y, msg_largura, msg_altura), 2, border_radius=10)
            
            texto_evento = self.fonte_evento.render(self.mensagem_evento, True, (255, 255, 200))
            texto_x = msg_x + (msg_largura - texto_evento.get_width()) // 2
            texto_y = msg_y + (msg_altura - texto_evento.get_height()) // 2
            self.tela.blit(texto_evento, (texto_x, texto_y))
            
            self.tempo_evento -= 1

    def desenhar_mensagem_vencedor(self):
        """Desenha a mensagem do vencedor em local reservado"""
        if not self.vencedor:
            return
            
        # Área reservada para mensagem (abaixo do tabuleiro)
        msg_x = self.largura * 0.65
        msg_y = 350 if self.tempo_evento > 0 else 280  # Ajusta posição se houver evento
        msg_largura = self.largura * 0.3
        msg_altura = 60
        
        # Fundo da mensagem
        pygame.draw.rect(self.tela, (40, 40, 80), 
                        (msg_x, msg_y, msg_largura, msg_altura), border_radius=10)
        pygame.draw.rect(self.tela, (255, 215, 0), 
                        (msg_x, msg_y, msg_largura, msg_altura), 2, border_radius=10)
        
        vencedor = self.jogadores[self.vencedor]
        texto_vencedor = self.fonte_vencedor.render(
            f"{vencedor['nome']} VENCEU!", True, vencedor['cor']
        )
        
        # Centralizar texto
        texto_x = msg_x + (msg_largura - texto_vencedor.get_width()) // 2
        texto_y = msg_y + (msg_altura - texto_vencedor.get_height()) // 2
        self.tela.blit(texto_vencedor, (texto_x, texto_y))

    def desenhar_estatisticas_jogadores(self):
        """Desenha as estatísticas de cada jogador"""
        stats_x = self.largura * 0.65
        stats_y = 420  # Abaixo das mensagens
        
        for i, jogador_id in enumerate([1, 2]):
            jogador = self.jogadores[jogador_id]
            stats = self.calcular_estatisticas_jogador(jogador_id)
            
            # Fundo das estatísticas
            stat_width = self.largura * 0.15
            stat_height = 180
            pygame.draw.rect(self.tela, (40, 40, 70), 
                           (stats_x + i * stat_width, stats_y, stat_width - 10, stat_height), 
                           border_radius=8)
            pygame.draw.rect(self.tela, jogador['cor'], 
                           (stats_x + i * stat_width, stats_y, stat_width - 10, stat_height), 
                           2, border_radius=8)
            
            # Título do jogador
            titulo = self.fonte.render(jogador['nome'], True, jogador['cor'])
            self.tela.blit(titulo, (stats_x + i * stat_width + 10, stats_y + 10))
            
            if stats:
                estatisticas = [
                    f"Lançamentos: {stats['total_lancamentos']}",
                    f"Média: {stats['media']:.2f}",
                    f"Mediana: {stats['mediana']:.1f}",
                    f"Moda: {stats['moda']}",
                    f"Desvio Padrão: {stats['desvio_padrao']:.2f}",
                    f"Variância: {stats['variancia']:.2f}",
                    f"Mín/Máx: {stats['minimo']}/{stats['maximo']}",
                    f"Soma Total: {stats['soma_total']}",
                    f"Posição: {jogador['posicao']}/{self.meta}"
                ]
                
                y_offset = stats_y + 40
                for stat in estatisticas:
                    texto = self.fonte_pequena.render(stat, True, self.cor_texto)
                    self.tela.blit(texto, (stats_x + i * stat_width + 10, y_offset))
                    y_offset += 20
            else:
                texto = self.fonte_pequena.render("Sem dados ainda", True, self.cor_texto)
                self.tela.blit(texto, (stats_x + i * stat_width + 10, stats_y + 50))

    def criar_grafico_comparacao(self):
        """Cria gráfico comparando os dois jogadores"""
        if len(self.jogadores[1]['dados']) < 2 or len(self.jogadores[2]['dados']) < 2:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.patch.set_facecolor('#1E1E3C')  # Cor de fundo uniforme
        
        # Gráfico 1: Distribuições comparadas
        for jogador_id in [1, 2]:
            dados = self.jogadores[jogador_id]['dados']
            if len(dados) > 0:
                valores, counts = np.unique(dados, return_counts=True)
                prob_empirica = counts / len(dados)
                cor = self.jogadores[jogador_id]['cor']
                ax1.bar(valores + (jogador_id-1.5)*0.3, prob_empirica, 0.3, 
                       alpha=0.7, label=f'{self.jogadores[jogador_id]["nome"]}', 
                       color=np.array(cor)/255)
        
        # Distribuição teórica
        teorica_dict = self.calcular_distribuicao_teorica()
        valores_teoricos = list(teorica_dict.keys())
        prob_teorica = [teorica_dict[v] for v in valores_teoricos]
        ax1.plot(valores_teoricos, prob_teorica, 'w--', alpha=0.5, label='Teórica')
        
        ax1.set_title('Distribuições Comparadas', color='white', fontsize=12)
        ax1.set_xlabel('Soma dos Dados', color='white')
        ax1.set_ylabel('Probabilidade', color='white')
        ax1.legend(facecolor='#2A2A4A', labelcolor='white', fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#2A2A4A')
        
        # Gráfico 2: Convergência das médias
        for jogador_id in [1, 2]:
            if self.historico_medias[jogador_id]:
                cor = self.jogadores[jogador_id]['cor']
                ax2.plot(self.historico_medias[jogador_id], 
                        color=np.array(cor)/255, 
                        linewidth=2,
                        label=f'{self.jogadores[jogador_id]["nome"]}')
        
        ax2.axhline(y=7, color='white', linestyle='--', alpha=0.5, label='Média Teórica')
        ax2.set_title('Convergência das Médias', color='white', fontsize=12)
        ax2.set_xlabel('Número de Lançamentos', color='white')
        ax2.set_ylabel('Média', color='white')
        ax2.legend(facecolor='#2A2A4A', labelcolor='white', fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#2A2A4A')
        
        # Configurar cores dos eixos
        for ax in [ax1, ax2]:
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        plt.tight_layout()
        
        # Converter para imagem pygame
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), 
                   bbox_inches='tight', dpi=80)
        buf.seek(0)
        image_surface = pygame.image.load(buf)
        buf.close()
        plt.close(fig)
        
        return image_surface

    def desenhar_interface_principal(self):
        """Desenha a interface principal do jogo"""
        # Área principal (lado esquerdo) - mesma cor do fundo
        area_principal = pygame.Rect(0, 0, self.largura * 0.6, self.altura)
        pygame.draw.rect(self.tela, self.cor_area_principal, area_principal)
        
        # Borda sutil entre as áreas
        pygame.draw.line(self.tela, (80, 80, 120), 
                        (self.largura * 0.6, 0), (self.largura * 0.6, self.altura), 2)
        
        # Título principal
        titulo = self.fonte_titulo.render("DUELO ESTATÍSTICO - CORRIDA DOS PEÕES", True, (255, 255, 0))
        self.tela.blit(titulo, (50, 30))
        
        # Botão de lançar dados
        cor_botao_jogar = self.cor_botao_hover if self.botao_jogar_hover else self.cor_botao
        pygame.draw.rect(self.tela, cor_botao_jogar, (50, 100, 400, 70), border_radius=15)
        pygame.draw.rect(self.tela, (255, 255, 255), (50, 100, 400, 70), 2, border_radius=15)
        
        texto_botao = "JOGAR DADOS" if not self.vencedor else "JOGO FINALIZADO"
        texto_lancar = self.fonte_titulo.render(texto_botao, True, self.cor_texto)
        self.tela.blit(texto_lancar, (80, 120))
        
        # Botão de reiniciar (ao lado do botão de jogar)
        cor_botao_reiniciar = self.cor_botao_reiniciar_hover if self.botao_reiniciar_hover else self.cor_botao_reiniciar
        pygame.draw.rect(self.tela, cor_botao_reiniciar, (470, 100, 200, 70), border_radius=15)
        pygame.draw.rect(self.tela, (255, 255, 255), (470, 100, 200, 70), 2, border_radius=15)
        
        texto_reiniciar = self.fonte_titulo.render("REINICIAR", True, self.cor_texto)
        self.tela.blit(texto_reiniciar, (500, 120))
        
        # Informações do turno
        if not self.vencedor:
            jogador_atual = self.jogadores[self.jogador_atual]
            texto_turno = self.fonte.render(
                f"Vez do: {jogador_atual['nome']}", True, jogador_atual['cor']
            )
            self.tela.blit(texto_turno, (50, 190))
        
        # Instruções
        instrucoes = [
            "REGRAS DA CORRIDA:",
            "- Cada jogador lança 2 dados por vez",
            "- Avança casas = resultado dos dados (máx 5 por turno)",
            "- Casas verdes: SORTE (avançar casas extras)",
            "- Casas vermelhas: AZAR (voltar casas)",
            "- Primeiro a chegar na casa 30 vence!",
            "- Estatísticas são calculadas em tempo real",
            "- Observe a convergência para a média teórica (7)",
            "",
            "CONTROLES:",
            "- CLIQUE no botão ou ESPAÇO para jogar",
            "- CLIQUE em REINICIAR ou R para novo jogo",
            "- ESC para sair"
        ]
        
        instrucoes_y = 250
        for instrucao in instrucoes:
            cor = (255, 255, 0) if "REGRAS" in instrucao or "CONTROLES" in instrucao else self.cor_texto
            fonte = self.fonte if "REGRAS" in instrucao or "CONTROLES" in instrucao else self.fonte_pequena
            texto = fonte.render(instrucao, True, cor)
            self.tela.blit(texto, (50, instrucoes_y))
            instrucoes_y += 25 if "REGRAS" in instrucao or "CONTROLES" in instrucao else 20

    def rodar(self):
        """Loop principal do jogo"""
        executando = True
        clock = pygame.time.Clock()
        
        print("Corrida Estatistica iniciada!")
        print("Dois peoes disputam quem chega primeiro a casa 30")
        print("Novo: Casas de SORTE (verde) e AZAR (vermelho) adicionadas!")
        print("Estatisticas sao calculadas em tempo real para cada jogador")
        
        while executando:
            mouse_pos = pygame.mouse.get_pos()
            
            # Verificar hover nos botões
            botao_jogar_rect = pygame.Rect(50, 100, 400, 70)
            botao_reiniciar_rect = pygame.Rect(470, 100, 200, 70)
            
            self.botao_jogar_hover = botao_jogar_rect.collidepoint(mouse_pos) and not self.vencedor
            self.botao_reiniciar_hover = botao_reiniciar_rect.collidepoint(mouse_pos)
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    executando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if self.botao_jogar_hover and not self.vencedor:
                        resultado = self.lancar_dados_jogador(self.jogador_atual)
                        if resultado:
                            print(f"Dados: {self.jogadores[self.jogador_atual]['nome']}: {resultado} pontos")
                            self.alternar_jogador()
                    elif self.botao_reiniciar_hover:
                        self.reiniciar_jogo()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE and not self.vencedor:
                        resultado = self.lancar_dados_jogador(self.jogador_atual)
                        if resultado:
                            print(f"Dados: {self.jogadores[self.jogador_atual]['nome']}: {resultado} pontos")
                            self.alternar_jogador()
                    elif evento.key == pygame.K_r:
                        self.reiniciar_jogo()
                    elif evento.key == pygame.K_ESCAPE:
                        executando = False
            
            # Limpar tela com cor uniforme
            self.tela.fill(self.cor_fundo)
            
            # Desenhar interface
            self.desenhar_interface_principal()
            self.desenhar_tabuleiro_corrida()
            self.desenhar_mensagem_evento()
            self.desenhar_mensagem_vencedor()
            self.desenhar_estatisticas_jogadores()
            
            # Desenhar gráficos comparativos
            try:
                grafico = self.criar_grafico_comparacao()
                if grafico:
                    self.tela.blit(grafico, (50, 450))
            except Exception as e:
                # Fallback simples se der erro no gráfico
                texto_erro = self.fonte_pequena.render("Gráfico disponível após alguns lançamentos", True, self.cor_texto)
                self.tela.blit(texto_erro, (50, 450))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

# Executar o jogo
if __name__ == "__main__":
    try:
        jogo = CorridaEstatistica()
        jogo.rodar()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")