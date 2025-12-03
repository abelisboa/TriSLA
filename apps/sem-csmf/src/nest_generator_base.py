"""
NEST Generator Base - SEM-CSMF
Lógica compartilhada para geração de NEST (remove duplicidades)
"""

from typing import Dict, Any
from models.nest import NetworkSlice, NetworkSliceStatus


class NESTGeneratorBase:
    """Classe base com lógica compartilhada para geração de NEST"""
    
    def _generate_network_slices(self, gst: Dict[str, Any]) -> list[NetworkSlice]:
        """Gera network slices baseado no template GST (lógica compartilhada)"""
        slices = []
        template = gst.get("template", {})
        slice_type = template.get("slice_type", "eMBB")
        
        # Gerar slice principal
        main_slice = NetworkSlice(
            slice_id=f"slice-{gst['intent_id']}-001",
            slice_type=slice_type,
            resources=self._calculate_resources(template),
            status=NetworkSliceStatus.GENERATED,
            metadata={"primary": True}
        )
        slices.append(main_slice)
        
        # Gerar slices adicionais se necessário
        if slice_type == "URLLC":
            # URLLC pode ter slices redundantes
            redundant_slice = NetworkSlice(
                slice_id=f"slice-{gst['intent_id']}-002",
                slice_type=slice_type,
                resources=self._calculate_resources(template),
                status=NetworkSliceStatus.GENERATED,
                metadata={"redundant": True}
            )
            slices.append(redundant_slice)
        
        return slices
    
    def _calculate_resources(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula recursos necessários baseado no template
        Inclui mapeamento completo de atributos 3GPP TS 28.541
        """
        resources = {
            "cpu": "2",
            "memory": "4Gi",
            "storage": "10Gi"
        }
        
        slice_type = template.get("slice_type")
        qos = template.get("qos", {})
        sla = template.get("sla", {})
        
        # Mapeamento 3GPP TS 28.541 - QoS Characteristics
        qos_characteristics = {
            "priorityLevel": self._get_priority_level(slice_type),
            "packetDelayBudget": self._get_packet_delay_budget(slice_type, qos, sla),
            "packetErrorRate": self._get_packet_error_rate(slice_type, qos, sla),
            "guaranteedBitRate": self._get_guaranteed_bitrate(slice_type, qos, sla),
            "maximumBitRate": self._get_maximum_bitrate(slice_type, qos, sla)
        }
        
        # Mapeamento 3GPP TS 28.541 - Slice Profile
        slice_profile = {
            "plmnId": template.get("plmn_id", "001-01"),  # Default PLMN
            "sNSSAI": self._generate_snssai(slice_type, template),
            "maxNumberOfUEs": self._get_max_number_of_ues(slice_type, template),
            "maxDataRatePerUE": self._get_max_data_rate_per_ue(slice_type, qos, sla)
        }
        
        # Mapeamento 3GPP TS 28.541 - Coverage Area
        coverage_area = {
            "areaType": template.get("coverage", {}).get("area_type", "Urban"),
            "geographicCoordinates": template.get("coverage", {}).get("coordinates", "")
        }
        
        # Ajustar recursos baseado no tipo de slice
        if slice_type == "eMBB":
            resources.update({
                "bandwidth": qos.get("maximum_bitrate", "1Gbps"),
                "cpu": "4",
                "memory": "8Gi",
                "qosCharacteristics": qos_characteristics,
                "sliceProfile": slice_profile,
                "coverageArea": coverage_area
            })
        elif slice_type == "URLLC":
            resources.update({
                "latency": qos.get("latency", "1ms"),
                "reliability": qos.get("reliability", "0.99999"),
                "cpu": "2",
                "memory": "4Gi",
                "qosCharacteristics": qos_characteristics,
                "sliceProfile": slice_profile,
                "coverageArea": coverage_area
            })
        elif slice_type == "mMTC":
            resources.update({
                "device_density": qos.get("device_density", "1000000/km²"),
                "data_rate": qos.get("data_rate", "160bps"),
                "cpu": "1",
                "memory": "2Gi",
                "qosCharacteristics": qos_characteristics,
                "sliceProfile": slice_profile,
                "coverageArea": coverage_area
            })
        else:
            # Fallback para tipo desconhecido
            resources.update({
                "qosCharacteristics": qos_characteristics,
                "sliceProfile": slice_profile,
                "coverageArea": coverage_area
            })
        
        return resources
    
    def _get_priority_level(self, slice_type: str) -> int:
        """Retorna priority level conforme 3GPP (1-8)"""
        priority_map = {
            "URLLC": 1,  # Highest priority
            "eMBB": 6,
            "mMTC": 8   # Lowest priority
        }
        return priority_map.get(slice_type, 6)
    
    def _get_packet_delay_budget(self, slice_type: str, qos: Dict, sla: Dict) -> int:
        """Retorna Packet Delay Budget em ms conforme 3GPP"""
        if "latency" in qos:
            latency_str = str(qos["latency"]).replace("ms", "").strip()
            try:
                return int(float(latency_str))
            except (ValueError, TypeError):
                pass
        
        # Valores padrão conforme 3GPP
        default_map = {
            "URLLC": 10,
            "eMBB": 50,
            "mMTC": 1000
        }
        return default_map.get(slice_type, 50)
    
    def _get_packet_error_rate(self, slice_type: str, qos: Dict, sla: Dict) -> float:
        """Retorna Packet Error Rate (0-1) conforme 3GPP"""
        if "reliability" in qos:
            reliability = float(qos["reliability"])
            return 1.0 - reliability
        
        # Valores padrão conforme 3GPP
        default_map = {
            "URLLC": 0.000001,  # 99.9999% reliability
            "eMBB": 0.0001,     # 99.99% reliability
            "mMTC": 0.01        # 99% reliability
        }
        return default_map.get(slice_type, 0.0001)
    
    def _get_guaranteed_bitrate(self, slice_type: str, qos: Dict, sla: Dict) -> float:
        """Retorna Guaranteed Bit Rate em Mbps conforme 3GPP"""
        if "guaranteed_bitrate" in qos:
            gbr_str = str(qos["guaranteed_bitrate"]).upper()
            if "GBPS" in gbr_str:
                return float(gbr_str.replace("GBPS", "").strip()) * 1000
            elif "MBPS" in gbr_str:
                return float(gbr_str.replace("MBPS", "").strip())
            else:
                try:
                    return float(gbr_str)
                except (ValueError, TypeError):
                    pass
        
        # Valores padrão conforme 3GPP
        default_map = {
            "URLLC": 10.0,
            "eMBB": 100.0,
            "mMTC": 0.1
        }
        return default_map.get(slice_type, 100.0)
    
    def _get_maximum_bitrate(self, slice_type: str, qos: Dict, sla: Dict) -> float:
        """Retorna Maximum Bit Rate em Mbps conforme 3GPP"""
        if "maximum_bitrate" in qos:
            mbr_str = str(qos["maximum_bitrate"]).upper()
            if "GBPS" in mbr_str:
                return float(mbr_str.replace("GBPS", "").strip()) * 1000
            elif "MBPS" in mbr_str:
                return float(mbr_str.replace("MBPS", "").strip())
            else:
                try:
                    return float(mbr_str)
                except (ValueError, TypeError):
                    pass
        
        # Valores padrão conforme 3GPP
        default_map = {
            "URLLC": 100.0,
            "eMBB": 1000.0,
            "mMTC": 1.0
        }
        return default_map.get(slice_type, 1000.0)
    
    def _generate_snssai(self, slice_type: str, template: Dict) -> str:
        """Gera sNSSAI (Single Network Slice Selection Assistance Information)"""
        # SST (Slice/Service Type): 1=eMBB, 2=URLLC, 3=mMTC
        sst_map = {
            "eMBB": "1",
            "URLLC": "2",
            "mMTC": "3"
        }
        sst = sst_map.get(slice_type, "1")
        
        # SD (Slice Differentiator) - opcional, pode vir do template
        sd = template.get("slice_differentiator", "000001")
        
        return f"{sst}-{sd}"
    
    def _get_max_number_of_ues(self, slice_type: str, template: Dict) -> int:
        """Retorna número máximo de UEs conforme 3GPP"""
        if "max_ues" in template:
            return int(template["max_ues"])
        
        # Valores padrão conforme tipo de slice
        default_map = {
            "URLLC": 1000,
            "eMBB": 10000,
            "mMTC": 1000000
        }
        return default_map.get(slice_type, 10000)
    
    def _get_max_data_rate_per_ue(self, slice_type: str, qos: Dict, sla: Dict) -> float:
        """Retorna taxa máxima de dados por UE em Mbps conforme 3GPP"""
        if "max_data_rate_per_ue" in qos:
            mdr_str = str(qos["max_data_rate_per_ue"]).upper()
            if "GBPS" in mdr_str:
                return float(mdr_str.replace("GBPS", "").strip()) * 1000
            elif "MBPS" in mdr_str:
                return float(mdr_str.replace("MBPS", "").strip())
            else:
                try:
                    return float(mdr_str)
                except (ValueError, TypeError):
                    pass
        
        # Valores padrão conforme 3GPP
        default_map = {
            "URLLC": 10.0,
            "eMBB": 100.0,
            "mMTC": 0.1
        }
        return default_map.get(slice_type, 100.0)
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual em ISO format"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

