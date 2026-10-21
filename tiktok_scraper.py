from playwright.sync_api import sync_playwright

class ScraperTikTok:
    def __init__(self, usuario, max_videos=10):
        self.usuario = usuario
        self.max_videos = max_videos
        self.url = f"https://www.tiktok.com/@{self.usuario}"
        
        # Variables de instancia para Playwright
        self.playwright = None
        self.browser = None
        self.page = None

    def iniciar(self):
        """Inicializa el navegador levantando la sesión de Playwright."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        self.page = context.new_page()

    def cerrar(self):
        """Cierra el navegador y detiene Playwright."""
        print("\nCerrando navegador...")
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _obtener_texto(self, selectores, usar_ultimo=False, valor_por_defecto="0"):
        """Método auxiliar interno para extraer texto de los localizadores de forma segura."""
        try:
            elemento = self.page.locator(selectores)
            if elemento.count() > 0:
                return elemento.last.inner_text() if usar_ultimo else elemento.first.inner_text()
            return valor_por_defecto
        except Exception:
            return valor_por_defecto

    def raspar_perfil(self):
        """Extrae la información principal del perfil."""
        print(f"Accediendo a: {self.url}")
        try:
            self.page.goto(self.url, timeout=30000)
        except Exception:
            pass # Ignoramos timeout de carga pesada
            
        print("Esperando validación (Resuelve el CAPTCHA si aparece)...")
        self.page.wait_for_selector('[data-e2e="followers-count"]', timeout=60000)
        
        datos_perfil = {
            "usuario": f"@{self.usuario}",
            "seguidores": self._obtener_texto('[data-e2e="followers-count"]'),
            "siguiendo": self._obtener_texto('[data-e2e="following-count"]'),
            "interacciones_totales": self._obtener_texto('[data-e2e="likes-count"]'),
            "biografia": self._obtener_texto('[data-e2e="user-bio"]', valor_por_defecto="Sin biografía")
        }
        return datos_perfil

    def raspar_videos(self):
        """Abre la vista inmersiva y navega por los videos recolectando métricas."""
        videos_extraidos = []
        
        print("\nAbriendo la cuadrícula de videos...")
        self.page.wait_for_timeout(3000)
        
        print("Intentando hacer clic en el primer video...")
        selector_video = '[data-e2e="user-post-item"], a[href*="/video/"], div[class*="ItemContainer"]'
        
        self.page.wait_for_selector(selector_video, timeout=15000)
        self.page.locator(selector_video).first.click(force=True)
        
        self.page.wait_for_timeout(4000) # Espera a que la ventana negra se abra
        
        for i in range(self.max_videos):
            print(f"Analizando video {i+1}/{self.max_videos}...")
            try:
                self.page.wait_for_selector('[data-e2e="browse-like-count"], [data-e2e="like-count"]', timeout=15000)
                
                likes = self._obtener_texto('[data-e2e="browse-like-count"], [data-e2e="like-count"]', usar_ultimo=True)
                comentarios = self._obtener_texto('[data-e2e="browse-comment-count"], [data-e2e="comment-count"]', usar_ultimo=True)
                guardados = self._obtener_texto('strong[data-e2e="collect-count"], [data-e2e="undefined-count"]', usar_ultimo=True)
                compartidos = self._obtener_texto('[data-e2e="share-count"], [data-e2e="browse-share-count"]', usar_ultimo=True)
                
                descripcion = self._obtener_texto('[data-e2e="browse-video-desc"]', usar_ultimo=True, valor_por_defecto="Sin descripción")
                descripcion_limpia = descripcion.replace('\n', ' ')
                
                hashtags = [palabra for palabra in descripcion_limpia.split() if palabra.startswith("#")]
                
                videos_extraidos.append({
                    "video_num": i + 1,
                    "me_gusta": likes,
                    "comentarios": comentarios,
                    "guardados": guardados,
                    "compartidos": compartidos,
                    "descripcion": descripcion_limpia,
                    "hashtags": ", ".join(hashtags) if hashtags else "Ninguno"
                })
                
                if i < self.max_videos - 1:
                    # --- NUEVO MECANISMO ANTI-BLOQUEOS ---
                    # 1. Presionamos Escape para cerrar popups molestos
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(500)
                    
                    # 2. Hacemos un clic en una zona muerta arriba a la izquierda para recuperar el foco del teclado
                    self.page.mouse.click(10, 10) 
                    self.page.wait_for_timeout(500)
                    
                    # 3. Ahora sí, deslizamos
                    self.page.keyboard.press("ArrowDown")
                    self.page.wait_for_timeout(3000)
                    
            except Exception as e:
                print(f"Interrupción en el video {i+1}: {e}")
                break
                
        return videos_extraidos
    
# ==========================================
# BLOQUE PRINCIPAL DE EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    # 1. Instanciamos el objeto de nuestra clase
    scraper = ScraperTikTok(usuario="samsole_1", max_videos=10)
    
    try:
        # 2. Ejecutamos los métodos paso a paso
        scraper.iniciar()
        
        info_perfil = scraper.raspar_perfil()
        info_videos = scraper.raspar_videos()
        
        # 3. Presentamos los datos estructurados
        print("\n" + "="*40)
        print("REPORTE DE PERFIL")
        print("="*40)
        for clave, valor in info_perfil.items():
            print(f"{clave.capitalize()}: {valor}")
            
        print("\n" + "="*40)
        print("REPORTE DE VIDEOS")
        print("="*40)
        for vid in info_videos:
            print(f"\n[ Video {vid['video_num']} ]")
            print(f"Me gusta: {vid['me_gusta']} | Comentarios: {vid['comentarios']} | Compartidos: {vid['compartidos']} | Guardados: {vid['guardados']}")
            print(f"Hashtags: {vid['hashtags']}")
            print(f"Descripción: {vid['descripcion']}")
            
    except Exception as error_general:
        print(f"\nSe produjo un error durante la ejecución: {error_general}")
        
    finally:
        # Esto garantiza que el navegador siempre se cierre, incluso si el código falla a la mitad
        scraper.cerrar()



        