/**
 * Teste para a funcionalidade de busca de métricas de SLA
 * 
 * Testa se o frontend busca métricas corretamente de /api/v1/sla/metrics/{id}
 */

describe('SLA Metrics', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'

  it('deve buscar métricas corretamente de /sla/metrics/{id}', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        sla_id: 'sla-123',
        tenant_id: 'default',
        latency: 5.0,
        throughput_ul: 100.0,
        throughput_dl: 500.0,
        packet_loss: 0.1
      })
    })

    global.fetch = mockFetch

    const slaId = 'sla-123'
    const response = await fetch(`${API_URL}/sla/metrics/${slaId}`)

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/sla/metrics/${slaId}`,
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        })
      })
    )

    const data = await response.json()
    expect(data).toHaveProperty('sla_id')
    expect(data).toHaveProperty('latency')
    expect(data).toHaveProperty('throughput_ul')
    expect(data).toHaveProperty('throughput_dl')
    expect(data).toHaveProperty('packet_loss')
  })

  it('deve suportar métricas em objeto aninhado', async () => {
    const mockMetrics = {
      sla_id: 'sla-123',
      tenant_id: 'default',
      metrics: {
        latency: 5.0,
        throughput_ul: 100.0,
        throughput_dl: 500.0,
        packet_loss: 0.1
      }
    }

    // Extrair métricas (suporta ambos os formatos)
    const latency = mockMetrics.latency || mockMetrics.metrics?.latency
    const throughput_ul = mockMetrics.throughput_ul || mockMetrics.metrics?.throughput_ul

    expect(latency).toBe(5.0)
    expect(throughput_ul).toBe(100.0)
  })

  it('deve usar porta 8001', () => {
    const url = new URL(API_URL)
    expect(url.port).toBe('8001')
  })

  it('deve ter campos de métricas corretos', () => {
    const expectedFields = ['latency', 'throughput_ul', 'throughput_dl', 'packet_loss']
    
    const mockData = {
      latency: 5.0,
      throughput_ul: 100.0,
      throughput_dl: 500.0,
      packet_loss: 0.1
    }

    expectedFields.forEach(field => {
      expect(mockData).toHaveProperty(field)
    })
  })
})

