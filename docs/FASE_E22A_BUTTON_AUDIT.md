# FASE E.2.2A — Auditoria estrutural do clique real no Menu 3

**Data:** 2026-03-17  
**Objetivo:** Descobrir por que o botão "Generate SLA Template" não dispara nada. Provar que o clique chega ao componente certo. Sem alterar backend, endpoint; sem build.

---

## Regra absoluta

- Não alterar backend.
- Não alterar endpoint.
- Não buildar ainda.
- Primeiro provar que o clique chega ao componente certo.

---

## 1. Alterações temporárias em `TemplateSlaSection.tsx`

### 1.1 Marcador visual acima do botão

Inserido **acima** do botão "Generate SLA Template":

```tsx
<div style={{ color: 'red', marginBottom: '12px' }}>
  TEMPLATE VERSION E21
</div>
```

**Validação A:** O marcador vermelho "TEMPLATE VERSION E21" aparece?
- **Se NÃO:** o frontend está carregando versão antiga (cache, build antigo ou rota errada).
- **Se SIM:** o componente renderizado é o atual (TemplateSlaSection com estas alterações).

### 1.2 Botão com log explícito no onClick

Alterado de:

```tsx
onClick={handleSubmit}
```

para:

```tsx
onClick={() => {
  console.log('BUTTON CLICK OK');
  handleSubmit();
}}
```

**Validação B:** Ao clicar no botão, aparece no console do browser "BUTTON CLICK OK"?
- **Se NÃO:** o botão não está ligado corretamente (outro componente, evento bloqueado, ou elemento não clicável).
- **Se SIM:** o clique está sendo tratado pelo componente correto.

**Validação C:** Se aparece "BUTTON CLICK OK", em seguida verificar no console:
- `SUBMIT PAYLOAD` (payload enviado),
- `SUBMIT RESPONSE` (resposta do submit),
- ou `SUBMIT ERROR` (erro na chamada).

---

## 2. Diff completo aplicado (antes de salvar)

```diff
          />

+         <div style={{ color: 'red', marginBottom: '12px' }}>
+           TEMPLATE VERSION E21
+         </div>
+
          <button
            type="button"
-           onClick={handleSubmit}
+           onClick={() => {
+             console.log('BUTTON CLICK OK');
+             handleSubmit();
+           }}
            disabled={loading}
```

---

## 3. Roteamento — "Criar SLA Template" usa exatamente `TemplateSlaSection.tsx`

**Arquivo:** `apps/portal-frontend/app/page.tsx` (App de roteamento da página principal).

- **Import:** `import TemplateSlaSection from '../src/sections/TemplateSlaSection';`
- **Estado:** `const [selected, setSelected] = useState('Home');`
- **Render condicional:** `renderSection()` com `switch (selected)`:
  - `case 'Criar SLA Template': return <TemplateSlaSection />;`
- **Sidebar:** `Sidebar` recebe `selected` e `onSelect={setSelected}`; ao clicar em um item do menu, `setSelected` atualiza e `renderSection()` re-renderiza. O item com label **"Criar SLA Template"** está definido em `Sidebar.tsx` na lista de opções.

**Conclusão:** "Criar SLA Template" usa **exatamente** `TemplateSlaSection.tsx`. Não há `App.tsx` separado; o ponto de entrada da página é `app/page.tsx`, que importa e renderiza `TemplateSlaSection` quando `selected === 'Criar SLA Template'`.

---

## 4. Passos de validação (executar frontend local)

1. Executar o frontend em modo desenvolvimento (ex.: `npm run dev` na raiz do portal-frontend).
2. Abrir a aplicação no browser e, na sidebar, clicar em **"Criar SLA Template"**.
3. **A)** Verificar se o texto vermelho **"TEMPLATE VERSION E21"** aparece acima do botão.
4. **B)** Abrir o console (F12 → Console), clicar em **"Generate SLA Template"** e verificar se aparece **"BUTTON CLICK OK"**.
5. **C)** Se **BUTTON CLICK OK** aparecer, verificar a sequência: **SUBMIT PAYLOAD** → **SUBMIT RESPONSE** ou **SUBMIT ERROR**.

Somente após identificar o resultado (marcador sim/não, clique sim/não, e sequência de logs), seguir para a correção final.
