import pygame
import numpy as np
import matplotlib.pyplot as plt
import random
import io
import sys
import os

# Configurar matplotlib para renderizar em memória (backend Agg)
plt.switch_backend('Agg')

class CorridaEstatistica:
    def __init__(self):
        pygame.init()
        
        # --- CONFIGURAÇÕES DE TELA ---
        self.largura_tela, self.altura_tela = 1150, 720
        self.tela = pygame.display.set_mode((self.largura_tela, self.altura_tela), pygame.RESIZABLE)
        pygame.display.set_caption("Corrida Estatística - Análise de Probabilidade em Tempo Real")
        
        # Cores atualizadas - tema mais moderno
        self.C_FUNDO = (20, 25, 35)
        self.C_PAINEL = (30, 35, 50)
        self.C_CASA_PADRAO = (220, 210, 190)
        self.C_CASA_SORTE = (80, 200, 120)
        self.C_CASA_AZAR = (220, 90, 90)
        self.C_BORDA = (80, 80, 100)
        self.C_JOGADOR1 = (255, 100, 100)
        self.C_JOGADOR2 = (80, 180, 255)
        self.C_TEXTO = (240, 240, 240)
        self.C_DESTAQUE = (255, 215, 0)
        self.C_BOTAO = (60, 140, 200)
        self.C_BOTAO_HOVER = (80, 160, 220)
        self.C_PODER = (180, 100, 220)
        
        # Fontes
        self.fonte_grande = pygame.font.SysFont('Arial', 28, bold=True)
        self.fonte_media = pygame.font.SysFont('Arial', 20)
        self.fonte_pequena = pygame.font.SysFont('Arial', 16, bold=True)
        self.fonte_mini = pygame.font.SysFont('Arial', 12)
        
        # --- LÓGICA DO JOGO ---
        self.meta = 30
        self.jogadores = {
            1: {'pos': 0, 'dados': [], 'cor': self.C_JOGADOR1, 'nome': 'Jogador 1', 'poder': None, 'poder_usado': False},
            2: {'pos': 0, 'dados': [], 'cor': self.C_JOGADOR2, 'nome': 'Jogador 2', 'poder': None, 'poder_usado': False}
        }
        self.turno_atual = 1
        self.vencedor = None
        self.historico_medias = {1: [], 2: []}
        self.historico_lancamentos = {1: [], 2: []}
        
        # Estados de exibição
        self.msg_evento = ""
        self.timer_evento = 0
        self.ultimo_lancamento = (0, 0)
        self.ultimo_resultado_soma = 0
        self.timer_dados_visiveis = 0
        
        # Cache da imagem do gráfico
        self.img_grafico_cache = None
        self.dados_para_grafico_atualizados = False
        
        # Sistema de poderes
        self.poderes_disponiveis = [
            {"nome": "Dobrar Dados", "descricao": "Próximo lançamento é dobrado", "cor": (255, 150, 50)},
            {"nome": "Retroceder Oponente", "descricao": "Oponente volta 3 casas", "cor": (200, 80, 80)},
            {"nome": "Trocar Posições", "descricao": "Troca de lugar com oponente", "cor": (150, 100, 200)},
            {"nome": "Jogar Novamente", "descricao": "Joga os dados novamente", "cor": (80, 180, 120)}
        ]
        
        # Estados do jogo
        self.estado = "menu"
        self.jogador_selecionando_poder = 1

        # Casas Especiais
        self.casas_especiais = {
            3: ("SORTE", 2, "Atalho! +2"), 8: ("SORTE", 3, "Vento! +3"),
            12: ("SORTE", 1, "Passo! +1"), 18: ("SORTE", 2, "Escada! +2"),
            22: ("SORTE", 4, "Jato! +4"), 28: ("SORTE", 1, "Quase! +1"),
            4: ("AZAR", 2, "Queda! -2"), 7: ("AZAR", 3, "Buraco! -3"),
            11: ("AZAR", 1, "Ops! -1"), 14: ("AZAR", 2, "Volta! -2"),
            17: ("AZAR", 4, "Crise! -4"), 21: ("AZAR", 2, "Recuo! -2"),
            26: ("AZAR", 3, "Monstro! -3")
        }

        # Gerar Tabuleiro
        self.rects_casas = []
        self._gerar_layout_tabuleiro()

    def _gerar_layout_tabuleiro(self):
        """Gera o layout Zig-Zag ajustado"""
        self.rects_casas = []
        
        painel_w = 380
        margem_esquerda_extra = 120 
        area_x_offset = painel_w + margem_esquerda_extra
        area_y_offset = 50
        
        area_w = self.largura_tela - area_x_offset - 30
        area_h = self.altura_tela - area_y_offset - 30
        
        cols = 6
        linhas = 5
        
        largura_celula = area_w / cols
        altura_celula = area_h / linhas
        margem = 6
        
        for i in range(self.meta):
            linha = i // cols
            coluna = i % cols
            
            if linha % 2 == 1:
                coluna = (cols - 1) - coluna
            
            linha_visual = (linhas - 1) - linha
            
            x = area_x_offset + (coluna * largura_celula) + margem
            y = area_y_offset + (linha_visual * altura_celula) + margem
            w = largura_celula - (margem * 2)
            h = altura_celula - (margem * 2)
            
            r = pygame.Rect(x, y, w, h)
            self.rects_casas.append({'rect': r, 'id': i, 'center': r.center})

    def reiniciar(self):
        self.jogadores[1]['pos'] = 0
        self.jogadores[1]['dados'] = []
        self.jogadores[1]['poder'] = None
        self.jogadores[1]['poder_usado'] = False
        self.jogadores[2]['pos'] = 0
        self.jogadores[2]['dados'] = []
        self.jogadores[2]['poder'] = None
        self.jogadores[2]['poder_usado'] = False
        self.turno_atual = 1
        self.vencedor = None
        self.historico_medias = {1: [], 2: []}
        self.historico_lancamentos = {1: [], 2: []}
        self.msg_evento = ""
        self.ultimo_lancamento = (0, 0)
        self.img_grafico_cache = None
        self.estado = "menu"
        self.jogador_selecionando_poder = 1

    def selecionar_poder(self, jogador_id, poder_index):
        """Atribui um poder ao jogador"""
        if 0 <= poder_index < len(self.poderes_disponiveis):
            self.jogadores[jogador_id]['poder'] = self.poderes_disponiveis[poder_index]
            self.jogadores[jogador_id]['poder_usado'] = False
            
            if jogador_id == 1:
                self.jogador_selecionando_poder = 2
            else:
                self.estado = "jogando"

    def usar_poder(self, jogador_id):
        """Ativa o poder do jogador atual"""
        jogador = self.jogadores[jogador_id]
        oponente_id = 3 - jogador_id
        
        if jogador['poder'] is None or jogador['poder_usado']:
            return False
            
        poder_nome = jogador['poder']['nome']
        jogador['poder_usado'] = True
        
        if poder_nome == "Dobrar Dados":
            self.msg_evento = f"{jogador['nome']} usou {poder_nome}!"
            self.poder_dobrar_ativa = True
            
        elif poder_nome == "Retroceder Oponente":
            self.jogadores[oponente_id]['pos'] = max(0, self.jogadores[oponente_id]['pos'] - 3)
            self.msg_evento = f"{jogador['nome']} usou {poder_nome}!"
            
        elif poder_nome == "Trocar Posições":
            pos_temp = jogador['pos']
            jogador['pos'] = self.jogadores[oponente_id]['pos']
            self.jogadores[oponente_id]['pos'] = pos_temp
            self.msg_evento = f"{jogador['nome']} usou {poder_nome}!"
            
        elif poder_nome == "Jogar Novamente":
            self.msg_evento = f"{jogador['nome']} usou {poder_nome}!"
            self.turno_extra = True
            
        self.timer_evento = 120
        return True

    def jogar_dados(self):
        if self.vencedor or self.estado != "jogando": 
            return

        jog = self.jogadores[self.turno_atual]
        
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        soma = d1 + d2
        
        # Aplicar poder de dobrar dados se estiver ativo
        if hasattr(self, 'poder_dobrar_ativa') and self.poder_dobrar_ativa:
            soma = soma * 2
            self.poder_dobrar_ativa = False
            self.msg_evento = f"Dados dobrados! Movimento: {soma} casas"
        else:
            self.msg_evento = f"Movimento: {soma} casas"
            
        self.timer_evento = 90
            
        self.ultimo_lancamento = (d1, d2)
        self.ultimo_resultado_soma = soma
        self.timer_dados_visiveis = 90
        
        # Armazenar dados para estatísticas
        jog['dados'].append(soma)
        self.historico_lancamentos[self.turno_atual].append((d1, d2))
        self.historico_medias[self.turno_atual].append(np.mean(jog['dados']))
        self.dados_para_grafico_atualizados = True
        
        # MOVIMENTO CORRETO: usar o valor real da soma
        movimento = soma
        pos_antiga = jog['pos']
        jog['pos'] += movimento
        
        # Verificar casas especiais apenas na posição final (evita recursão)
        self._verificar_consequencias_final(jog['pos'])
        
        # Verificar vitória
        if jog['pos'] >= self.meta - 1:
            jog['pos'] = self.meta - 1
            self.vencedor = self.turno_atual
            self.msg_evento = f"{jog['nome']} VENCEU!"
            self.estado = "fim"
        
        # Mudar turno (a menos que haja turno extra)
        if not self.vencedor and not hasattr(self, 'turno_extra'):
            self.turno_atual = 3 - self.turno_atual
        elif hasattr(self, 'turno_extra'):
            del self.turno_extra

    def _verificar_consequencias_final(self, posicao):
        """Verifica consequências apenas na posição final (evita recursão infinita)"""
        if posicao >= self.meta:
            return
            
        if posicao in self.casas_especiais:
            tipo, valor, texto = self.casas_especiais[posicao]
            jog = self.jogadores[self.turno_atual]
            
            self.msg_evento = f"{texto} na casa {posicao + 1}"
            self.timer_evento = 120
            
            if tipo == "SORTE":
                jog['pos'] += valor
                self.msg_evento += f" (+{valor})"
            elif tipo == "AZAR":
                jog['pos'] = max(0, jog['pos'] - valor)
                self.msg_evento += f" (-{valor})"

    def _calcular_stats_texto(self, jogador_id):
        dados = self.jogadores[jogador_id]['dados']
        if not dados:
            return "-", "-", "-"
        media = np.mean(dados)
        mediana = np.median(dados)
        valores, contagens = np.unique(dados, return_counts=True)
        indice_moda = np.argmax(contagens)
        moda = valores[indice_moda]
        return f"{media:.2f}", f"{mediana:.1f}", f"{moda}"

    def _desenhar_dado_pontos(self, x, y, tamanho, valor):
        rect = pygame.Rect(x, y, tamanho, tamanho)
        pygame.draw.rect(self.tela, (10, 10, 10), (x+2, y+2, tamanho, tamanho), border_radius=8)
        pygame.draw.rect(self.tela, (245, 245, 245), rect, border_radius=8)
        pygame.draw.rect(self.tela, (20, 20, 20), rect, 2, border_radius=8)
        
        raio = tamanho // 9
        cor_ponto = (0, 0, 0)
        
        cx, cy = x + tamanho//2, y + tamanho//2
        tl_x, tl_y = x + tamanho//4, y + tamanho//4
        tr_x, tr_y = x + 3*tamanho//4, y + tamanho//4
        bl_x, bl_y = x + tamanho//4, y + 3*tamanho//4
        br_x, br_y = x + 3*tamanho//4, y + 3*tamanho//4
        ml_x, ml_y = x + tamanho//4, y + tamanho//2
        mr_x, mr_y = x + 3*tamanho//4, y + tamanho//2
        
        pontos = []
        if valor == 1: pontos = [(cx, cy)]
        elif valor == 2: pontos = [(tl_x, tl_y), (br_x, br_y)]
        elif valor == 3: pontos = [(tl_x, tl_y), (cx, cy), (br_x, br_y)]
        elif valor == 4: pontos = [(tl_x, tl_y), (tr_x, tr_y), (bl_x, bl_y), (br_x, br_y)]
        elif valor == 5: pontos = [(tl_x, tl_y), (tr_x, tr_y), (cx, cy), (bl_x, bl_y), (br_x, br_y)]
        elif valor == 6: pontos = [(tl_x, tl_y), (tr_x, tr_y), (ml_x, ml_y), (mr_x, mr_y), (bl_x, bl_y), (br_x, br_y)]
            
        for px, py in pontos:
            pygame.draw.circle(self.tela, cor_ponto, (int(px), int(py)), raio)

    def _desenhar_tabuleiro(self):
        if len(self.rects_casas) > 1:
            pontos = [c['center'] for c in self.rects_casas]
            pygame.draw.lines(self.tela, (80, 80, 100), False, pontos, 8)
            
        for casa in self.rects_casas:
            rect = casa['rect']
            idx = casa['id']
            cor = self.C_CASA_PADRAO
            borda = self.C_BORDA
            largura_borda = 2
            
            shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
            pygame.draw.rect(self.tela, (10, 10, 10), shadow_rect, border_radius=8)
            
            if idx in self.casas_especiais:
                tipo = self.casas_especiais[idx][0]
                cor = self.C_CASA_SORTE if tipo == "SORTE" else self.C_CASA_AZAR
            if idx == self.meta - 1:
                cor = self.C_DESTAQUE
                borda = (255, 255, 200)
                largura_borda = 4
                
            pygame.draw.rect(self.tela, cor, rect, border_radius=8)
            pygame.draw.rect(self.tela, borda, rect, largura_borda, border_radius=8)
            
            txt = self.fonte_pequena.render(str(idx + 1), True, (50, 50, 50))
            self.tela.blit(txt, (rect.x + 5, rect.y + 5))
            
            if idx in self.casas_especiais:
                label = self.casas_especiais[idx][2].split('!')[0]
                txt_evt = self.fonte_mini.render(label, True, (0, 0, 0))
                self.tela.blit(txt_evt, (rect.centerx - txt_evt.get_width()//2, rect.centery))
                
            if idx == self.meta - 1:
                txt_meta = self.fonte_grande.render("META", True, (0,0,0))
                self.tela.blit(txt_meta, (rect.centerx - txt_meta.get_width()//2, rect.centery - 10))

    def _desenhar_peoes(self):
        for pid, dados in self.jogadores.items():
            pos_idx = min(dados['pos'], len(self.rects_casas) - 1)
            rect = self.rects_casas[pos_idx]['rect']
            cx, cy = rect.center
            cx += -12 if pid == 1 else 12
            cy += 8
            
            pygame.draw.circle(self.tela, (0,0,0), (cx+2, cy+2), 14)
            pygame.draw.circle(self.tela, dados['cor'], (cx, cy), 12)
            pygame.draw.circle(self.tela, (255,255,255), (cx, cy), 12, 2)
            
            if pid == self.turno_atual and not self.vencedor and self.estado == "jogando":
                pygame.draw.circle(self.tela, self.C_DESTAQUE, (cx, cy), 16, 3)

    def _desenhar_botao(self, rect, texto, cor_normal, cor_hover, fonte):
        mouse = pygame.mouse.get_pos()
        cor = cor_hover if rect.collidepoint(mouse) else cor_normal
        
        shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        pygame.draw.rect(self.tela, (10, 10, 10), shadow_rect, border_radius=8)
        
        pygame.draw.rect(self.tela, cor, rect, border_radius=8)
        pygame.draw.rect(self.tela, (240, 240, 240), rect, 2, border_radius=8)
        
        txt = fonte.render(texto, True, (255, 255, 255))
        self.tela.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
        
        return rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]

    def _desenhar_menu(self):
        self.tela.fill(self.C_FUNDO)
        
        titulo = self.fonte_grande.render("CORRIDA ESTATÍSTICA", True, self.C_DESTAQUE)
        subtitulo = self.fonte_media.render("Análise de Probabilidade em Tempo Real", True, self.C_TEXTO)
        
        self.tela.blit(titulo, (self.largura_tela//2 - titulo.get_width()//2, 120))
        self.tela.blit(subtitulo, (self.largura_tela//2 - subtitulo.get_width()//2, 170))
        
        btn_largura, btn_altura = 300, 60
        btn_x = self.largura_tela//2 - btn_largura//2
        
        btn_iniciar = pygame.Rect(btn_x, 280, btn_largura, btn_altura)
        if self._desenhar_botao(btn_iniciar, "INICIAR JOGO", self.C_BOTAO, self.C_BOTAO_HOVER, self.fonte_media):
            self.estado = "selecao_poder"
            self.jogador_selecionando_poder = 1
            pygame.time.delay(300)
        
        btn_sair = pygame.Rect(btn_x, 360, btn_largura, btn_altura)
        if self._desenhar_botao(btn_sair, "SAIR", (160, 60, 60), (180, 80, 80), self.fonte_media):
            pygame.quit()
            sys.exit()
        
        instrucoes = [
            "• Cada jogador escolhe um poder no início",
            "• Use poderes estrategicamente durante o jogo",
            "• Lance os dados e avance no tabuleiro",
            "• Cuidado com as casas de azar!",
            "• Primeiro a chegar na META vence!",
            "• Gráficos mostram distribuições em tempo real"
        ]
        
        for i, texto in enumerate(instrucoes):
            linha = self.fonte_pequena.render(texto, True, self.C_TEXTO)
            self.tela.blit(linha, (self.largura_tela//2 - linha.get_width()//2, 460 + i * 30))

    def _desenhar_selecao_poder(self):
        self.tela.fill(self.C_FUNDO)
        
        titulo = self.fonte_grande.render(f"{self.jogadores[self.jogador_selecionando_poder]['nome']} - Escolha seu Poder", 
                                         True, self.jogadores[self.jogador_selecionando_poder]['cor'])
        self.tela.blit(titulo, (self.largura_tela//2 - titulo.get_width()//2, 30))
        
        instrucao = self.fonte_media.render("Cada jogador pode usar seu poder UMA VEZ durante o jogo", 
                                           True, self.C_DESTAQUE)
        self.tela.blit(instrucao, (self.largura_tela//2 - instrucao.get_width()//2, 80))
        
        poder_largura = 250
        poder_altura = 120
        espacamento = 30
        total_largura = 2 * poder_largura + espacamento
        start_x = (self.largura_tela - total_largura) // 2
        start_y = 150
        
        for i, poder in enumerate(self.poderes_disponiveis):
            linha = i // 2
            coluna = i % 2
            
            x = start_x + coluna * (poder_largura + espacamento)
            y = start_y + linha * (poder_altura + espacamento)
            
            rect = pygame.Rect(x, y, poder_largura, poder_altura)
            
            shadow_rect = pygame.Rect(x + 4, y + 4, poder_largura, poder_altura)
            pygame.draw.rect(self.tela, (10, 10, 10), shadow_rect, border_radius=12)
            
            pygame.draw.rect(self.tela, poder['cor'], rect, border_radius=12)
            pygame.draw.rect(self.tela, (240, 240, 240), rect, 2, border_radius=12)
            
            nome_texto = self.fonte_media.render(poder['nome'], True, (255, 255, 255))
            self.tela.blit(nome_texto, (rect.centerx - nome_texto.get_width()//2, y + 15))
            
            desc_texto = self.fonte_pequena.render(poder['descricao'], True, (240, 240, 240))
            self.tela.blit(desc_texto, (rect.centerx - desc_texto.get_width()//2, y + 55))
            
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.selecionar_poder(self.jogador_selecionando_poder, i)
                pygame.time.delay(300)

    def _desenhar_painel_esquerdo(self):
        w_painel = 380
        for i in range(w_painel):
            alpha = i / w_painel
            cor = (
                int(self.C_PAINEL[0] * (1 - alpha) + self.C_FUNDO[0] * alpha),
                int(self.C_PAINEL[1] * (1 - alpha) + self.C_FUNDO[1] * alpha),
                int(self.C_PAINEL[2] * (1 - alpha) + self.C_FUNDO[2] * alpha)
            )
            pygame.draw.line(self.tela, cor, (i, 0), (i, self.altura_tela))
        
        y_cursor = 15
        
        titulo = self.fonte_grande.render("ANÁLISE ESTATÍSTICA", True, self.C_DESTAQUE)
        self.tela.blit(titulo, (20, y_cursor))
        y_cursor += 50
        
        btn_jogar = pygame.Rect(20, y_cursor, 160, 45)
        if self._desenhar_botao(btn_jogar, "JOGAR (Espaço)", 
                               self.C_BOTAO, self.C_BOTAO_HOVER, self.fonte_media):
            if not self.vencedor and self.estado == "jogando":
                pygame.time.wait(150)
                self.jogar_dados()

        btn_reset = pygame.Rect(190, y_cursor, 160, 45)
        if self._desenhar_botao(btn_reset, "RESET (R)", 
                               (160, 60, 60), (180, 80, 80), self.fonte_media):
            self.reiniciar()

        y_cursor += 60
        
        if self.estado == "jogando" and not self.vencedor:
            nome = self.jogadores[self.turno_atual]['nome']
            cor = self.jogadores[self.turno_atual]['cor']
            txt_vez = self.fonte_media.render(f"Vez de: {nome}", True, cor)
            self.tela.blit(txt_vez, (20, y_cursor))
        elif self.estado == "fim":
            txt_venc = self.fonte_grande.render("JOGO ENCERRADO", True, self.C_DESTAQUE)
            self.tela.blit(txt_venc, (20, y_cursor))

        y_cursor += 40
        if self.timer_dados_visiveis > 0:
            d1, d2 = self.ultimo_lancamento
            soma = self.ultimo_resultado_soma
            tamanho_dado = 50
            self._desenhar_dado_pontos(20, y_cursor, tamanho_dado, d1)
            self._desenhar_dado_pontos(80, y_cursor, tamanho_dado, d2)
            txt_soma = self.fonte_grande.render(f"= {soma}", True, (255,255,255))
            self.tela.blit(txt_soma, (140, y_cursor + 10))
            self.timer_dados_visiveis -= 1

        y_cursor += 60
        
        if self.estado == "jogando" and not self.vencedor:
            jogador = self.jogadores[self.turno_atual]
            if jogador['poder'] and not jogador['poder_usado']:
                btn_poder = pygame.Rect(20, y_cursor, 330, 40)
                if self._desenhar_botao(btn_poder, f"USAR PODER: {jogador['poder']['nome']}", 
                                       self.C_PODER, (200, 120, 240), self.fonte_pequena):
                    self.usar_poder(self.turno_atual)
                y_cursor += 50

        y_cursor += 20
        pygame.draw.line(self.tela, (100,100,100), (20, y_cursor), (360, y_cursor), 1)
        y_cursor += 10
        
        col_x = [20, 100, 180, 260]
        titulos = ["", "Média", "Mediana", "Moda"]
        for i, t in enumerate(titulos):
            surf = self.fonte_pequena.render(t, True, (180,180,180))
            self.tela.blit(surf, (col_x[i], y_cursor))
        
        y_cursor += 25
        for pid in [1, 2]:
            media, mediana, moda = self._calcular_stats_texto(pid)
            cor = self.jogadores[pid]['cor']
            t_nome = self.fonte_pequena.render(f"Jog {pid}", True, cor)
            self.tela.blit(t_nome, (col_x[0], y_cursor))
            for i, val in enumerate([media, mediana, moda]):
                t_val = self.fonte_pequena.render(val, True, (255,255,255))
                self.tela.blit(t_val, (col_x[i+1], y_cursor))
            
            if self.jogadores[pid]['poder']:
                status = "✓" if self.jogadores[pid]['poder_usado'] else "●"
                cor_status = (150,150,150) if self.jogadores[pid]['poder_usado'] else self.jogadores[pid]['poder']['cor']
                txt_poder = self.fonte_mini.render(f"{status} {self.jogadores[pid]['poder']['nome']}", True, cor_status)
                self.tela.blit(txt_poder, (20, y_cursor + 15))
            
            y_cursor += 35

        y_cursor += 10
        
        if self.timer_evento > 0:
            r_msg = pygame.Rect(20, y_cursor, 340, 40)
            pygame.draw.rect(self.tela, (40, 40, 20), r_msg, border_radius=5)
            pygame.draw.rect(self.tela, (255, 255, 100), r_msg, 1, border_radius=5)
            
            if len(self.msg_evento) > 25:
                t_msg = self.fonte_pequena.render(self.msg_evento, True, (255, 255, 100))
            else:
                t_msg = self.fonte_media.render(self.msg_evento, True, (255, 255, 100))
                
            text_rect = t_msg.get_rect(center=r_msg.center)
            self.tela.blit(t_msg, text_rect)
            
            self.timer_evento -= 1
            y_cursor += 50

        y_grafico = y_cursor + 20
        altura_disp = self.altura_tela - y_grafico - 10
        if self.dados_para_grafico_atualizados or self.img_grafico_cache is None:
            self._gerar_grafico_matplotlib(3.8, altura_disp / 80)
            self.dados_para_grafico_atualizados = False
        if self.img_grafico_cache:
            self.tela.blit(self.img_grafico_cache, (10, y_grafico))

    def _gerar_grafico_matplotlib(self, w_inch, h_inch):
        """Gera gráficos estatísticos precisos em tempo real"""
        todos_dados = []
        for pid in [1, 2]:
            todos_dados.extend(self.jogadores[pid]['dados'])
        
        if len(todos_dados) < 1:
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(w_inch + 1, h_inch))
        fig.patch.set_facecolor('#141923')
        
        # Gráfico 1: Distribuição de frequência CORRETA
        if todos_dados:
            # Calcular distribuição empírica correta
            valores_possiveis = range(2, 13)
            freq_empirica = []
            
            for valor in valores_possiveis:
                freq = todos_dados.count(valor) / len(todos_dados)
                freq_empirica.append(freq)
            
            # Plot para cada jogador
            for pid in [1, 2]:
                dados_jogador = self.jogadores[pid]['dados']
                if len(dados_jogador) > 0:
                    freq_jogador = []
                    for valor in valores_possiveis:
                        freq = dados_jogador.count(valor) / len(dados_jogador)
                        freq_jogador.append(freq)
                    
                    cor = np.array(self.jogadores[pid]['cor']) / 255
                    ax1.bar(np.array(valores_possiveis) - 0.2 + (pid-1)*0.4, freq_jogador, 
                           width=0.35, color=cor, alpha=0.7, label=f"J{pid}")

            # Distribuição teórica CORRETA para dois dados
            prob_teo = [1/36, 2/36, 3/36, 4/36, 5/36, 6/36, 5/36, 4/36, 3/36, 2/36, 1/36]
            
            ax1.plot(valores_possiveis, prob_teo, 'w-', linewidth=2, alpha=0.8, label="Teórico")
            ax1.fill_between(valores_possiveis, prob_teo, alpha=0.2, color='white')
            
            ax1.set_title("Distribuição de Probabilidade", color='white', fontsize=10, pad=10)
            ax1.set_xlabel('Soma dos Dados', color='white', fontsize=9)
            ax1.set_ylabel('Frequência Relativa', color='white', fontsize=9)
            ax1.legend(fontsize=7, facecolor='#232337', loc='upper right')
            ax1.set_xticks(range(2, 13))
            ax1.grid(True, alpha=0.3, color='gray')
            
            ax1.tick_params(colors='white', labelsize=8)
            ax1.set_facecolor('#232337')

        # Gráfico 2: Convergência da média CORRETA
        ax2.clear()
        for pid in [1, 2]:
            medias = self.historico_medias[pid]
            if len(medias) > 0:
                cor = np.array(self.jogadores[pid]['cor']) / 255
                ax2.plot(range(1, len(medias)+1), medias, 
                        color=cor, linewidth=2, label=f"J{pid}")
        
        # Linha da média teórica
        ax2.axhline(7, color='white', linestyle='--', linewidth=2, alpha=0.7, 
                   label="Média Teórica = 7.0")
        
        ax2.set_title("Lei dos Grandes Números", color='white', fontsize=10, pad=10)
        ax2.set_xlabel('Número de Lançamentos', color='white', fontsize=9)
        ax2.set_ylabel('Média Acumulada', color='white', fontsize=9)
        ax2.legend(fontsize=7, facecolor='#232337')
        ax2.grid(True, alpha=0.3, color='gray')
        
        ax2.tick_params(colors='white', labelsize=8)
        ax2.set_facecolor('#232337')

        # Estilização consistente
        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_color('white')
            
        plt.tight_layout(pad=2.0)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#141923', dpi=100, 
                   bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        plt.close(fig)
        
        self.img_grafico_cache = pygame.image.load(buf)
        buf.close()

    def rodar(self):
        clock = pygame.time.Clock()
        rodando = True
        while rodando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    rodando = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.estado == "jogando": 
                        self.jogar_dados()
                    if event.key == pygame.K_r: 
                        self.reiniciar()
                    if event.key == pygame.K_ESCAPE: 
                        rodando = False

            self.tela.fill(self.C_FUNDO)
            
            if self.estado == "menu":
                self._desenhar_menu()
            elif self.estado == "selecao_poder":
                self._desenhar_selecao_poder()
            else:
                self._desenhar_painel_esquerdo()
                self._desenhar_tabuleiro()
                self._desenhar_peoes()
            
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    CorridaEstatistica().rodar()