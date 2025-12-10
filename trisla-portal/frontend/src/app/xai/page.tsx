'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { XAIExplanation } from '@/types'
import { Brain, BarChart3 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function XAIPage() {
  const [explanations, setExplanations] = useState<XAIExplanation[]>([])
  const [selectedExplanation, setSelectedExplanation] = useState<XAIExplanation | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchExplanations()
  }, [])

  const fetchExplanations = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getXAIExplanations()
      setExplanations(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const chartData = selectedExplanation
    ? Object.entries(selectedExplanation.features_importance).map(([name, value]) => ({
        name,
        value: value * 100,
      }))
    : []

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardContent className="p-6">
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Erro</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Brain className="h-8 w-8" />
          XAI Viewer
        </h1>
        <p className="text-muted-foreground">
          Visualizador de explicações de IA (Explainable AI)
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Explicações Disponíveis</CardTitle>
            <CardDescription>
              Selecione uma explicação para visualizar
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {explanations.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  Nenhuma explicação disponível
                </div>
              ) : (
                explanations.map((explanation) => (
                  <div
                    key={explanation.explanation_id}
                    className={`p-3 border rounded cursor-pointer transition-colors ${
                      selectedExplanation?.explanation_id === explanation.explanation_id
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                    }`}
                    onClick={() => setSelectedExplanation(explanation)}
                  >
                    <div className="font-semibold">
                      {explanation.type === 'ml_prediction' ? 'Predição ML' : 'Decisão'}
                    </div>
                    <div className="text-sm opacity-80">
                      {explanation.explanation_id.slice(0, 8)}...
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Detalhes da Explicação</CardTitle>
            <CardDescription>
              Explicação detalhada e visualização
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedExplanation ? (
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground">Método</div>
                  <div className="font-semibold">{selectedExplanation.method}</div>
                </div>
                {selectedExplanation.viability_score !== undefined && (
                  <div>
                    <div className="text-sm text-muted-foreground">Score de Viabilidade</div>
                    <div className="font-semibold">
                      {(selectedExplanation.viability_score * 100).toFixed(2)}%
                    </div>
                  </div>
                )}
                {selectedExplanation.recommendation && (
                  <div>
                    <div className="text-sm text-muted-foreground">Recomendação</div>
                    <div className="font-semibold">{selectedExplanation.recommendation}</div>
                  </div>
                )}
                <div>
                  <div className="text-sm text-muted-foreground mb-2">Raciocínio</div>
                  <div className="p-3 bg-muted rounded text-sm">
                    {selectedExplanation.reasoning}
                  </div>
                </div>
                {chartData.length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                      <BarChart3 className="h-4 w-4" />
                      Feature Importance
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="hsl(var(--primary))" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                Selecione uma explicação para visualizar
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}







