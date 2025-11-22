"""
Training Pipeline - ML-NSMF
Pipeline completo de treinamento do modelo de ML para previsão de viabilidade
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
from datetime import datetime

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataset_generator import DatasetGenerator

class ModelTrainer:
    """Pipeline de treinamento do modelo ML"""
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Inicializa trainer
        
        Args:
            model_type: Tipo de modelo ("random_forest" ou "gradient_boosting")
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            "latency", "throughput", "reliability", "jitter", "packet_loss",
            "latency_throughput_ratio", "reliability_packet_loss_ratio",
            "jitter_latency_ratio", "slice_type_encoded"
        ]
        self.training_history = {}
    
    def load_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Carrega dataset de treinamento"""
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset não encontrado: {dataset_path}")
        
        df = pd.read_csv(dataset_path)
        print(f"✅ Dataset carregado: {len(df)} amostras")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """
        Prepara features e target para treinamento
        
        Returns:
            (X, y) - Features e target
        """
        # Selecionar features
        X = df[self.feature_columns].copy()
        y = df["viability_score"].copy()
        
        # Verificar valores faltantes
        if X.isnull().any().any():
            print("⚠️ Valores faltantes detectados, preenchendo com média...")
            X = X.fillna(X.mean())
        
        print(f"✅ Features preparadas: {X.shape}")
        print(f"✅ Target preparado: {y.shape}")
        
        return X, y
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """
        Treina o modelo
        
        Args:
            X: Features
            y: Target (viability_score)
            test_size: Proporção de dados de teste
        """
        print(f"\n🔄 Iniciando treinamento do modelo {self.model_type}...")
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=None
        )
        
        print(f"  📊 Treino: {len(X_train)} amostras")
        print(f"  📊 Teste: {len(X_test)} amostras")
        
        # Normalizar features
        print("  🔄 Normalizando features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Criar modelo
        if self.model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Tipo de modelo inválido: {self.model_type}")
        
        # Treinar
        print(f"  🔄 Treinando modelo...")
        self.model.fit(X_train_scaled, y_train)
        
        # Avaliar
        print(f"  📊 Avaliando modelo...")
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, cv=5, scoring='r2'
        )
        
        self.training_history = {
            "model_type": self.model_type,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_mse": float(train_mse),
            "test_mse": float(test_mse),
            "train_mae": float(train_mae),
            "test_mae": float(test_mae),
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "feature_importance": dict(zip(
                self.feature_columns,
                self.model.feature_importances_.tolist()
            )),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        print(f"\n✅ Treinamento concluído!")
        print(f"  📊 Train R²: {train_r2:.4f}")
        print(f"  📊 Test R²: {test_r2:.4f}")
        print(f"  📊 Test MAE: {test_mae:.4f}")
        print(f"  📊 CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        return self.training_history
    
    def save_model(self, model_dir: str = None):
        """
        Salva modelo e scaler
        
        Args:
            model_dir: Diretório para salvar (padrão: ../models)
        """
        if self.model is None:
            raise ValueError("Modelo não treinado. Execute train() primeiro.")
        
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), "../models")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # Salvar modelo
        model_path = os.path.join(model_dir, "viability_model.pkl")
        joblib.dump(self.model, model_path)
        print(f"✅ Modelo salvo em: {model_path}")
        
        # Salvar scaler
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        print(f"✅ Scaler salvo em: {scaler_path}")
        
        # Salvar metadados
        metadata_path = os.path.join(model_dir, "model_metadata.json")
        metadata = {
            "model_type": self.model_type,
            "feature_columns": self.feature_columns,
            "training_history": self.training_history,
            "model_path": "viability_model.pkl",
            "scaler_path": "scaler.pkl"
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadados salvos em: {metadata_path}")
        
        return {
            "model_path": model_path,
            "scaler_path": scaler_path,
            "metadata_path": metadata_path
        }


if __name__ == "__main__":
    # Pipeline completo de treinamento
    print("=" * 60)
    print("TRI-SLA ML-NSMF - Pipeline de Treinamento")
    print("=" * 60)
    
    # 1. Gerar dataset se não existir
    dataset_path = os.path.join(
        os.path.dirname(__file__),
        "../data/datasets/trisla_ml_dataset.csv"
    )
    
    if not os.path.exists(dataset_path):
        print("\n📊 Dataset não encontrado, gerando...")
        generator = DatasetGenerator()
        dataset = generator.generate_full_dataset(
            n_samples_per_type=2000,
            output_path=dataset_path
        )
    else:
        print(f"\n✅ Dataset encontrado: {dataset_path}")
    
    # 2. Carregar dataset
    trainer = ModelTrainer(model_type="random_forest")
    df = trainer.load_dataset(dataset_path)
    
    # 3. Preparar features
    X, y = trainer.prepare_features(df)
    
    # 4. Treinar modelo
    history = trainer.train(X, y, test_size=0.2)
    
    # 5. Salvar modelo
    saved_paths = trainer.save_model()
    
    print("\n" + "=" * 60)
    print("✅ Pipeline de treinamento concluído com sucesso!")
    print("=" * 60)


