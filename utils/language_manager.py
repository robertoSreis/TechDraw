"""
===============================================================================
STL2TechnicalDrawing - Gerenciador de Idiomas
===============================================================================
Pasta: utils/
Arquivo: utils/language_manager.py
Descrição: Gerencia internacionalização (i18n) do aplicativo
===============================================================================
"""

import json
import os,sys
from typing import Dict, List, Optional


class LanguageManager:
    """Gerenciador de idiomas e traduções"""
    
    def __init__(self, lang_dir: str = "lang"):
        """
        Inicializa o gerenciador de idiomas.
        
        Args:
            lang_dir: Diretório contendo arquivos de idioma
        """
        self.lang_dir = lang_dir
        self.current_language = "PT-BR"
        self.translations: Dict[str, any] = {}
        self.available_languages: List[Dict[str, str]] = []
        
        # Cria diretório e arquivos se não existirem
        self._ensure_language_files()
        self._scan_languages()
    
    def _ensure_language_files(self):
        """Garante que diretório e arquivos de idioma existem"""
        # Cria diretório
        if not os.path.exists(self.lang_dir):
            os.makedirs(self.lang_dir)
            print(f"[Language] Diretório '{self.lang_dir}' criado")
        
        # Cria PT-BR se não existir
        pt_br_file = os.path.join(self.lang_dir, "PT-BR.json")
        if not os.path.exists(pt_br_file):
            self._create_pt_br_file(pt_br_file)
            print(f"[Language] Arquivo PT-BR.json criado")
        
        # Cria EN-US se não existir
        en_us_file = os.path.join(self.lang_dir, "EN-US.json")
        if not os.path.exists(en_us_file):
            self._create_en_us_file(en_us_file)
            print(f"[Language] Arquivo EN-US.json criado")
    
    def _create_pt_br_file(self, filepath: str):
        """Cria arquivo PT-BR.json com conteúdo padrão"""
        content = {
            "UIshow": "Português (Brasil)",
            "code": "PT-BR",
            
            "menu": {
                "file": "Arquivo",
                "file_open": "Abrir STL...",
                "file_export": "Exportar Imagem...",
                "file_exit": "Sair",
                "view": "Visualizar",
                "view_reset": "Resetar Vista",
                "help": "Ajuda",
                "help_about": "Sobre"
            },
            
            "toolbar": {
                "open": "Abrir",
                "clear": "Limpar",
                "mirror_x": "Espelhar X",
                "mirror_y": "Espelhar Y",
                "edges": "Arestas",
                "faces": "Faces",
                "grid": "Grid"
            },
            
            "sidebar": {
                "views_title": "⚙️ Vistas Predefinidas",
                "front": "Frontal",
                "back": "Traseira",
                "top": "Superior",
                "bottom": "Inferior",
                "left": "Esquerda",
                "right": "Direita",
                "isometric": "🔲 Vista Isométrica",
                "reset": "🔄 Resetar Vista",
                
                "actions_title": "🎯 Ações",
                "generate_drawing": "🔧 Gerar Desenho",
                "export_image": "💾 Exportar IMG",
                
                "info_title": "📊 Info do Modelo",
                "file": "Arquivo:",
                "vertices": "Vértices:",
                "faces": "Faces:",
                "edges": "Arestas:",
                "dimensions": "Dimensões:",
                "volume": "Volume:",
                "width": "L",
                "height": "A",
                "depth": "P",
                "simplified": "✓ Simplificado",
                "not_simplified": "Não simplificado",
                
                "settings_title": "⚙️ Configurações",
                "language": "Idioma:",
                "model_color": "Cor do Modelo:",
                "choose_color": "Escolher Cor",
                "reset_color": "Restaurar Padrão",
                
                "navigation_title": "🖱️ Navegação",
                "mouse_left": "• Esq: Rotacionar",
                "mouse_middle": "• Meio: Pan",
                "mouse_scroll": "• Scroll: Zoom"
            },
            
            "statusbar": {
                "ready": "Pronto. Abra um arquivo STL para começar.",
                "loading": "Carregando...",
                "generating": "Gerando desenho técnico...",
                "loaded": "✓ Carregado:",
                "vertices": "vértices",
                "edges": "arestas",
                "error": "Erro ao carregar arquivo",
                "model_removed": "Modelo removido",
                "view_changed": "Vista alterada:",
                "exported": "✓ Imagem exportada:",
                "drawing_generated": "✓ Desenho técnico gerado"
            },
            
            "dialogs": {
                "open_stl": "Abrir Arquivo STL",
                "stl_files": "Arquivos STL (*.stl)",
                "all_files": "Todos os arquivos (*)",
                "export_image": "Exportar Imagem",
                "loading_title": "Carregando",
                "loading_message": "Carregando arquivo STL...",
                "cancel": "Cancelar",
                "no_model": "Nenhum modelo carregado.",
                "warning": "Aviso",
                "error": "Erro",
                "info": "Informação",
                "about_title": "Sobre",
                "about_text": "<h3>STL to Technical Drawing</h3><p>Gerador automático de desenhos técnicos.</p><p><b>Versão:</b> 1.2.35</p><p><b>Por:</b> Roberto Reis - SE3D | 2025</p>"
            },
            
            "views": {
                "front": "FRONTAL",
                "back": "TRASEIRA",
                "top": "SUPERIOR",
                "bottom": "INFERIOR",
                "left": "ESQ.",
                "right": "DIR.",
                "isometric": "ISOMÉTRICA"
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    
    def _create_en_us_file(self, filepath: str):
        """Cria arquivo EN-US.json com conteúdo padrão"""
        content = {
            "UIshow": "English (United States)",
            "code": "EN-US",
            
            "menu": {
                "file": "File",
                "file_open": "Open STL...",
                "file_export": "Export Image...",
                "file_exit": "Exit",
                "view": "View",
                "view_reset": "Reset View",
                "help": "Help",
                "help_about": "About"
            },
            
            "toolbar": {
                "open": "Open",
                "clear": "Clear",
                "mirror_x": "Mirror X",
                "mirror_y": "Mirror Y",
                "edges": "Edges",
                "faces": "Faces",
                "grid": "Grid"
            },
            
            "sidebar": {
                "views_title": "⚙️ Predefined Views",
                "front": "Front",
                "back": "Back",
                "top": "Top",
                "bottom": "Bottom",
                "left": "Left",
                "right": "Right",
                "isometric": "🔲 Isometric View",
                "reset": "🔄 Reset View",
                
                "actions_title": "🎯 Actions",
                "generate_drawing": "🔧 Generate Drawing",
                "export_image": "💾 Export IMG",
                
                "info_title": "📊 Model Info",
                "file": "File:",
                "vertices": "Vertices:",
                "faces": "Faces:",
                "edges": "Edges:",
                "dimensions": "Dimensions:",
                "volume": "Volume:",
                "width": "W",
                "height": "H",
                "depth": "D",
                "simplified": "✓ Simplified",
                "not_simplified": "Not simplified",
                
                "settings_title": "⚙️ Settings",
                "language": "Language:",
                "model_color": "Model Color:",
                "choose_color": "Choose Color",
                "reset_color": "Reset Default",
                
                "navigation_title": "🖱️ Navigation",
                "mouse_left": "• Left: Rotate",
                "mouse_middle": "• Middle: Pan",
                "mouse_scroll": "• Scroll: Zoom"
            },
            
            "statusbar": {
                "ready": "Ready. Open an STL file to begin.",
                "loading": "Loading...",
                "generating": "Generating technical drawing...",
                "loaded": "✓ Loaded:",
                "vertices": "vertices",
                "edges": "edges",
                "error": "Error loading file",
                "model_removed": "Model removed",
                "view_changed": "View changed:",
                "exported": "✓ Image exported:",
                "drawing_generated": "✓ Technical drawing generated"
            },
            
            "dialogs": {
                "open_stl": "Open STL File",
                "stl_files": "STL Files (*.stl)",
                "all_files": "All files (*)",
                "export_image": "Export Image",
                "loading_title": "Loading",
                "loading_message": "Loading STL file...",
                "cancel": "Cancel",
                "no_model": "No model loaded.",
                "warning": "Warning",
                "error": "Error",
                "info": "Information",
                "about_title": "About",
                "about_text": "<h3>STL to Technical Drawing</h3><p>Automatic technical drawing generator.</p><p><b>Version:</b> 1.2.35</p><p><b>By:</b> Roberto Reis - SE3D | 2025</p>"
            },
            
            "views": {
                "front": "FRONT",
                "back": "BACK",
                "top": "TOP",
                "bottom": "BOTTOM",
                "left": "LEFT",
                "right": "RIGHT",
                "isometric": "ISOMETRIC"
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    
    def _scan_languages(self):
        """Escaneia diretório de idiomas"""
        self.available_languages = []
        
        if not os.path.exists(self.lang_dir):
            return
        
        for filename in os.listdir(self.lang_dir):
            if filename.endswith('.json'):
                lang_code = filename.replace('.json', '')
                lang_file = os.path.join(self.lang_dir, filename)
                
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        self.available_languages.append({
                            'code': lang_code,
                            'name': data.get('UIshow', lang_code),
                            'file': lang_file
                        })
                except Exception as e:
                    print(f"[Language] Erro ao ler '{filename}': {e}")
        
        print(f"[Language] Idiomas encontrados: {[l['code'] for l in self.available_languages]}")
    
    def load_language(self, language_code: str) -> bool:
        """
        Carrega um idioma.
        
        Args:
            language_code: Código do idioma (ex: "PT-BR")
        
        Returns:
            True se carregou com sucesso
        """
        lang_file = os.path.join(self.lang_dir, f"{language_code}.json")
        
        if not os.path.exists(lang_file):
            print(f"[Language] Arquivo não encontrado: '{lang_file}'")
            return False
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
                self.current_language = language_code
                print(f"[Language] Idioma carregado: {language_code}")
                print(f"[Language] Traduções carregadas: {len(str(self.translations))} caracteres")
                return True
        except Exception as e:
            print(f"[Language] Erro ao carregar idioma: {e}")
            return False
    
    def get(self, key: str, default: str = "") -> str:
        """
        Obtém uma tradução.
        
        Args:
            key: Chave no formato "section.key" (ex: "menu.file")
            default: Valor padrão se não existir
        
        Returns:
            Texto traduzido
        """
        if not self.translations:
            print(f"[Language] AVISO: Nenhuma tradução carregada! Retornando chave: {key}")
            return default if default else key
        
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Retorna default ou a chave se não encontrar
                return default if default else key
        
        return value if isinstance(value, str) else (default if default else key)
    
    def get_available_languages(self):
        """Retorna lista de idiomas disponíveis com múltiplas tentativas"""
        try:
            languages = []
            
            # Tenta vários locais possíveis
            possible_paths = [
                # 1. Relativo ao executável (para .exe) - para Nuitka
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lang"),
                
                # 2. Para PyInstaller/Flet-to-exe
                os.path.join(os.path.dirname(sys.executable), "lang"),
                
                # 3. Raiz do projeto (para desenvolvimento no VSCode)
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "lang"),
                
                # 4. Diretório atual de trabalho
                os.path.join(os.getcwd(), "lang"),
                
                # 5. Mesma pasta do script principal
                os.path.join(os.path.dirname(sys.argv[0]), "lang"),
                
            ]
            
            lang_dir = None
            for path in possible_paths:
                path = os.path.normpath(path)
                print(f"🔍 Tentando: {path}")
                if os.path.exists(path) and os.path.isdir(path):
                    lang_dir = path
                    print(f"✅ Encontrada pasta lang em: {lang_dir}")
                    break
            
            if not lang_dir:
                print("❌ Nenhuma pasta lang encontrada em nenhum local!")
                return []
            
            # Procura arquivos .json
            import glob
            lang_files = glob.glob(os.path.join(lang_dir, "*.json"))
            
            print(f"📚 Encontrados {len(lang_files)} arquivos de idioma")
            
            for filepath in lang_files:
                filename = os.path.basename(filepath)
                lang_code = os.path.splitext(filename)[0]
                
                try:
                    # Tenta abrir com encoding específico para BOM
                    with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig lida com BOM
                        data = json.load(f)
                    
                    lang_name = data.get('UIshow', lang_code)
                    
                    languages.append({
                        'code': lang_code,
                        'name': lang_name,
                        'file': filepath
                    })
                    
                    print(f"   ✅ {lang_code} -> {lang_name}")
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ ERRO JSON em {filename}: {e}")
                    # Mostra um trecho do arquivo com erro
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        error_pos = e.pos
                        start = max(0, error_pos - 50)
                        end = min(len(content), error_pos + 50)
                        print(f"      Contexto: ...{content[start:end]}...")
                        
                except Exception as e:
                    print(f"   ❌ Erro em {filename}: {type(e).__name__}: {e}")
            
            print(f"📊 Total carregados com sucesso: {len(languages)}")
            return languages
            
        except Exception as e:
            print(f"💥 Erro crítico em get_available_languages: {e}")
            import traceback
            traceback.print_exc()
            return []  # Retorna lista vazia em vez de chamar a si mesmo
            
    
    def get_current_language(self) -> str:
        """Retorna código do idioma atual"""
        return self.current_language
    
    def format(self, key: str, **kwargs) -> str:
        """
        Obtém tradução formatada com variáveis.
        
        Args:
            key: Chave da tradução
            **kwargs: Variáveis para substituir
        
        Returns:
            Texto formatado
        """
        text = self.get(key)
        try:
            return text.format(**kwargs)
        except KeyError:
            return text