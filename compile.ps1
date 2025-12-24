# compile.ps1 - Script para compilar STL2TechnicalDrawing com Nuitka

param(
    [switch]$Clean = $false,
    [switch]$Onefile = $false,
    [switch]$Standalone = $true
)

# Configurações
$APP_NAME = "TechDraw"
$MAIN_FILE = "main.py"
$VERSION = "1.3.35"
$COMPANY = "SE3D"
$PRODUCT = "SE3D-Technical Drawing"

# Diretórios - ESTRUTURA FIXA
$CURRENT_DIR = Get-Location
$DIST_DIR = Join-Path $CURRENT_DIR "dist"
$BUILD_DIR = Join-Path $CURRENT_DIR "build"
$FINAL_DIR = Join-Path $DIST_DIR $APP_NAME  # Pasta final onde ficará tudo

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " STL2TechnicalDrawing - Compilador Nuitka" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Limpar builds anteriores SOMENTE se solicitado
if ($Clean) {
    Write-Host "Limpando builds anteriores..." -ForegroundColor Yellow
    if (Test-Path $BUILD_DIR) { Remove-Item $BUILD_DIR -Recurse -Force }
    if (Test-Path $DIST_DIR) { Remove-Item $DIST_DIR -Recurse -Force }
    Write-Host "Limpeza concluída!" -ForegroundColor Green
    Write-Host ""
}

