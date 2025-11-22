"""
Dataset Generator - ML-NSMF
Gera dataset sintético parametrizado pela ontologia TriSLA para treinamento do modelo ML
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import os
import sys
from datetime import datetime, timedelta
import json

# Adicionar path para acessar ontologia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../sem-csmf/src"))
from owlready2 import get_ontology

class DatasetGenerator:
    """Gera dataset sintético baseado na ontologia TriSLA e métricas do NASP"""
    
    def __init__(self, ontology_path: str = None):
        """
        Inicializa gerador de dataset
        
        Args:
            ontology_path: Caminho para a ontologia OWL (opcional)
        """
        self.ontology_path = ontology_path or os.path.join(
            os.path.dirname(__file__),
            "../../../sem-csmf/src/ontology/trisla.owl"
        )
        self.ontology = self._load_ontology()
        
        # Ranges baseados na ontologia (extraídos de trisla.owl)
        self.slice_ranges = {
            "URLLC": {
                "latency": (1, 10),  # ms
                "throughput": (1, 100),  # Mbps
                "reliability": (0.99999, 0.999999),
                "jitter": (0.1, 1.0),  # ms
                "packet_loss": (1e-6, 1e-5)
            },
            "eMBB": {
                "latency": (10, 50),  # ms
                "throughput": (100, 1000),  # Mbps
                "reliability": (0.99, 0.999),
                "jitter": (1.0, 10.0),  # ms
                "packet_loss": (1e-5, 1e-4)
            },
            "mMTC": {
                "latency": (100, 1000),  # ms
                "throughput": (0.00016, 1.0),  # Mbps (160bps a 1Mbps)
                "reliability": (0.9, 0.99),
                "jitter": (10.0, 100.0),  # ms
                "packet_loss": (1e-4, 1e-3)
            }
        }
    
    def _load_ontology(self):
        """Carrega ontologia OWL"""
        try:
            if os.path.exists(self.ontology_path):
                onto = get_ontology(f"file://{self.ontology_path}").load()
                print(f"✅ Ontologia carregada: {onto.base_iri}")
                return onto
            else:
                print(f"⚠️ Ontologia não encontrada em {self.ontology_path}, usando ranges padrão")
                return None
        except Exception as e:
            print(f"⚠️ Erro ao carregar ontologia: {e}, usando ranges padrão")
            return None
    
    def generate_synthetic_metrics(
        self,
        slice_type: str,
        n_samples: int = 1000,
        noise_level: float = 0.1
    ) -> pd.DataFrame:
        """
        Gera métricas sintéticas baseadas nos ranges da ontologia
        
        Args:
            slice_type: Tipo de slice (URLLC, eMBB, mMTC)
            n_samples: Número de amostras a gerar
            noise_level: Nível de ruído (0-1)
        
        Returns:
            DataFrame com métricas sintéticas
        """
        if slice_type not in self.slice_ranges:
            raise ValueError(f"Tipo de slice inválido: {slice_type}")
        
        ranges = self.slice_ranges[slice_type]
        data = []
        
        for i in range(n_samples):
            # Gerar métricas dentro dos ranges da ontologia
            latency = np.random.uniform(*ranges["latency"])
            throughput = np.random.uniform(*ranges["throughput"])
            reliability = np.random.uniform(*ranges["reliability"])
            jitter = np.random.uniform(*ranges["jitter"])
            packet_loss = np.random.uniform(*ranges["packet_loss"])
            
            # Adicionar ruído
            latency += np.random.normal(0, latency * noise_level)
            throughput += np.random.normal(0, throughput * noise_level)
            reliability += np.random.normal(0, reliability * noise_level)
            jitter += np.random.normal(0, jitter * noise_level)
            packet_loss += np.random.normal(0, packet_loss * noise_level)
            
            # Garantir que valores estão dentro dos ranges
            latency = np.clip(latency, ranges["latency"][0], ranges["latency"][1])
            throughput = np.clip(throughput, ranges["throughput"][0], ranges["throughput"][1])
            reliability = np.clip(reliability, ranges["reliability"][0], ranges["reliability"][1])
            jitter = np.clip(jitter, ranges["jitter"][0], ranges["jitter"][1])
            packet_loss = np.clip(packet_loss, ranges["packet_loss"][0], ranges["packet_loss"][1])
            
            # Calcular viabilidade baseada em regras heurísticas
            # Viabilidade = função de quão bem as métricas atendem aos requisitos
            viability_score = self._calculate_viability(
                latency, throughput, reliability, jitter, packet_loss, slice_type
            )
            
            data.append({
                "slice_type": slice_type,
                "latency": latency,
                "throughput": throughput,
                "reliability": reliability,
                "jitter": jitter,
                "packet_loss": packet_loss,
                "viability_score": viability_score,
                "timestamp": datetime.utcnow() - timedelta(days=np.random.randint(0, 365))
            })
        
        return pd.DataFrame(data)
    
    def _calculate_viability(
        self,
        latency: float,
        throughput: float,
        reliability: float,
        jitter: float,
        packet_loss: float,
        slice_type: str
    ) -> float:
        """
        Calcula score de viabilidade baseado em regras heurísticas
        (Em produção, isso seria aprendido pelo modelo ML)
        """
        ranges = self.slice_ranges[slice_type]
        
        # Normalizar métricas (0-1, onde 1 é melhor)
        latency_norm = 1.0 - (latency - ranges["latency"][0]) / (ranges["latency"][1] - ranges["latency"][0])
        throughput_norm = (throughput - ranges["throughput"][0]) / (ranges["throughput"][1] - ranges["throughput"][0])
        reliability_norm = (reliability - ranges["reliability"][0]) / (ranges["reliability"][1] - ranges["reliability"][0])
        jitter_norm = 1.0 - (jitter - ranges["jitter"][0]) / (ranges["jitter"][1] - ranges["jitter"][0])
        packet_loss_norm = 1.0 - (packet_loss - ranges["packet_loss"][0]) / (ranges["packet_loss"][1] - ranges["packet_loss"][0])
        
        # Pesos baseados no tipo de slice
        if slice_type == "URLLC":
            weights = {"latency": 0.4, "reliability": 0.3, "jitter": 0.15, "packet_loss": 0.1, "throughput": 0.05}
        elif slice_type == "eMBB":
            weights = {"throughput": 0.4, "latency": 0.2, "reliability": 0.2, "jitter": 0.1, "packet_loss": 0.1}
        else:  # mMTC
            weights = {"reliability": 0.3, "packet_loss": 0.2, "throughput": 0.2, "latency": 0.15, "jitter": 0.15}
        
        # Calcular score ponderado
        viability = (
            weights["latency"] * latency_norm +
            weights["throughput"] * throughput_norm +
            weights["reliability"] * reliability_norm +
            weights["jitter"] * jitter_norm +
            weights["packet_loss"] * packet_loss_norm
        )
        
        # Adicionar ruído para simular variação real
        viability += np.random.normal(0, 0.05)
        
        return np.clip(viability, 0.0, 1.0)
    
    def generate_full_dataset(
        self,
        n_samples_per_type: int = 1000,
        output_path: str = None
    ) -> pd.DataFrame:
        """
        Gera dataset completo com todos os tipos de slice
        
        Args:
            n_samples_per_type: Número de amostras por tipo de slice
            output_path: Caminho para salvar dataset (opcional)
        
        Returns:
            DataFrame completo
        """
        print("🔄 Gerando dataset sintético parametrizado pela ontologia...")
        
        datasets = []
        for slice_type in ["URLLC", "eMBB", "mMTC"]:
            print(f"  📊 Gerando {n_samples_per_type} amostras para {slice_type}...")
            df = self.generate_synthetic_metrics(slice_type, n_samples_per_type)
            datasets.append(df)
        
        full_dataset = pd.concat(datasets, ignore_index=True)
        
        # Adicionar features derivadas
        full_dataset["latency_throughput_ratio"] = full_dataset["latency"] / (full_dataset["throughput"] + 1e-6)
        full_dataset["reliability_packet_loss_ratio"] = full_dataset["reliability"] / (full_dataset["packet_loss"] + 1e-9)
        full_dataset["jitter_latency_ratio"] = full_dataset["jitter"] / (full_dataset["latency"] + 1e-6)
        
        # Codificar slice_type
        full_dataset["slice_type_encoded"] = full_dataset["slice_type"].map({
            "URLLC": 0,
            "eMBB": 1,
            "mMTC": 2
        })
        
        if output_path:
            full_dataset.to_csv(output_path, index=False)
            print(f"✅ Dataset salvo em: {output_path}")
        
        print(f"✅ Dataset completo gerado: {len(full_dataset)} amostras")
        return full_dataset


if __name__ == "__main__":
    # Gerar dataset para treinamento
    generator = DatasetGenerator()
    
    output_dir = os.path.join(os.path.dirname(__file__), "../data/datasets")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "trisla_ml_dataset.csv")
    dataset = generator.generate_full_dataset(n_samples_per_type=2000, output_path=output_path)
    
    print(f"\n📊 Estatísticas do Dataset:")
    print(dataset.describe())
    print(f"\n📈 Distribuição por tipo de slice:")
    print(dataset["slice_type"].value_counts())


