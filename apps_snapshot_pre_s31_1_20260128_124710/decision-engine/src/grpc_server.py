"""
gRPC Server - Decision Engine
Servidor gRPC para Interface I-01 (recebe metadados do SEM-CSMF)
"""

import grpc
from concurrent import futures
import asyncio
from opentelemetry import trace

import sys
import os
# Adicionar caminho do proto ao sys.path
proto_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto', 'proto')
if proto_path not in sys.path:
    sys.path.insert(0, proto_path)

# Importar diretamente do diretório proto/proto
import i01_interface_pb2
import i01_interface_pb2_grpc
from decision_maker import DecisionMaker
from rule_engine import RuleEngine

tracer = trace.get_tracer(__name__)


class DecisionEngineService(i01_interface_pb2_grpc.DecisionEngineServiceServicer):
    """Implementação do serviço gRPC I-01"""
    
    def __init__(self):
        rule_engine = RuleEngine()
        self.decision_maker = DecisionMaker(rule_engine)
        self.decisions = {}  # Storage em memória (substituir por DB)
    
    def SendNESTMetadata(self, request, context):
        """
        Recebe metadados de NEST do SEM-CSMF via I-01
        """
        with tracer.start_as_current_span("receive_nest_metadata_grpc") as span:
            span.set_attribute("intent.id", request.intent_id)
            span.set_attribute("nest.id", request.nest_id)
            
            try:
                # Converter request para contexto de decisão
                decision_context = {
                    "intent_id": request.intent_id,
                    "nest_id": request.nest_id,
                    "tenant_id": request.tenant_id,
                    "service_type": request.service_type,
                    "sla_requirements": dict(request.sla_requirements),
                    "nest_status": request.nest_status,
                    "metadata": dict(request.metadata)
                }
                
                # Fazer decisão (síncrono em contexto gRPC)
                # Criar novo event loop para esta thread
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                decision = loop.run_until_complete(self.decision_maker.decide(decision_context))
                
                # Gerar decision_id
                decision_id = f"decision-{request.intent_id}"
                self.decisions[decision_id] = {
                    "decision_id": decision_id,
                    "intent_id": request.intent_id,
                    "decision": decision.get("action"),
                    "reason": decision.get("reason", ""),
                    "timestamp": request.timestamp,
                    "details": decision_context
                }
                
                span.set_attribute("decision.id", decision_id)
                span.set_attribute("decision.action", decision.get("action"))
                
                return i01_interface_pb2.NESTMetadataResponse(
                    success=True,
                    decision_id=decision_id,
                    message=f"Decision made: {decision.get('action')}",
                    status_code=200
                )
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                return i01_interface_pb2.NESTMetadataResponse(
                    success=False,
                    decision_id="",
                    message=f"Error: {str(e)}",
                    status_code=500
                )
    
    def GetDecisionStatus(self, request, context):
        """Retorna status de decisão"""
        with tracer.start_as_current_span("get_decision_status_grpc") as span:
            decision_id = request.decision_id
            span.set_attribute("decision.id", decision_id)
            
            decision = self.decisions.get(decision_id)
            if not decision:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Decision not found")
                return i01_interface_pb2.DecisionStatusResponse()
            
            return i01_interface_pb2.DecisionStatusResponse(
                decision_id=decision["decision_id"],
                intent_id=decision["intent_id"],
                decision=decision["decision"],
                reason=decision["reason"],
                timestamp=decision["timestamp"],
                details={k: str(v) for k, v in decision["details"].items()}
            )


def serve():
    """Inicia servidor gRPC"""
    import sys
    import logging
    import os
    import time
    
    # Configurar logging com arquivo
    log_file = os.getenv("GRPC_LOG_FILE", "/tmp/grpc_server.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_file) if os.path.exists(os.path.dirname(log_file)) or os.path.dirname(log_file) == '' else logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info("🔧 Creating gRPC server...")
        print("🔧 Creating gRPC server...", file=sys.stderr, flush=True)
        print("🔧 Creating gRPC server...", file=sys.stdout, flush=True)
        
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        i01_interface_pb2_grpc.add_DecisionEngineServiceServicer_to_server(
            DecisionEngineService(), server
        )
        
        port = os.getenv("GRPC_PORT", "50051")
        logger.info(f"🔌 Binding to port {port}...")
        print(f"🔌 Binding to port {port}...", file=sys.stderr, flush=True)
        print(f"🔌 Binding to port {port}...", file=sys.stdout, flush=True)
        
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        
        logger.info(f"✅ gRPC server started on port {port}")
        print(f"✅ gRPC server started on port {port}", file=sys.stderr, flush=True)
        print(f"✅ gRPC server started on port {port}", file=sys.stdout, flush=True)
        
        # Escrever em arquivo também
        try:
            with open(log_file, "a") as f:
                f.write(f"[{time.time()}] ✅ gRPC server started on port {port}\n")
        except Exception:
            pass
        
        # Manter servidor rodando
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("Shutting down gRPC server...")
            server.stop(0)
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor gRPC: {e}", exc_info=True)
        print(f"❌ Erro ao iniciar servidor gRPC: {e}", file=sys.stderr, flush=True)
        print(f"❌ Erro ao iniciar servidor gRPC: {e}", file=sys.stdout, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        
        # Escrever erro em arquivo
        try:
            with open(log_file, "a") as f:
                f.write(f"[{time.time()}] ❌ Erro: {e}\n")
                traceback.print_exc(file=f)
        except Exception:
            pass


if __name__ == "__main__":
    serve()

