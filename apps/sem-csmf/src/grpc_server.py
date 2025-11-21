"""
gRPC Server - SEM-CSMF
Interface I-01: Recepção de metadados via gRPC
"""

import grpc
from concurrent import futures
from opentelemetry import trace

# Protobuf definitions (gerar com protoc)
# from trisla_proto import intent_service_pb2, intent_service_pb2_grpc

tracer = trace.get_tracer(__name__)


class IntentServiceServicer:
    """Servidor gRPC para I-01"""
    
    def __init__(self, intent_processor):
        self.intent_processor = intent_processor
    
    def SendMetadata(self, request, context):
        """Recebe metadados via I-01"""
        with tracer.start_as_current_span("grpc_send_metadata") as span:
            span.set_attribute("intent.id", request.intent_id)
            
            # Processar metadados
            # Em produção, converter request para Intent e processar
            # intent = self._convert_request_to_intent(request)
            # result = await self.intent_processor.process(intent)
            
            # response = intent_service_pb2.MetadataResponse(
            #     status="accepted",
            #     message="Metadata received"
            # )
            # return response
            
            # Placeholder
            return None


def serve(port=50051):
    """Inicia servidor gRPC"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # intent_service_pb2_grpc.add_IntentServiceServicer_to_server(
    #     IntentServiceServicer(), server
    # )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"gRPC server started on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

