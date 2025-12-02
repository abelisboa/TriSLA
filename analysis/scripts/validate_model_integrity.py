#!/usr/bin/env python3
"""
FASE N.1 - Verificar integridade do modelo ML-NSMF v3.7.0
Valida:
- Carregamento de viability_model.pkl
- Carregamento de scaler.pkl
- Validação JSON model_metadata.json
- Validação lista oficial das 13 features
- Validação ordem das features
- Validação feature importance
"""

import os
import sys
import json
import pickle
import numpy as np
from pathlib import Path

# Caminhos relativos ao TriSLA-clean
BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / "apps" / "ml_nsmf" / "models"

# Lista oficial das 13 features (ordem esperada)
OFFICIAL_FEATURES = [
    "latency",
    "throughput",
    "reliability",
    "jitter",
    "packet_loss",
    "cpu_utilization",
    "memory_utilization",
    "network_bandwidth_available",
    "active_slices_count",
    "slice_type_encoded",
    "latency_throughput_ratio",
    "reliability_packet_loss_ratio",
    "jitter_latency_ratio"
]


def validate_model_integrity():
    """Valida integridade completa do modelo"""
    print("=" * 80)
    print("FASE N.1 - VERIFICAÇÃO DE INTEGRIDADE DO MODELO ML-NSMF v3.7.0")
    print("=" * 80)
    print()
    
    errors = []
    warnings = []
    
    # 1. Verificar existência dos arquivos
    print("1. Verificando existência dos arquivos...")
    model_path = MODELS_DIR / "viability_model.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    metadata_path = MODELS_DIR / "model_metadata.json"
    
    if not model_path.exists():
        errors.append(f"Modelo não encontrado: {model_path}")
    else:
        print(f"   ✓ viability_model.pkl encontrado")
    
    if not scaler_path.exists():
        errors.append(f"Scaler não encontrado: {scaler_path}")
    else:
        print(f"   ✓ scaler.pkl encontrado")
    
    if not metadata_path.exists():
        errors.append(f"Metadados não encontrados: {metadata_path}")
    else:
        print(f"   ✓ model_metadata.json encontrado")
    
    print()
    
    # 2. Carregar e validar modelo
    print("2. Carregando viability_model.pkl...")
    model = None
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        print(f"   ✓ Modelo carregado com sucesso")
        print(f"   - Tipo: {type(model).__name__}")
        
        # Verificar se é RandomForestRegressor
        if hasattr(model, 'feature_importances_'):
            n_features = len(model.feature_importances_)
            print(f"   - Número de features: {n_features}")
            if n_features != 13:
                errors.append(f"Modelo espera {n_features} features, mas deveria ter 13")
        else:
            warnings.append("Modelo não possui atributo feature_importances_")
    except Exception as e:
        errors.append(f"Erro ao carregar modelo: {e}")
    
    print()
    
    # 3. Carregar e validar scaler
    print("3. Carregando scaler.pkl...")
    scaler = None
    try:
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        print(f"   ✓ Scaler carregado com sucesso")
        print(f"   - Tipo: {type(scaler).__name__}")
        
        # Verificar número de features do scaler
        if hasattr(scaler, 'n_features_in_'):
            n_features_scaler = scaler.n_features_in_
            print(f"   - Número de features: {n_features_scaler}")
            if n_features_scaler != 13:
                errors.append(f"Scaler espera {n_features_scaler} features, mas deveria ter 13")
        elif hasattr(scaler, 'mean_'):
            n_features_scaler = len(scaler.mean_)
            print(f"   - Número de features (via mean_): {n_features_scaler}")
            if n_features_scaler != 13:
                errors.append(f"Scaler espera {n_features_scaler} features, mas deveria ter 13")
    except Exception as e:
        errors.append(f"Erro ao carregar scaler: {e}")
    
    print()
    
    # 4. Validar JSON model_metadata.json
    print("4. Validando model_metadata.json...")
    metadata = None
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        print(f"   ✓ JSON válido")
        
        # Verificar estrutura básica
        required_keys = ["model_type", "feature_columns", "training_history", "model_path", "scaler_path"]
        for key in required_keys:
            if key not in metadata:
                errors.append(f"Chave obrigatória ausente em metadata: {key}")
            else:
                print(f"   ✓ Chave '{key}' presente")
        
        # Verificar feature_columns
        if "feature_columns" in metadata:
            feature_columns = metadata["feature_columns"]
            print(f"   - Features no metadata: {len(feature_columns)}")
            
            # Validar lista oficial das 13 features
            if len(feature_columns) != 13:
                errors.append(f"Metadata contém {len(feature_columns)} features, mas deveria ter 13")
            else:
                print(f"   ✓ Número correto de features (13)")
            
            # Validar ordem das features
            if feature_columns != OFFICIAL_FEATURES:
                errors.append("Ordem das features no metadata não corresponde à ordem oficial")
                print(f"   ✗ Ordem das features incorreta")
                print(f"   - Esperado: {OFFICIAL_FEATURES}")
                print(f"   - Encontrado: {feature_columns}")
            else:
                print(f"   ✓ Ordem das features correta")
            
            # Verificar se todas as features oficiais estão presentes
            missing_features = set(OFFICIAL_FEATURES) - set(feature_columns)
            if missing_features:
                errors.append(f"Features ausentes no metadata: {missing_features}")
            else:
                print(f"   ✓ Todas as 13 features oficiais presentes")
        
        # Validar feature importance
        if "training_history" in metadata:
            training_history = metadata["training_history"]
            if "feature_importance" in training_history:
                feature_importance = training_history["feature_importance"]
                print(f"   ✓ Feature importance presente no metadata")
                
                # Verificar se todas as features têm importância
                if len(feature_importance) != 13:
                    warnings.append(f"Feature importance contém {len(feature_importance)} features, esperado 13")
                else:
                    print(f"   ✓ Feature importance completo (13 features)")
                
                # Verificar se soma das importâncias é próxima de 1.0
                total_importance = sum(feature_importance.values())
                if abs(total_importance - 1.0) > 0.01:
                    warnings.append(f"Soma das importâncias é {total_importance:.4f}, esperado ~1.0")
                else:
                    print(f"   ✓ Soma das importâncias válida ({total_importance:.4f})")
                
                # Mostrar top 5 features
                sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
                print(f"   - Top 5 features por importância:")
                for i, (feature, importance) in enumerate(sorted_features[:5], 1):
                    print(f"     {i}. {feature}: {importance:.4f}")
            else:
                warnings.append("Feature importance não encontrado em training_history")
        
    except json.JSONDecodeError as e:
        errors.append(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        errors.append(f"Erro ao validar metadata: {e}")
    
    print()
    
    # 5. Validar consistência entre modelo e metadata
    print("5. Validando consistência entre modelo e metadata...")
    if model and metadata:
        if "feature_columns" in metadata:
            metadata_features = metadata["feature_columns"]
            
            if hasattr(model, 'feature_importances_'):
                model_n_features = len(model.feature_importances_)
                if model_n_features != len(metadata_features):
                    errors.append(
                        f"Inconsistência: modelo tem {model_n_features} features, "
                        f"metadata tem {len(metadata_features)}"
                    )
                else:
                    print(f"   ✓ Número de features consistente entre modelo e metadata")
        
        if scaler and metadata:
            if hasattr(scaler, 'n_features_in_'):
                scaler_n_features = scaler.n_features_in_
                if "feature_columns" in metadata:
                    metadata_n_features = len(metadata["feature_columns"])
                    if scaler_n_features != metadata_n_features:
                        errors.append(
                            f"Inconsistência: scaler tem {scaler_n_features} features, "
                            f"metadata tem {metadata_n_features}"
                        )
                    else:
                        print(f"   ✓ Número de features consistente entre scaler e metadata")
    
    print()
    
    # 6. Teste de predição básica
    print("6. Testando predição básica...")
    if model and scaler and metadata:
        try:
            # Criar array de teste com 13 features
            test_features = np.array([[1.0] * 13])
            
            # Normalizar
            test_scaled = scaler.transform(test_features)
            
            # Predição
            prediction = model.predict(test_scaled)
            
            # Validar que predição está no range [0, 1]
            if prediction[0] < 0 or prediction[0] > 1:
                warnings.append(f"Predição fora do range [0,1]: {prediction[0]}")
            else:
                print(f"   ✓ Predição bem-sucedida: {prediction[0]:.4f}")
                print(f"   ✓ Predição no range válido [0, 1]")
        except Exception as e:
            errors.append(f"Erro ao testar predição: {e}")
    
    print()
    print("=" * 80)
    
    # Resumo final
    print("RESUMO DA VALIDAÇÃO:")
    print("=" * 80)
    
    if errors:
        print(f"❌ ERROS ENCONTRADOS: {len(errors)}")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    else:
        print("✓ Nenhum erro encontrado")
    
    if warnings:
        print(f"\n⚠️  AVISOS: {len(warnings)}")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    else:
        print("\n✓ Nenhum aviso")
    
    print()
    
    # Status final
    if errors:
        status = "ERROR"
    elif warnings:
        status = "WARNING"
    else:
        status = "OK"
    
    print(f"[FASE N.1] Status: {status}")
    print()
    
    return status, errors, warnings


if __name__ == "__main__":
    status, errors, warnings = validate_model_integrity()
    sys.exit(0 if status == "OK" else 1)

