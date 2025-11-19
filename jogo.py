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
        pygame.display.set_caption("Corrida Estatística - Gráficos com Eixos Nomeados")
        
        # Cores
        self.C_FUNDO = (30, 30, 45)
        self.C_PAINEL = (35, 35, 55)
        self.C_CASA_PADRAO = (200, 190, 170)
        self.C_CASA_SORTE = (100, 220, 100)
        self.C_CASA_AZAR = (220, 100, 100)
        self.C_BORDA = (60, 60, 60)
        self.C_JOGADOR1 = (255, 80, 80)
        self.C_JOGADOR2 = (80, 180, 255)
        self.C_TEXTO = (230, 230, 230)
        self.C_DESTAQUE = (255, 215, 0)
        
        # Fontes
        self.fonte_grande = pygame.font.SysFont('Arial', 26, bold=True)
        self.fonte_media = pygame.font.SysFont('Arial', 18)
        self.fonte_pequena = pygame.font.SysFont('Arial', 14, bold=True)
        self.fonte_mini = pygame.font.SysFont('Arial', 11)
        
        # --- LÓGICA DO JOGO ---
        self.meta = 30
        self.jogadores = {
            1: {'pos': 0, 'dados': [], 'cor': self.C_JOGADOR1, 'nome': 'Jogador 1'},
            2: {'pos': 0, 'dados': [], 'cor': self.C_JOGADOR2, 'nome': 'Jogador 2'}
        }
        self.turno_atual = 1
        self.vencedor = None
        self.historico_medias = {1: [], 2: []}
        
        # Estados de exibição
        self.msg_evento = ""
        self.timer_evento = 0
        self.ultimo_lancamento = (0, 0)
        self.ultimo_resultado_soma = 0
        self.timer_dados_visiveis = 0
        
        # Cache da imagem do gráfico
        self.img_grafico_cache = None
        self.dados_para_grafico_atualizados = False

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
        """Gera o layout Zig-Zag ajustado (Deslocado para a direita)"""
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
        self.jogadores[2]['pos'] = 0
        self.jogadores[2]['dados'] = []
        self.turno_atual = 1
        self.vencedor = None
        self.historico_medias = {1: [], 2: []}
        self.msg_evento = ""
        self.ultimo_lancamento = (0, 0)
        self.img_grafico_cache = None
        print("Jogo Reiniciado")

    def jogar_dados(self):
        if self.vencedor: return

        jog = self.jogadores[self.turno_atual]
        
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        soma = d1 + d2
        
        self.ultimo_lancamento = (d1, d2)
        self.ultimo_resultado_soma = soma
        self.timer_dados_visiveis = 90
        
        jog['dados'].append(soma)
        self.historico_medias[self.turno_atual].append(np.mean(jog['dados']))
        self.dados_para_grafico_atualizados = True
        
        movimento = min(soma, 5)
        pos_antiga = jog['pos']
        jog['pos'] += movimento
        
        self._verificar_consequencias(jog['pos'])
        
        if jog['pos'] >= self.meta - 1:
            jog['pos'] = self.meta - 1
            self.vencedor = self.turno_atual
            self.msg_evento = f"{jog['nome']} VENCEU!"
        
        if not self.vencedor:
            self.turno_atual = 3 - self.turno_atual

    def _verificar_consequencias(self, fim):
        idx = min(fim, self.meta - 1)
        if idx in self.casas_especiais:
            tipo, valor, texto = self.casas_especiais[idx]
            jog = self.jogadores[self.turno_atual]
            self.msg_evento = texto
            self.timer_evento = 120
            if tipo == "SORTE":
                jog['pos'] += valor
                self.msg_evento += f" (+{valor})"
            elif tipo == "AZAR":
                jog['pos'] -= valor
                if jog['pos'] < 0: jog['pos'] = 0
                self.msg_evento += f" (-{valor})"

    def _calcular_stats_texto(self, jogador_id):
        dados = self.jogadores[jogador_id]['dados']
        if not dados:
            return "Sem dados", "Sem dados", "Sem dados"
        media = np.mean(dados)
        mediana = np.median(dados)
        valores, contagens = np.unique(dados, return_counts=True)
        indice_moda = np.argmax(contagens)
        moda = valores[indice_moda]
        return f"{media:.2f}", f"{mediana:.1f}", f"{moda}"

    # --- DESENHAR DADO COM PONTOS ---
    def _desenhar_dado_pontos(self, x, y, tamanho, valor):
        rect = pygame.Rect(x, y, tamanho, tamanho)
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
            pygame.draw.lines(self.tela, (60, 60, 80), False, pontos, 5)
        for casa in self.rects_casas:
            rect = casa['rect']
            idx = casa['id']
            cor = self.C_CASA_PADRAO
            borda = self.C_BORDA
            largura_borda = 2
            if idx in self.casas_especiais:
                tipo = self.casas_especiais[idx][0]
                cor = self.C_CASA_SORTE if tipo == "SORTE" else self.C_CASA_AZAR
            if idx == self.meta - 1:
                cor = self.C_DESTAQUE
                borda = (255, 255, 255)
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
            pygame.draw.circle(self.tela, (0,0,0, 100), (cx+2, cy+2), 12)
            pygame.draw.circle(self.tela, dados['cor'], (cx, cy), 10)
            pygame.draw.circle(self.tela, (255,255,255), (cx, cy), 10, 2)
            if pid == self.turno_atual and not self.vencedor:
                pygame.draw.circle(self.tela, self.C_DESTAQUE, (cx, cy), 14, 2)

    def _desenhar_painel_esquerdo(self):
        w_painel = 380
        pygame.draw.rect(self.tela, self.C_PAINEL, (0, 0, w_painel, self.altura_tela))
        pygame.draw.line(self.tela, self.C_DESTAQUE, (w_painel, 0), (w_painel, self.altura_tela), 2)
        
        y_cursor = 15
        titulo = self.fonte_grande.render("CORRIDA ESTATÍSTICA", True, self.C_DESTAQUE)
        self.tela.blit(titulo, (20, y_cursor))
        
        y_cursor += 50
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        btn_jogar = pygame.Rect(20, y_cursor, 160, 45)
        cor_j = (0, 160, 0) if btn_jogar.collidepoint(mouse) else (0, 120, 0)
        pygame.draw.rect(self.tela, cor_j, btn_jogar, border_radius=6)
        txt_j = self.fonte_media.render("JOGAR (Espaço)", True, (255,255,255))
        self.tela.blit(txt_j, (btn_jogar.centerx - txt_j.get_width()//2, btn_jogar.centery - 10))
        if click and btn_jogar.collidepoint(mouse) and not self.vencedor:
            pygame.time.wait(150)
            self.jogar_dados()

        btn_reset = pygame.Rect(190, y_cursor, 160, 45)
        cor_r = (160, 0, 0) if btn_reset.collidepoint(mouse) else (120, 0, 0)
        pygame.draw.rect(self.tela, cor_r, btn_reset, border_radius=6)
        txt_r = self.fonte_media.render("RESET (R)", True, (255,255,255))
        self.tela.blit(txt_r, (btn_reset.centerx - txt_r.get_width()//2, btn_reset.centery - 10))
        if click and btn_reset.collidepoint(mouse):
            self.reiniciar()

        y_cursor += 60
        if not self.vencedor:
            nome = self.jogadores[self.turno_atual]['nome']
            cor = self.jogadores[self.turno_atual]['cor']
            txt_vez = self.fonte_media.render(f"Vez de: {nome}", True, cor)
            self.tela.blit(txt_vez, (20, y_cursor))
        else:
            txt_venc = self.fonte_grande.render("JOGO ENCERRADO", True, self.C_DESTAQUE)
            self.tela.blit(txt_venc, (20, y_cursor))

        # --- EXIBIÇÃO DOS DADOS ---
        y_cursor += 30
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
            y_cursor += 20

        y_cursor += 10
        if self.timer_evento > 0:
            r_msg = pygame.Rect(20, y_cursor, 340, 30)
            pygame.draw.rect(self.tela, (50, 50, 0), r_msg, border_radius=5)
            t_msg = self.fonte_media.render(self.msg_evento, True, (255, 255, 100))
            self.tela.blit(t_msg, (30, y_cursor + 5))
            self.timer_evento -= 1

        y_grafico = y_cursor + 40
        altura_disp = self.altura_tela - y_grafico - 10
        if self.dados_para_grafico_atualizados or self.img_grafico_cache is None:
            self._gerar_grafico_matplotlib(3.8, altura_disp / 80)
            self.dados_para_grafico_atualizados = False
        if self.img_grafico_cache:
            self.tela.blit(self.img_grafico_cache, (10, y_grafico))

    def _gerar_grafico_matplotlib(self, w_inch, h_inch):
        if len(self.jogadores[1]['dados']) < 1: return
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(w_inch + 1, h_inch))
        fig.patch.set_facecolor('#232337')
        
        for pid in [1, 2]:
            dados = self.jogadores[pid]['dados']
            if dados:
                vals, counts = np.unique(dados, return_counts=True)
                freq = counts / len(dados)
                cor = np.array(self.jogadores[pid]['cor']) / 255
                offset = -0.15 if pid == 1 else 0.15
                ax1.bar(vals + offset, freq, width=0.3, color=cor, alpha=0.7, label=f"J{pid}")

        x_teo = np.arange(2, 13)
        prob_teo = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
        prob_teo = [p/36 for p in prob_teo]
        ax1.plot(x_teo, prob_teo, 'w--', linewidth=1, alpha=0.5, label="Teórico")
        
        ax1.set_title("Frequência", color='white', fontsize=10)
        # --- NOMES DOS EIXOS (GRÁFICO 1) ---
        ax1.set_xlabel('Soma', color='white', fontsize=8)
        ax1.set_ylabel('Prob', color='white', fontsize=8)
        
        ax1.tick_params(colors='white', labelsize=8)
        ax1.set_facecolor('#232337')
        
        for pid in [1, 2]:
            medias = self.historico_medias[pid]
            if medias:
                cor = np.array(self.jogadores[pid]['cor']) / 255
                ax2.plot(medias, color=cor, linewidth=1.5)
        
        ax2.axhline(7, color='white', linestyle='--', alpha=0.5)
        ax2.set_title("Conv. Média", color='white', fontsize=10)
        # --- NOMES DOS EIXOS (GRÁFICO 2) ---
        ax2.set_xlabel('Lançamentos', color='white', fontsize=8)
        ax2.set_ylabel('Média', color='white', fontsize=8)
        
        ax2.tick_params(colors='white', labelsize=8)
        ax2.set_facecolor('#232337')

        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_color('white')
            ax.grid(True, alpha=0.1)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#232337')
        buf.seek(0)
        plt.close(fig)
        self.img_grafico_cache = pygame.image.load(buf)

    def rodar(self):
        clock = pygame.time.Clock()
        rodando = True
        while rodando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: rodando = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: self.jogar_dados()
                    if event.key == pygame.K_r: self.reiniciar()
                    if event.key == pygame.K_ESCAPE: rodando = False

            self.tela.fill(self.C_FUNDO)
            self._desenhar_painel_esquerdo()
            self._desenhar_tabuleiro()
            self._desenhar_peoes()
            
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    CorridaEstatistica().rodar()