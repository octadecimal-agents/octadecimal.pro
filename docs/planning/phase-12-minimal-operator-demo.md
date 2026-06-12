<link rel="stylesheet" href="../styles/main.css">

# Faza 12: Minimal Operator Demo

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [FastAPI](../technologies/FastAPI.md) | [Playwright](../technologies/Playwright.md) | [React.js](../technologies/React.js.md) | [Next.js](../technologies/Next.js.md)

Status: draft prywatny

Cel fazy: dodać minimalny interfejs demonstracyjny dla approval flow, nie budować pełnego produktu frontendowego.

## Główna idea

UI jest narzędziem demo dla rekrutera i operatora:

```text
pending approvals -> approve/reject -> audit trail
```

Nie jest głównym sygnałem AI Engineer.

## Zakres techniczny

- minimal operator console,
- lista pending approvals,
- approve/reject,
- audit trail,
- trace/eval summary opcjonalnie,
- Playwright opcjonalnie.

## Czego nie robimy w tej fazie

- pełnego design systemu,
- rozbudowanego frontendu,
- auth enterprise,
- dashboardów jak w produkcyjnym SaaS.

## Checklist

- [ ] 1. Wybrać minimalną formę: Streamlit/server-rendered/simple frontend.
- [ ] 2. Dodać widok pending approvals.
- [ ] 3. Dodać approve/reject.
- [ ] 4. Dodać audit trail read-only.
- [ ] 5. Ukryć/nie pokazywać sekretów.
- [ ] 6. Dodać prosty demo script.
- [ ] 7. Playwright tylko jeśli UI jest stabilne.

## Referencje do PHP

### Operator console vs panel admina

To nie ma być pełny EasyAdmin/Nova.

```text
PHP:
Panel admina często zarządza CRUD-em całej aplikacji.

Tutaj:
Minimalny operator console pokazuje jeden krytyczny workflow.
```

```php
// PHP — klasyczny admin CRUD może szybko urosnąć
Route::resource('/admin/users', UserAdminController::class);
Route::resource('/admin/orders', OrderAdminController::class);
```

```python
# Python — demo ma obsłużyć tylko approval flow
@app.get("/operator/approvals")
async def pending_approvals() -> ApprovalListResponse:
    ...
```

**Implikacje dla projektu:**

- UI ma pokazać governance, nie zastąpić portfolio backendowego.
- Minimalizm jest zaletą.
- Demo ma być szybkie do zrozumienia w 5 minut.

## Oczekiwany rezultat fazy

Rekruter może zobaczyć flow bez curl, ale projekt nadal pozostaje AI/backend/security portfolio.
