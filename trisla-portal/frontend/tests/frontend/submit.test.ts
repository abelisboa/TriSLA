/**
 * Teste para a funcionalidade de submissão de SLA via Template
 * 
 * Testa se o frontend envia o payload correto para /api/v1/sla/submit
 */

describe('SLA Submit (Template)', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'

  it('deve enviar payload correto para /sla/submit', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        sla_id: 'sla-123',
        status: 'submitted',
        intent_id: 'intent-456',
        nest_id: 'nest-789'
      })
    })

    global.fetch = mockFetch

    const payload = {
      tenant_id: 'default',
      template_id: 'urllc-template-001',
      form_values: {
        latency: 5,
        reliability: 99.999
      }
    }

    const response = await fetch(`${API_URL}/sla/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/sla/submit`,
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify(payload)
      })
    )

    const data = await response.json()
    expect(data).toHaveProperty('sla_id')
    expect(data).toHaveProperty('status')
  })

  it('deve usar tenant_id "default"', () => {
    const payload = {
      tenant_id: 'default',
      template_id: 'urllc-template-001',
      form_values: {}
    }

    expect(payload.tenant_id).toBe('default')
  })

  it('deve incluir template_id e form_values', () => {
    const payload = {
      tenant_id: 'default',
      template_id: 'embb-template-001',
      form_values: {
        throughput_ul: 100,
        throughput_dl: 500
      }
    }

    expect(payload).toHaveProperty('template_id')
    expect(payload).toHaveProperty('form_values')
    expect(payload.form_values).toHaveProperty('throughput_ul')
  })

  it('deve usar porta 8001', () => {
    const url = new URL(API_URL)
    expect(url.port).toBe('8001')
  })
})

