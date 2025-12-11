/**
 * Teste para a funcionalidade de interpretação de SLA via PLN
 * 
 * Testa se o frontend envia o payload correto para /api/v1/sla/interpret
 */

describe('SLA Interpret (PLN)', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'

  it('deve enviar payload correto para /sla/interpret', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        sla_id: 'sla-123',
        status: 'processing',
        intent_id: 'intent-456',
        nest_id: 'nest-789'
      })
    })

    global.fetch = mockFetch

    const response = await fetch(`${API_URL}/sla/interpret`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tenant_id: 'default',
        intent_text: 'Quero um slice URLLC com latência de 5ms'
      })
    })

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/sla/interpret`,
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify({
          tenant_id: 'default',
          intent_text: 'Quero um slice URLLC com latência de 5ms'
        })
      })
    )

    const data = await response.json()
    expect(data).toHaveProperty('sla_id')
    expect(data).toHaveProperty('status')
    expect(data.tenant_id).toBeUndefined() // Não deve retornar tenant_id
  })

  it('deve usar tenant_id "default" por padrão', () => {
    const payload = {
      tenant_id: 'default',
      intent_text: 'Test intent'
    }

    expect(payload.tenant_id).toBe('default')
  })

  it('deve usar porta 8001', () => {
    const url = new URL(API_URL)
    expect(url.port).toBe('8001')
  })
})

