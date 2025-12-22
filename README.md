<div align="center">

# 🔧 STL2TechnicalDrawing

### Gerador Automático de Desenhos Técnicos a partir de Arquivos STL

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-Private-red?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)](https://github.com/seu-usuario/STL2TechnicalDrawing)

[English](#english) | [Português](#português)

![Screenshot](docs/screenshot.png)

</div>

---

<a name="português"></a>

## 🇧🇷 Português

### 📖 Sobre o Projeto

**STL2TechnicalDrawing** é uma aplicação desktop poderosa e intuitiva que converte automaticamente modelos 3D em arquivos STL para desenhos técnicos profissionais com projeções ortográficas, dimensionamento automático e exportação em alta resolução.

#### ✨ Principais Funcionalidades

- 🎯 **Visualização 3D Interativa**: Navegação completa com rotação, zoom e pan
- 📐 **7 Vistas Predefinidas**: Frontal, traseira, superior, inferior, laterais e isométrica
- 🔄 **Geração Automática de Desenhos**: Projeções ortográficas profissionais
- 📏 **Dimensionamento Inteligente**: Cotas automáticas com detecção de features
- ⚡ **Otimização de Malha**: Redução inteligente de até 83% das arestas
- 💾 **Exportação em Alta Resolução**: PNG/JPG até 300 DPI (formato A4)
- 🎨 **Interface Moderna**: Tema escuro e design intuitivo
- 🖱️ **Drag & Drop**: Arraste arquivos STL diretamente

---

### 🚀 Instalação Rápida

#### Pré-requisitos

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes Python)
- **Git** (opcional, para clonar o repositório)

#### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/STL2TechnicalDrawing.git
cd STL2TechnicalDrawing
```

#### Passo 2: Criar Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

#### Passo 4: Executar a Aplicação
```bash
python main.py
```

---

### 🎮 Como Usar

#### 1️⃣ Carregar Modelo STL

- **Método 1**: Menu **Arquivo → Abrir STL**
- **Método 2**: Drag & Drop do arquivo na janela
- **Método 3**: Via linha de comando:
```bash
  python main.py caminho/para/arquivo.stl
```

#### 2️⃣ Visualizar em 3D

| Ação | Controle |
|------|----------|
| **Rotacionar** | Botão esquerdo + arrastar |
| **Pan (mover)** | Botão do meio + arrastar |
| **Zoom** | Scroll do mouse |
| **Zoom alternativo** | Botão direito + arrastar |

#### 3️⃣ Atalhos de Teclado

| Tecla | Função |
|-------|--------|
| `1` | Vista Frontal |
| `2` | Vista Traseira |
| `3` | Vista Superior |
| `4` | Vista Inferior |
| `5` | Vista Esquerda |
| `6` | Vista Direita |
| `7` | Vista Isométrica |
| `R` | Resetar Vista |
| `W` | Toggle Wireframe |
| `E` | Toggle Arestas |
| `F` | Toggle Faces |
| `G` | Toggle Grid |

#### 4️⃣ Gerar Desenho Técnico

1. Clique no botão **"🔧 Gerar Desenho"**
2. Aguarde o processamento (barra de progresso)
3. Visualize o desenho técnico com todas as vistas
4. Ajuste opções de visualização (linhas ocultas, dimensões, bordas)
5. Exporte para PNG/JPG em alta resolução

---

### 🛠️ Compilação (Executável Standalone)

#### Usando Nuitka (Recomendado)

**Vantagens**: Executável rápido, otimizado e sem dependências Python.

##### Windows
```powershell
# Instalar Nuitka
pip install nuitka

# Instalar compilador MSVC (necessário)
# Baixe: https://visualstudio.microsoft.com/downloads/
# Instale: "Build Tools for Visual Studio 2022"

# Compilar
python -m nuitka ^
    --standalone ^
    --windows-console-mode=disable ^
    --plugin-enable=pyqt6 ^
    --plugin-enable=numpy ^
    --include-data-dir=gui=gui ^
    --include-data-dir=core=core ^
    --include-data-dir=utils=utils ^
    --output-dir=dist ^
    --windows-icon-from-ico=icon.ico ^
    main.py
```

##### Linux
```bash
# Instalar Nuitka
pip install nuitka

# Instalar compilador
sudo apt-get install build-essential

# Compilar
python -m nuitka \
    --standalone \
    --plugin-enable=pyqt6 \
    --plugin-enable=numpy \
    --include-data-dir=gui=gui \
    --include-data-dir=core=core \
    --include-data-dir=utils=utils \
    --output-dir=dist \
    main.py
```

#### Usando PyInstaller (Alternativa)
```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar
pyinstaller --onefile --windowed \
    --add-data "gui:gui" \
    --add-data "core:core" \
    --add-data "utils:utils" \
    --icon=icon.ico \
    --name STL2TechnicalDrawing \
    main.py
```

#### Script PowerShell Automatizado (Windows)

Use o script `compile.ps1` incluído:
```powershell
# Compilação padrão (pasta com dependências)
.\compile.ps1

# Compilação em arquivo único
.\compile.ps1 -Onefile

# Limpar builds anteriores
.\compile.ps1 -Clean
```

---

### 📁 Estrutura do Projeto
```
STL2TechnicalDrawing/
│
├── main.py                      # ← Arquivo principal
├── requirements.txt             # Dependências
├── compile.ps1                  # Script de compilação
├── README.md                    # Este arquivo
│
├── core/                        # Módulo CORE - Processamento
│   ├── __init__.py
│   ├── stl_loader.py           # Carregamento e simplificação
│   ├── projection_engine.py    # Projeções ortográficas
│   ├── dimension_system.py     # Sistema de dimensionamento
│   ├── feature_detector.py     # Detecção de features
│   ├── geometry_analyzer.py    # Análise geométrica
│   └── mesh_simplifier.py      # Otimização de malha
│
├── gui/                         # Módulo GUI - Interface
│   ├── __init__.py
│   ├── main_window.py          # Janela principal
│   ├── gl_widget.py            # Widget OpenGL 3D
│   ├── technical_drawing_widget.py  # Widget desenho 2D
│   ├── drawing_preview_window.py    # Preview e exportação
│   └── progress_dialog.py      # Diálogo de progresso
│
├── utils/                       # Módulo UTILS - Utilitários
│   ├── __init__.py
│   └── constants.py            # Constantes e configurações
│
├── samples/                     # Arquivos STL de exemplo
│   ├── cube.stl
│   ├── bracket.stl
│   ├── cylinder.stl
│   └── plate.stl
│
└── docs/                        # Documentação
    ├── screenshot.png
    └── technical_drawing.png
```

---

### 🔧 Dependências
```txt
PyQt6>=6.4.0              # Interface gráfica
PyOpenGL>=3.1.6           # Renderização 3D
PyOpenGL-accelerate>=3.1.6
numpy>=1.24.0             # Computação numérica
numpy-stl>=3.0.0          # Processamento STL
trimesh>=4.0.0            # Análise de malha
scipy>=1.10.0             # Cálculos científicos
Pillow>=10.0.0            # Processamento de imagens
```

---

### 🐛 Solução de Problemas

#### ❌ Erro: "cannot import name 'BACKGROUND_COLOR'"

**Causa**: Arquivos `__init__.py` ausentes.

**Solução**: Verifique se todas as pastas (`core/`, `gui/`, `utils/`) possuem `__init__.py`.

#### ❌ Erro: "No module named 'PyQt6'"

**Causa**: Dependências não instaladas.

**Solução**:
```bash
pip install -r requirements.txt
```

#### ❌ OpenGL não funciona

**Causa**: Drivers gráficos desatualizados.

**Solução**: Atualize os drivers da placa de vídeo.

#### ❌ Incompatible version of OpenGL_accelerate

**Solução**:
```bash
pip install --upgrade PyOpenGL PyOpenGL-accelerate
```

---

### 🎯 Roadmap

- [x] Visualização 3D interativa
- [x] 7 vistas ortográficas predefinidas
- [x] Projeção ortográfica automática
- [x] Dimensionamento automático
- [x] Exportação PNG/JPG em alta resolução
- [x] Otimização de malha (redução até 83%)
- [ ] Detecção automática de furos e círculos
- [ ] Exportação para DXF/DWG (AutoCAD)
- [ ] Exportação para PDF vetorial
- [ ] Templates personalizáveis
- [ ] Anotações manuais
- [ ] Detecção de chanfros e filetes
- [ ] Tabela de materiais
- [ ] Suporte a múltiplos idiomas

---

### 📝 Licença

© 2025 **SE3D | TechDraw** - Todos os direitos reservados.

Este projeto é **proprietário** e de uso **privado**. Distribuição, modificação ou uso comercial não autorizado é proibido.

---

### 👥 Créditos

**Desenvolvido por**: Roberto Reis  
**Empresa**: SE3D GESTOR  
**Versão**: 1.2.35  
**Data**: 2025

---

### 📧 Contato

- **Email**: contato@se3d.com.br
- **Website**: [www.se3d.com.br](https://www.se3d.com.br)
- **GitHub**: [github.com/se3d](https://github.com/se3d)

---

### 🙏 Agradecimentos

Obrigado por usar o **STL2TechnicalDrawing**! 

Se você encontrar bugs ou tiver sugestões, por favor abra uma issue no GitHub.

</div>

---
---

<a name="english"></a>

## 🇺🇸 English

### 📖 About the Project

**STL2TechnicalDrawing** is a powerful and intuitive desktop application that automatically converts 3D models in STL files into professional technical drawings with orthographic projections, automatic dimensioning, and high-resolution export.

#### ✨ Key Features

- 🎯 **Interactive 3D Visualization**: Full navigation with rotation, zoom, and pan
- 📐 **7 Predefined Views**: Front, back, top, bottom, left, right, and isometric
- 🔄 **Automatic Drawing Generation**: Professional orthographic projections
- 📏 **Smart Dimensioning**: Automatic dimensions with feature detection
- ⚡ **Mesh Optimization**: Intelligent reduction up to 83% of edges
- 💾 **High-Resolution Export**: PNG/JPG up to 300 DPI (A4 format)
- 🎨 **Modern Interface**: Dark theme and intuitive design
- 🖱️ **Drag & Drop**: Drop STL files directly

---

### 🚀 Quick Installation

#### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (Python package manager)
- **Git** (optional, to clone the repository)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/STL2TechnicalDrawing.git
cd STL2TechnicalDrawing
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Application
```bash
python main.py
```

---

### 🎮 How to Use

#### 1️⃣ Load STL Model

- **Method 1**: Menu **File → Open STL**
- **Method 2**: Drag & Drop file into window
- **Method 3**: Via command line:
```bash
  python main.py path/to/file.stl
```

#### 2️⃣ View in 3D

| Action | Control |
|--------|---------|
| **Rotate** | Left button + drag |
| **Pan (move)** | Middle button + drag |
| **Zoom** | Mouse scroll |
| **Alternative zoom** | Right button + drag |

#### 3️⃣ Keyboard Shortcuts

| Key | Function |
|-----|----------|
| `1` | Front View |
| `2` | Back View |
| `3` | Top View |
| `4` | Bottom View |
| `5` | Left View |
| `6` | Right View |
| `7` | Isometric View |
| `R` | Reset View |
| `W` | Toggle Wireframe |
| `E` | Toggle Edges |
| `F` | Toggle Faces |
| `G` | Toggle Grid |

#### 4️⃣ Generate Technical Drawing

1. Click **"🔧 Generate Drawing"** button
2. Wait for processing (progress bar)
3. View technical drawing with all views
4. Adjust display options (hidden lines, dimensions, borders)
5. Export to PNG/JPG in high resolution

---

### 🛠️ Compilation (Standalone Executable)

#### Using Nuitka (Recommended)

**Advantages**: Fast, optimized executable without Python dependencies.

##### Windows
```powershell
# Install Nuitka
pip install nuitka

# Install MSVC compiler (required)
# Download: https://visualstudio.microsoft.com/downloads/
# Install: "Build Tools for Visual Studio 2022"

# Compile
python -m nuitka ^
    --standalone ^
    --windows-console-mode=disable ^
    --plugin-enable=pyqt6 ^
    --plugin-enable=numpy ^
    --include-data-dir=gui=gui ^
    --include-data-dir=core=core ^
    --include-data-dir=utils=utils ^
    --output-dir=dist ^
    --windows-icon-from-ico=icon.ico ^
    main.py
```

##### Linux
```bash
# Install Nuitka
pip install nuitka

# Install compiler
sudo apt-get install build-essential

# Compile
python -m nuitka \
    --standalone \
    --plugin-enable=pyqt6 \
    --plugin-enable=numpy \
    --include-data-dir=gui=gui \
    --include-data-dir=core=core \
    --include-data-dir=utils=utils \
    --output-dir=dist \
    main.py
```

#### Using PyInstaller (Alternative)
```bash
# Install PyInstaller
pip install pyinstaller

# Compile
pyinstaller --onefile --windowed \
    --add-data "gui:gui" \
    --add-data "core:core" \
    --add-data "utils:utils" \
    --icon=icon.ico \
    --name STL2TechnicalDrawing \
    main.py
```

---

### 🐛 Troubleshooting

#### ❌ Error: "cannot import name 'BACKGROUND_COLOR'"

**Cause**: Missing `__init__.py` files.

**Solution**: Verify that all folders (`core/`, `gui/`, `utils/`) have `__init__.py`.

#### ❌ Error: "No module named 'PyQt6'"

**Cause**: Dependencies not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

#### ❌ OpenGL not working

**Cause**: Outdated graphics drivers.

**Solution**: Update your graphics card drivers.

---

### 📝 License

© 2025 **SE3D | TechDraw** - All rights reserved.

This project is **proprietary** and for **private** use. Unauthorized distribution, modification, or commercial use is prohibited.

---

### 👥 Credits

**Developed by**: Roberto Reis  
**Company**: SE3D GESTOR  
**Version**: 1.2.35  
**Date**: 2025

---

### 📧 Contact

- **Email**: contact@se3d.com
- **Website**: [www.se3d.com](https://www.se3d.com)
- **GitHub**: [github.com/se3d](https://github.com/se3d)

---

<div align="center">

### ⭐ If this project helped you, please give it a star!

Made with ❤️ by **SE3D Team**

</div>