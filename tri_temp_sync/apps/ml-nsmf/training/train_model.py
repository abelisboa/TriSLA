"""
Script de Treinamento do Modelo ML-NSMF
Treina modelo Random Forest para predição de viabilidade de SLA
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
import json
from datetime import datetime
import os
import sys

# Adicionar caminho do módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_dataset(path: str) -> pd.DataFrame:
    """Carrega dataset de treinamento"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset não encontrado: {path}")
    
    df = pd.read_csv(path)
    print(f"Dataset carregado: {len(df)} amostras")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cria features derivadas"""
    # Evitar divisão por zero
    epsilon = 0.001
    
    df['latency_throughput_ratio'] = df['latency'] / (df['throughput'] + epsilon)
    df['reliability_packet_loss_ratio'] = df['reliability'] / (df['packet_loss'] + epsilon)
    df['jitter_latency_ratio'] = df['jitter'] / (df['latency'] + epsilon)
    
    print("Features derivadas criadas")
    return df


def train_model(X_train, y_train):
    """Treina modelo Random Forest"""
    print("Treinando modelo Random Forest...")
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    print("Modelo treinado com sucesso!")
    return model


def evaluate_model(model, X_test, y_test):
    """Avalia modelo"""
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {
        "mse": float(mse),
        "mae": float(mae),
        "r2": float(r2)
    }


def main():
    """Função principal de treinamento"""
    print("=" * 60)
    print("TREINAMENTO DO MODELO ML-NSMF")
    print("=" * 60)
    
    # 1. Carregar dataset
    dataset_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data/datasets/trisla_ml_dataset.csv"
    )
    
    try:
        df = load_dataset(dataset_path)
    except FileNotFoundError:
        print(f"ERRO: Dataset não encontrado em {dataset_path}")
        print("Criando dataset de exemplo...")
        # Criar dataset de exemplo
        n_samples = 1000
        df = pd.DataFrame({
            'latency': np.random.uniform(1, 100, n_samples),
            'throughput': np.random.uniform(1, 1000, n_samples),
            'reliability': np.random.uniform(0.9, 1.0, n_samples),
            'jitter': np.random.uniform(0.1, 10, n_samples),
            'packet_loss': np.random.uniform(0.001, 0.1, n_samples),
            'cpu_utilization': np.random.uniform(0.3, 0.9, n_samples),
            'memory_utilization': np.random.uniform(0.3, 0.9, n_samples),
            'network_bandwidth_available': np.random.uniform(100, 1000, n_samples),
            'active_slices_count': np.random.randint(1, 20, n_samples),
            'slice_type_encoded': np.random.randint(1, 4, n_samples),
            'viability_score': np.random.uniform(0.5, 1.0, n_samples)
        })
        os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
        df.to_csv(dataset_path, index=False)
        print(f"Dataset de exemplo criado: {dataset_path}")
    
    # 2. Feature engineering
    df = engineer_features(df)
    
    # 3. Separar features e target
    feature_columns = [
        "latency", "throughput", "reliability", "jitter", "packet_loss",
        "cpu_utilization", "memory_utilization", "network_bandwidth_available",
        "active_slices_count", "slice_type_encoded",
        "latency_throughput_ratio", "reliability_packet_loss_ratio",
        "jitter_latency_ratio"
    ]
    
    # Verificar se todas as colunas existem
    missing_cols = [col for col in feature_columns if col not in df.columns]
    if missing_cols:
        print(f"AVISO: Colunas faltantes: {missing_cols}")
        feature_columns = [col for col in feature_columns if col in df.columns]
    
    if 'viability_score' not in df.columns:
        raise ValueError("Coluna 'viability_score' não encontrada no dataset")
    
    X = df[feature_columns]
    y = df['viability_score']
    
    print(f"Features: {len(feature_columns)}")
    print(f"Target: viability_score")
    
    # 4. Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Train samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # 5. Normalização
    print("Normalizando features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 6. Treinar modelo
    model = train_model(X_train_scaled, y_train)
    
    # 7. Avaliar modelo
    print("\nAvaliando modelo...")
    train_metrics = evaluate_model(model, X_train_scaled, y_train)
    test_metrics = evaluate_model(model, X_test_scaled, y_test)
    
    print(f"\nTrain Metrics:")
    print(f"  R²: {train_metrics['r2']:.4f}")
    print(f"  MAE: {train_metrics['mae']:.4f}")
    print(f"  MSE: {train_metrics['mse']:.4f}")
    
    print(f"\nTest Metrics:")
    print(f"  R²: {test_metrics['r2']:.4f}")
    print(f"  MAE: {test_metrics['mae']:.4f}")
    print(f"  MSE: {test_metrics['mse']:.4f}")
    
    # 8. Cross-validation
    print("\nExecutando cross-validation...")
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    print(f"CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # 9. Feature importance
    feature_importance = dict(zip(feature_columns, model.feature_importances_))
    print("\nTop 5 Features por Importância:")
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {feature}: {importance:.4f}")
    
    # 10. Salvar modelo
    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "models"
    )
    os.makedirs(models_dir, exist_ok=True)
    
    # Salvar modelo
    model_path = os.path.join(models_dir, "viability_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModelo salvo: {model_path}")
    
    # Salvar scaler
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"Scaler salvo: {scaler_path}")
    
    # Salvar metadados
    metadata = {
        "model_type": "random_forest",
        "feature_columns": feature_columns,
        "training_history": {
            "model_type": "random_forest",
            "train_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "train_mse": train_metrics["mse"],
            "test_mse": test_metrics["mse"],
            "train_mae": train_metrics["mae"],
            "test_mae": test_metrics["mae"],
            "train_r2": train_metrics["r2"],
            "test_r2": test_metrics["r2"],
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "feature_importance": {k: float(v) for k, v in feature_importance.items()},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "model_path": "viability_model.pkl",
        "scaler_path": "scaler.pkl"
    }
    
    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadados salvos: {metadata_path}")
    
    print("\n" + "=" * 60)
    print("TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print(f"\nTest R²: {test_metrics['r2']:.4f}")
    print(f"Test MAE: {test_metrics['mae']:.4f}")
    print(f"CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")


if __name__ == "__main__":
    main()