# Verificar se Nuitka está instalado
Write-Host "Verificando Nuitka..." -ForegroundColor Yellow
try {
    $null = Get-Command nuitka -ErrorAction Stop
    Write-Host "Nuitka encontrado!" -ForegroundColor Green
} catch {
    Write-Host "Nuitka não encontrado. Instalando..." -ForegroundColor Yellow
    pip install nuitka
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Falha ao instalar Nuitka!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Configuração da Compilação" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Aplicação: $APP_NAME" -ForegroundColor White
Write-Host "Versão: $VERSION" -ForegroundColor White
Write-Host "Modo: $(if ($Onefile) { 'Onefile (executável único)' } else { 'Standalone (pasta)' })" -ForegroundColor White
Write-Host ""

# Opções base do Nuitka - REMOVIDO --remove-output
$NUITKA_OPTIONS = @(
    "--standalone",
    "--follow-imports",
    "--enable-plugin=pyqt6",
    "--include-qt-plugins=qml",
    "--output-dir=$BUILD_DIR",  # Compila na pasta build
    "--assume-yes-for-downloads",
    "--windows-console-mode=disable"
)

# Adicionar onefile se necessário
if ($Onefile) {
    $NUITKA_OPTIONS += "--onefile"
    Write-Host "Modo: ONEFILE (arquivo único)" -ForegroundColor Yellow
} else {
    Write-Host "Modo: STANDALONE (pasta com dependências)" -ForegroundColor Yellow
}

# Adicionar informações do Windows
if (Test-Path "icon.ico") {
    $NUITKA_OPTIONS += "--windows-icon-from-ico=icon.ico"
    Write-Host "Ícone: icon.ico" -ForegroundColor Green
}

# Informações do produto
$NUITKA_OPTIONS += @(
    "--windows-company-name=$COMPANY",
    "--windows-product-name=$PRODUCT",
    "--windows-file-version=$VERSION",
    "--windows-product-version=$VERSION",
    "--windows-file-description=$APP_NAME"
)

# Incluir diretórios de dados
$NUITKA_OPTIONS += @(
    "--include-data-dir=gui=gui",
    "--include-data-dir=lang=lang",
    "--include-data-dir=samples=samples",
    "--include-package-data=PyQt6"
)

# Opções de otimização
$NUITKA_OPTIONS += @(
    "--msvc=latest",
    "--disable-ccache",
    "--jobs=4"
)

# Comando final
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Iniciando Compilação" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$COMMAND_ARGS = @($MAIN_FILE) + $NUITKA_OPTIONS

Write-Host "Executando: nuitka $($COMMAND_ARGS -join ' ')" -ForegroundColor Gray
Write-Host ""

# Criar diretórios se não existirem
if (-not (Test-Path $BUILD_DIR)) { New-Item -ItemType Directory -Path $BUILD_DIR | Out-Null }
if (-not (Test-Path $DIST_DIR)) { New-Item -ItemType Directory -Path $DIST_DIR | Out-Null }

# Executar Nuitka
& nuitka @COMMAND_ARGS

# Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host " Compilação CONCLUÍDA com SUCESSO!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    
    # Encontrar o resultado da compilação
    $COMPILED_DIR = $null
    $EXE_PATH = $null
    
    # Procurar no build
    if ($Onefile) {
        # Modo onefile - procura .exe no build
        $exeFiles = Get-ChildItem -Path $BUILD_DIR -Filter "*.exe" -Recurse -ErrorAction SilentlyContinue
        if ($exeFiles) {
            $EXE_PATH = $exeFiles[0].FullName
            $COMPILED_DIR = Split-Path $EXE_PATH -Parent
        }
    } else {
        # Modo standalone - procura pasta .dist
        $distDirs = Get-ChildItem -Path $BUILD_DIR -Directory -Filter "*.dist" -ErrorAction SilentlyContinue
        if ($distDirs) {
            $COMPILED_DIR = $distDirs[0].FullName
            $EXE_PATH = Join-Path $COMPILED_DIR "$APP_NAME.exe"
            
            # Se não encontrar com nome específico, procura qualquer .exe
            if (-not (Test-Path $EXE_PATH)) {
                $exeFiles = Get-ChildItem -Path $COMPILED_DIR -Filter "*.exe" -ErrorAction SilentlyContinue
                if ($exeFiles) {
                    $EXE_PATH = $exeFiles[0].FullName
                    $APP_NAME = [System.IO.Path]::GetFileNameWithoutExtension($exeFiles[0].Name)
                }
            }
        }
    }
    
    if ($EXE_PATH -and (Test-Path $EXE_PATH)) {
        # Preparar pasta final
        Write-Host "Preparando distribuição final..." -ForegroundColor Yellow
        
        if ($Onefile) {
            # Modo onefile - copia apenas o executável
            $finalExe = Join-Path $FINAL_DIR "$APP_NAME.exe"
            if (-not (Test-Path $FINAL_DIR)) { New-Item -ItemType Directory -Path $FINAL_DIR | Out-Null }
            Copy-Item -Path $EXE_PATH -Destination $finalExe -Force
            $EXE_PATH = $finalExe
        } else {
            # Modo standalone - copia toda a pasta
            if (Test-Path $FINAL_DIR) { Remove-Item $FINAL_DIR -Recurse -Force }
            Copy-Item -Path $COMPILED_DIR -Destination $FINAL_DIR -Recurse -Force
            $EXE_PATH = Join-Path $FINAL_DIR "$APP_NAME.exe"
        }
        
        Write-Host "Distribuição pronta em:" -ForegroundColor Cyan
        Write-Host "  $FINAL_DIR" -ForegroundColor White
        Write-Host ""
        
        if ($Onefile) {
            Write-Host "Executável:" -ForegroundColor Cyan
            Write-Host "  $EXE_PATH" -ForegroundColor White
            Write-Host ""
            Write-Host "Tamanho: $([math]::Round((Get-Item $EXE_PATH).Length / 1MB, 2)) MB" -ForegroundColor Yellow
        } else {
            Write-Host "Estrutura da pasta:" -ForegroundColor Cyan
            Get-ChildItem -Path $FINAL_DIR | ForEach-Object {
                if ($_.PSIsContainer) {
                    Write-Host "  [DIR]  $($_.Name)" -ForegroundColor Blue
                } else {
                    $size = if ($_.Length -gt 0) { "$([math]::Round($_.Length / 1KB, 2)) KB" } else { "0 KB" }
                    Write-Host "  [FILE] $($_.Name) ($size)" -ForegroundColor Gray
                }
            }
        }
        
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host " PRONTO PARA USO!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Execute o programa:" -ForegroundColor Yellow
        Write-Host "  $EXE_PATH" -ForegroundColor White
        Write-Host ""
        
        # Abrir explorer na pasta final
        Write-Host "Abrindo pasta no Explorer..." -ForegroundColor Cyan
        Start-Process "explorer.exe" -ArgumentList $FINAL_DIR
        
    } else {
        Write-Host "ERRO: Não foi possível encontrar o resultado da compilação!" -ForegroundColor Red
        Write-Host "Verifique a pasta: $BUILD_DIR" -ForegroundColor Yellow
    }
    
} else {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host " ERRO na Compilação!" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Código de saída: $LASTEXITCODE" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique os erros acima e tente novamente." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")