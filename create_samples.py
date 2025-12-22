#!/usr/bin/env python3
"""
===============================================================================
STL2TechnicalDrawing - Gerador de Arquivos STL de Exemplo
===============================================================================
Arquivo: create_samples.py
Descrição: Script para gerar arquivos STL de teste
Uso: python create_samples.py
===============================================================================
"""

import numpy as np
from stl import mesh
import os


def create_cube(size=10.0):
    """Cria um cubo simples"""
    # 8 vértices do cubo
    vertices = np.array([
        [0, 0, 0],
        [size, 0, 0],
        [size, size, 0],
        [0, size, 0],
        [0, 0, size],
        [size, 0, size],
        [size, size, size],
        [0, size, size]
    ])
    
    # 12 triângulos (2 por face)
    faces = np.array([
        # Fundo
        [0, 3, 1], [1, 3, 2],
        # Topo
        [4, 5, 7], [5, 6, 7],
        # Frente
        [0, 1, 4], [1, 5, 4],
        # Traseira
        [2, 3, 6], [3, 7, 6],
        # Esquerda
        [0, 4, 3], [3, 4, 7],
        # Direita
        [1, 2, 5], [2, 6, 5]
    ])
    
    # Cria o mesh
    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[f[j], :]
    
    return cube


def create_bracket():
    """Cria um bracket em L - peça mais complexa para teste"""
    # Dimensões
    base_width = 40.0
    base_depth = 30.0
    base_height = 8.0
    
    wall_width = 8.0
    wall_height = 35.0
    
    # Vértices
    vertices = [
        # Base horizontal (8 vértices)
        [0, 0, 0],                           # 0
        [base_width, 0, 0],                  # 1
        [base_width, base_depth, 0],         # 2
        [0, base_depth, 0],                  # 3
        [0, 0, base_height],                 # 4
        [base_width, 0, base_height],        # 5
        [base_width, base_depth, base_height], # 6
        [0, base_depth, base_height],        # 7
        
        # Parede vertical (4 vértices adicionais)
        [wall_width, 0, base_height],                 # 8
        [wall_width, base_depth, base_height],        # 9
        [0, 0, base_height + wall_height],            # 10
        [wall_width, 0, base_height + wall_height],   # 11
        [wall_width, base_depth, base_height + wall_height],  # 12
        [0, base_depth, base_height + wall_height],   # 13
    ]
    
    vertices = np.array(vertices)
    
    # Faces
    faces = [
        # Base - fundo
        [0, 1, 3], [1, 2, 3],
        # Base - topo (parte sem parede)
        [5, 6, 8], [6, 9, 8],
        # Base - frente
        [0, 4, 1], [1, 4, 5],
        # Base - traseira
        [2, 3, 6], [3, 7, 6],
        # Base - direita
        [1, 5, 2], [2, 5, 6],
        # Base - esquerda (parcial, continua na parede)
        [0, 3, 4], [3, 7, 4],
        
        # Parede - topo
        [10, 11, 13], [11, 12, 13],
        # Parede - frente
        [4, 10, 8], [8, 10, 11],
        # Parede - traseira  
        [7, 13, 9], [9, 13, 12],
        # Parede - lateral interna
        [8, 11, 9], [9, 11, 12],
        # Parede - lateral externa (continuação da base)
        [4, 7, 10], [7, 13, 10],
        # Conexão base-parede topo
        [7, 9, 6], [8, 9, 5], [5, 9, 6],
    ]
    
    faces = np.array(faces)
    
    # Cria o mesh
    bracket = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            bracket.vectors[i][j] = vertices[f[j], :]
    
    return bracket


def create_cylinder(radius=10.0, height=30.0, segments=32):
    """Cria um cilindro"""
    vertices = []
    faces = []
    
    # Centro inferior e superior
    vertices.append([0, 0, 0])  # 0 - centro inferior
    vertices.append([0, 0, height])  # 1 - centro superior
    
    # Vértices do círculo inferior e superior
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        vertices.append([x, y, 0])  # inferior
        vertices.append([x, y, height])  # superior
    
    vertices = np.array(vertices)
    
    # Faces
    for i in range(segments):
        # Índices dos vértices
        curr_bottom = 2 + i * 2
        curr_top = 3 + i * 2
        next_bottom = 2 + ((i + 1) % segments) * 2
        next_top = 3 + ((i + 1) % segments) * 2
        
        # Tampa inferior
        faces.append([0, next_bottom, curr_bottom])
        
        # Tampa superior
        faces.append([1, curr_top, next_top])
        
        # Lateral
        faces.append([curr_bottom, next_bottom, curr_top])
        faces.append([curr_top, next_bottom, next_top])
    
    faces = np.array(faces)
    
    # Cria o mesh
    cylinder = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            cylinder.vectors[i][j] = vertices[f[j], :]
    
    return cylinder


def create_plate_with_holes():
    """Cria uma placa com furos - útil para testar detecção de círculos"""
    # Este é um exemplo mais complexo
    # Por enquanto, criar uma placa simples
    width = 80.0
    depth = 60.0
    height = 5.0
    
    vertices = np.array([
        [0, 0, 0],
        [width, 0, 0],
        [width, depth, 0],
        [0, depth, 0],
        [0, 0, height],
        [width, 0, height],
        [width, depth, height],
        [0, depth, height]
    ])
    
    faces = np.array([
        # Fundo
        [0, 3, 1], [1, 3, 2],
        # Topo
        [4, 5, 7], [5, 6, 7],
        # Frente
        [0, 1, 4], [1, 5, 4],
        # Traseira
        [2, 3, 6], [3, 7, 6],
        # Esquerda
        [0, 4, 3], [3, 4, 7],
        # Direita
        [1, 2, 5], [2, 6, 5]
    ])
    
    plate = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            plate.vectors[i][j] = vertices[f[j], :]
    
    return plate


if __name__ == "__main__":
    # Diretório de saída
    output_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(output_dir, "samples")
    os.makedirs(samples_dir, exist_ok=True)
    
    print("=" * 60)
    print("STL2TechnicalDrawing - Gerador de Samples")
    print("=" * 60)
    print(f"Diretório de saída: {samples_dir}")
    print("-" * 60)
    
    # Gera os arquivos
    print("Gerando arquivos STL de exemplo...")
    
    # Cubo
    cube = create_cube(20.0)
    cube.save(os.path.join(samples_dir, "cube.stl"))
    print("  ✓ cube.stl (cubo 20x20x20)")
    
    # Bracket
    bracket = create_bracket()
    bracket.save(os.path.join(samples_dir, "bracket.stl"))
    print("  ✓ bracket.stl (bracket em L)")
    
    # Cilindro
    cylinder = create_cylinder(15.0, 40.0, 64)
    cylinder.save(os.path.join(samples_dir, "cylinder.stl"))
    print("  ✓ cylinder.stl (cilindro r=15, h=40)")
    
    # Placa
    plate = create_plate_with_holes()
    plate.save(os.path.join(samples_dir, "plate.stl"))
    print("  ✓ plate.stl (placa 80x60x5)")
    
    print("-" * 60)
    print(f"✓ {4} arquivos gerados com sucesso!")
    print("=" * 60)
