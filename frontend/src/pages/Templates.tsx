import React, { useState, useEffect } from 'react'
import MainLayout from '../layout/MainLayout'
import { templatesApi } from '../services/api'

interface Template {
  id: number
  name: string
  type: string
  description?: string
  content: any
  created_at: string
  updated_at?: string
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [editMode, setEditMode] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(false)
  
  // Form state
  const [formName, setFormName] = useState<string>('')
  const [formType, setFormType] = useState<string>('GST')
  const [formDescription, setFormDescription] = useState<string>('')
  const [formContent, setFormContent] = useState<string>('')
  
  // Fetch templates
  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const response = await templatesApi.list(selectedType !== 'all' ? selectedType : undefined)
      if (response.data && response.data.templates) {
        setTemplates(response.data.templates)
      }
    } catch (error) {
      console.error('Error fetching templates:', error)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    fetchTemplates()
  }, [selectedType])
  
  // Handle template selection
  const handleSelectTemplate = (template: Template) => {
    setSelectedTemplate(template)
    setEditMode(false)
    
    // Reset form
    setFormName(template.name)
    setFormType(template.type)
    setFormDescription(template.description || '')
    setFormContent(JSON.stringify(template.content, null, 2))
  }
  
  // Create new template
  const handleCreateNew = () => {
    setSelectedTemplate(null)
    setEditMode(true)
    
    // Reset form
    setFormName('')
    setFormType('GST')
    setFormDescription('')
    setFormContent(JSON.stringify({
      serviceName: '',
      serviceType: '',
      latency: '',
      throughput: '',
      availability: '',
      domains: []
    }, null, 2))
  }
  
  // Edit selected template
  const handleEditTemplate = () => {
    if (!selectedTemplate) return
    setEditMode(true)
  }
  
  // Save template (create or update)
  const handleSaveTemplate = async () => {
    try {
      let contentObj
      try {
        contentObj = JSON.parse(formContent)
      } catch (e) {
        alert('Invalid JSON content. Please check your format.')
        return
      }
      
      const templateData = {
        name: formName,
        type: formType,
        description: formDescription,
        content: contentObj
      }
      
      if (editMode && selectedTemplate) {
        // Update existing template
        await templatesApi.update(selectedTemplate.id, templateData)
      } else {
        // Create new template
        await templatesApi.create(templateData)
      }
      
      // Refresh templates
      fetchTemplates()
      setEditMode(false)
    } catch (error) {
      console.error('Error saving template:', error)
      alert('Failed to save template. Please try again.')
    }
  }
  
  // Delete template
  const handleDeleteTemplate = async () => {
    if (!selectedTemplate) return
    
    if (confirm(`Are you sure you want to delete template "${selectedTemplate.name}"?`)) {
      try {
        await templatesApi.delete(selectedTemplate.id)
        setSelectedTemplate(null)
        fetchTemplates()
      } catch (error) {
        console.error('Error deleting template:', error)
        alert('Failed to delete template. Please try again.')
      }
    }
  }
  
  // Export template to JSON file
  const handleExportTemplate = () => {
    if (!selectedTemplate) return
    
    const dataStr = JSON.stringify(selectedTemplate, null, 2)
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`
    
    const exportFileDefaultName = `${selectedTemplate.type.toLowerCase()}_${selectedTemplate.name.toLowerCase().replace(/\s+/g, '_')}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }
  
  // Import template from JSON file
  const handleImportTemplate = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const content = e.target?.result as string
        const importedTemplate = JSON.parse(content)
        
        // Validate imported template
        if (!importedTemplate.name || !importedTemplate.type || !importedTemplate.content) {
          alert('Invalid template format. Please check your file.')
          return
        }
        
        // Create new template from imported data
        await templatesApi.create({
          name: importedTemplate.name,
          type: importedTemplate.type,
          description: importedTemplate.description || '',
          content: importedTemplate.content
        })
        
        // Refresh templates
        fetchTemplates()
      } catch (error) {
        console.error('Error importing template:', error)
        alert('Failed to import template. Please check your file format.')
      }
    }
    reader.readAsText(file)
    
    // Reset file input
    event.target.value = ''
  }
  
  // Load template to slice form
  const handleLoadToForm = () => {
    if (!selectedTemplate) return
    
    // Store template in localStorage for use in slice creation forms
    localStorage.setItem('selectedTemplate', JSON.stringify(selectedTemplate))
    
    // Redirect to appropriate slice creation page based on template type
    if (selectedTemplate.type.toUpperCase() === 'GST') {
      window.location.href = '/slices/gst'
    } else {
      window.location.href = '/slices'
    }
  }
  
  return (
    <MainLayout>
      <section id="templates">
        <h2 className="text-xl font-semibold mb-3">Templates GST/NEST</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Templates List */}
          <div className="bg-white rounded-xl shadow-soft p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">Catálogo</h3>
              <div>
                <select 
                  className="border rounded-lg p-1 text-sm mr-2"
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                >
                  <option value="all">Todos</option>
                  <option value="GST">GST</option>
                  <option value="NEST">NEST</option>
                </select>
                <button 
                  className="px-2 py-1 bg-sidebar text-white text-sm rounded-lg"
                  onClick={handleCreateNew}
                >
                  Novo
                </button>
              </div>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-gray-500">Carregando templates...</div>
            ) : templates.length === 0 ? (
              <div className="text-center py-8 text-gray-500">Nenhum template encontrado</div>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                {templates.map((template) => (
                  <div 
                    key={template.id}
                    className={`p-3 mb-2 rounded-lg cursor-pointer hover:bg-gray-50 ${selectedTemplate?.id === template.id ? 'bg-gray-100 border-l-4 border-sidebar' : ''}`}
                    onClick={() => handleSelectTemplate(template)}
                  >
                    <div className="font-medium">{template.name}</div>
                    <div className="text-xs text-gray-500 flex justify-between">
                      <span>{template.type}</span>
                      <span>{new Date(template.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Import/Export */}
            <div className="mt-4 pt-4 border-t">
              <div className="flex justify-between">
                <label className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-lg cursor-pointer">
                  Importar
                  <input 
                    type="file" 
                    accept=".json" 
                    className="hidden" 
                    onChange={handleImportTemplate} 
                  />
                </label>
                
                <button 
                  className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-lg"
                  onClick={handleExportTemplate}
                  disabled={!selectedTemplate}
                >
                  Exportar
                </button>
              </div>
            </div>
          </div>
          
          {/* Template Details/Editor */}
          <div className="bg-white rounded-xl shadow-soft p-6 md:col-span-2">
            {!selectedTemplate && !editMode ? (
              <div className="text-center py-12 text-gray-500">
                Selecione um template para visualizar ou clique em "Novo" para criar
              </div>
            ) : editMode ? (
              <div>
                <h3 className="text-lg font-medium mb-4">
                  {selectedTemplate ? 'Editar Template' : 'Novo Template'}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Nome</label>
                    <input 
                      className="w-full border rounded-lg p-2"
                      value={formName}
                      onChange={(e) => setFormName(e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Tipo</label>
                    <select 
                      className="w-full border rounded-lg p-2"
                      value={formType}
                      onChange={(e) => setFormType(e.target.value)}
                    >
                      <option value="GST">GST</option>
                      <option value="NEST">NEST</option>
                    </select>
                  </div>
                </div>
                
                <div className="mb-4">
                  <label className="block text-sm text-gray-600 mb-1">Descrição</label>
                  <input 
                    className="w-full border rounded-lg p-2"
                    value={formDescription}
                    onChange={(e) => setFormDescription(e.target.value)}
                  />
                </div>
                
                <div className="mb-4">
                  <label className="block text-sm text-gray-600 mb-1">Conteúdo (JSON)</label>
                  <textarea 
                    className="w-full border rounded-lg p-2 font-mono text-sm"
                    rows={10}
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <button 
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg"
                    onClick={() => setEditMode(false)}
                  >
                    Cancelar
                  </button>
                  <button 
                    className="px-4 py-2 bg-sidebar text-white rounded-lg"
                    onClick={handleSaveTemplate}
                  >
                    Salvar
                  </button>
                </div>
              </div>
            ) : selectedTemplate && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium">{selectedTemplate.name}</h3>
                  <div className="space-x-2">
                    <button 
                      className="px-3 py-1 bg-sidebar text-white text-sm rounded-lg"
                      onClick={handleLoadToForm}
                    >
                      Carregar no Formulário
                    </button>
                    <button 
                      className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-lg"
                      onClick={handleEditTemplate}
                    >
                      Editar
                    </button>
                    <button 
                      className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-lg"
                      onClick={handleDeleteTemplate}
                    >
                      Excluir
                    </button>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm text-gray-600">Tipo</div>
                  <div className="font-medium">{selectedTemplate.type}</div>
                </div>
                
                {selectedTemplate.description && (
                  <div className="mb-4">
                    <div className="text-sm text-gray-600">Descrição</div>
                    <div>{selectedTemplate.description}</div>
                  </div>
                )}
                
                <div>
                  <div className="text-sm text-gray-600 mb-1">Conteúdo</div>
                  <pre className="bg-gray-50 p-3 rounded-lg overflow-auto text-sm max-h-80">
                    {JSON.stringify(selectedTemplate.content, null, 2)}
                  </pre>
                </div>
                
                <div className="mt-4 text-xs text-gray-500">
                  Criado em: {new Date(selectedTemplate.created_at).toLocaleString()}
                  {selectedTemplate.updated_at && (
                    <span> | Atualizado em: {new Date(selectedTemplate.updated_at).toLocaleString()}</span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </MainLayout>
  )
}
