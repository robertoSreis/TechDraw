"""
===============================================================================
STL2TechnicalDrawing - Gerenciador de Configurações CORRIGIDO
===============================================================================
Pasta: utils/
Arquivo: utils/config_manager.py
Descrição: Gerencia configurações com salvamento automático e fallback
===============================================================================
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Gerencia configurações da aplicação com salvamento automático"""
    
    def __init__(self, config_file: Optional[str] = None):
        # ✅ DIRETÓRIO DE CONFIGURAÇÃO DO USUÁRIO (não raiz do projeto)
        if config_file is None:
            # Usa diretório de configuração do usuário
            config_dir = self._get_user_config_dir()
            config_file = os.path.join(config_dir, 'stl2technicaldrawing_config.json')
        
        self.config_file = config_file
        self.config = self._load_config()
        
        # Configurações padrão
        self._set_defaults()
    
    def _get_user_config_dir(self) -> str:
        """Retorna diretório de configuração do usuário"""
        # Windows: C:\Users\Usuario\AppData\Local\STL2TechnicalDrawing
        # Linux/Mac: ~/.config/stl2technicaldrawing
        if os.name == 'nt':  # Windows
            appdata = os.getenv('LOCALAPPDATA')
            if appdata:
                config_dir = os.path.join(appdata, 'STL2TechnicalDrawing')
            else:
                config_dir = os.path.join(str(Path.home()), '.stl2technicaldrawing')
        else:  # Linux/Mac
            config_dir = os.path.join(str(Path.home()), '.config', 'stl2technicaldrawing')
        
        # Cria diretório se não existir
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ Configurações carregadas de: {self.config_file}")
                return config
            else:
                print(f"⚠️ Arquivo de configuração não encontrado. Criando novo.")
                return {}
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            return {}
    
    def _set_defaults(self):
        """Define valores padrão para configurações ausentes"""
        defaults = {
            'language': 'EN-US',
            'last_directory': '',
            'view_settings': {
                'show_faces': True,
                'show_edges': True,
                'show_grid': True,
                'mirror_x': False,
                'mirror_y': False,
                'mirror_z': False 
            },
            'model_color': [0.2, 0.6, 0.9, 1.0],  # RGBA
            'window': {
                'maximized': True,
                'width': 1200,
                'height': 800
            }
        }
        
        # Aplica defaults apenas para chaves ausentes
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Para dicionários aninhados, mescla
                for subkey, subvalue in value.items():
                    if subkey not in self.config[key]:
                        self.config[key][subkey] = subvalue
    
    def save(self):
        """✅ SALVA CONFIGURAÇÕES NO ARQUIVO IMEDIATAMENTE"""
        try:
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # ✅ CONVERTE PATH PARA STRING SIMPLES
            if 'last_directory' in self.config:
                self.config['last_directory'] = str(self.config['last_directory'])
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Configurações salvas em: {self.config_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar configurações: {e}")
            import traceback
            traceback.print_exc()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Define um valor de configuração e SALVA"""
        keys = key.split('.')
        config = self.config
        
        # Navega até o dicionário pai
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Define o valor
        config[keys[-1]] = value
        
        # ✅ SALVA IMEDIATAMENTE
        self.save()
    
    # ========== MÉTODOS ESPECÍFICOS ==========
    
    def get_language(self) -> str:
        """Retorna o idioma configurado"""
        return self.get('language', 'EN-US')
    
    def set_language(self, lang_code: str):
        """Define o idioma"""
        self.set('language', lang_code)
    
    def get_last_directory(self) -> str:
        """Retorna o último diretório usado"""
        directory = self.get('last_directory', '')
        # ✅ VERIFICA SE O DIRETÓRIO AINDA EXISTE
        if directory and os.path.isdir(directory):
            return directory
        return ''
    
    def set_last_directory(self, directory: str):
        """✅ DEFINE O ÚLTIMO DIRETÓRIO E SALVA IMEDIATAMENTE"""
        if directory and os.path.isdir(directory):
            # ✅ CONVERTE PARA STRING ABSOLUTA
            directory = os.path.abspath(directory)
            self.set('last_directory', directory)
            print(f"✅ Diretório salvo: {directory}")
    
    def get_view_settings(self) -> Dict[str, Any]:
        """Retorna configurações de visualização"""
        return self.get('view_settings', {})
    
    def set_view_setting(self, key: str, value: Any):
        """Define uma configuração de visualização"""
        settings = self.get_view_settings()
        settings[key] = value
        self.set('view_settings', settings)
    
    def get_model_color(self) -> tuple:
        """Retorna a cor do modelo como tuple RGBA"""
        color = self.get('model_color', [0.2, 0.6, 0.9, 1.0])
        return tuple(color)
    
    def set_model_color(self, r: float, g: float, b: float, a: float = 1.0):
        """Define a cor do modelo"""
        self.set('model_color', [r, g, b, a])
    
    def get_window_state(self) -> Dict[str, Any]:
        """Retorna estado da janela"""
        return self.get('window', {})
    
    def set_window_state(self, maximized: bool, width: int, height: int):
        """Define estado da janela"""
        self.set('window', {
            'maximized': maximized,
            'width': width,
            'height': height
        })
