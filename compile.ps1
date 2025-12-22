# compile.ps1 - Script para compilar STL2TechnicalDrawing com Nuitka

param(
    [switch]$Clean = $false,
    [switch]$Onefile = $false,
    [switch]$Standalone = $true
)

# Configurações
$APP_NAME = "TechDraw"
$MAIN_FILE = "main.py"
$VERSION = "1.2.35"
$COMPANY = "SE3D"
$PRODUCT = "SE3D-Technical Drawing"

# Diretórios
$CURRENT_DIR = Get-Location
$DIST_DIR = Join-Path $CURRENT_DIR "dist"
$BUILD_DIR = Join-Path $CURRENT_DIR "build"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " STL2TechnicalDrawing - Compilador Nuitka" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Limpar builds anteriores
if ($Clean -or (Test-Path $BUILD_DIR) -or (Test-Path $DIST_DIR)) {
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

# Opções base do Nuitka
$NUITKA_OPTIONS = @(
    "--standalone",
    "--remove-output",
    "--follow-imports",
    "--enable-plugin=pyqt6",
    "--include-qt-plugins=qml",
    "--output-dir=$DIST_DIR",
    "--assume-yes-for-downloads"
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
    "--windows-file-description=$APP_NAME",
    "--windows-console-mode=disable"
)

# Incluir diretórios de dados
$NUITKA_OPTIONS += @(
    "--include-data-dir=gui=gui",
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

# Executar Nuitka
& nuitka @COMMAND_ARGS

# Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host " Compilação CONCLUÍDA com SUCESSO!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    
    # Determinar caminho do executável
    if ($Onefile) {
        # Modo onefile
        $EXE_PATH = Join-Path $DIST_DIR "$APP_NAME.exe"
        if (-not (Test-Path $EXE_PATH)) {
            $foundExe = Get-ChildItem -Path $DIST_DIR -Filter "*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($foundExe) {
                $EXE_PATH = $foundExe.FullName
            }
        }
        
        if (Test-Path $EXE_PATH) {
            Write-Host "Executável criado:" -ForegroundColor Cyan
            Write-Host "  $EXE_PATH" -ForegroundColor White
            Write-Host ""
            Write-Host "Tamanho: $([math]::Round((Get-Item $EXE_PATH).Length / 1MB, 2)) MB" -ForegroundColor Yellow
        }
    } else {
        # Modo standalone
        $DIST_SUBDIR = Join-Path $DIST_DIR "$APP_NAME.dist"
        $EXE_PATH = Join-Path $DIST_SUBDIR "$APP_NAME.exe"
        
        if (-not (Test-Path $EXE_PATH)) {
            $distDirs = Get-ChildItem -Path $DIST_DIR -Directory -Filter "*.dist" -ErrorAction SilentlyContinue
            if ($distDirs) {
                foreach ($dir in $distDirs) {
                    $potentialExe = Join-Path $dir.FullName "$APP_NAME.exe"
                    if (Test-Path $potentialExe) {
                        $EXE_PATH = $potentialExe
                        break
                    }
                }
            }
        }
        
        if (Test-Path $EXE_PATH) {
            $outputDir = Split-Path $EXE_PATH -Parent
            
            Write-Host "Diretório de saída:" -ForegroundColor Cyan
            Write-Host "  $outputDir" -ForegroundColor White
            Write-Host ""
            Write-Host "Executável:" -ForegroundColor Cyan
            Write-Host "  $EXE_PATH" -ForegroundColor White
            Write-Host ""
            Write-Host "Tamanho: $([math]::Round((Get-Item $EXE_PATH).Length / 1MB, 2)) MB" -ForegroundColor Yellow
            Write-Host ""
            
            Write-Host "Estrutura:" -ForegroundColor Cyan
            Get-ChildItem -Path $outputDir | Select-Object -First 10 | ForEach-Object {
                if ($_.PSIsContainer) {
                    Write-Host "  [DIR]  $($_.Name)" -ForegroundColor Blue
                } else {
                    $size = [math]::Round($_.Length / 1KB, 2)
                    Write-Host "  [FILE] $($_.Name) ($size KB)" -ForegroundColor Gray
                }
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

Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
