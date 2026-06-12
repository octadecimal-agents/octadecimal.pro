<link rel="stylesheet" href="../styles/main.css">

# Faza 11: Secret Manager Integration

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [Bitwarden Secrets Manager](../technologies/BitwardenSecretsManager.md) | [RBAC](../technologies/RBAC.md) | [HITL](../technologies/HITL.md) | [PHP → Python](../technologies/PHP-do-Python.md)

Status: draft prywatny

Cel fazy: dodać bezpieczny model dostępu do sekretów przez porty i adapter Bitwarden, bez logowania wartości sekretów.

## Główna idea

Domena nie zna Bitwardena. Application zna port:

```text
SecretProvider Protocol -> EnvSecretProvider / BitwardenSecretProvider
```

## Zakres techniczny

- `SecretProvider` port,
- fake provider,
- env provider,
- Bitwarden adapter,
- audit secret resolution,
- policy/HITL dla wysokiego ryzyka,
- testy bez realnych sekretów.

## Czego nie robimy w tej fazie

- własnego vaulta,
- przechowywania sekretów w bazie,
- logowania sekretów,
- wymuszania Bitwardena jako jedynej opcji dev.

## Checklist

- [ ] 1. Dodać `SecretProvider` Protocol.
- [ ] 2. Dodać fake provider.
- [ ] 3. Dodać env provider.
- [ ] 4. Dodać Bitwarden provider.
- [ ] 5. Dodać audit event bez wartości sekretu.
- [ ] 6. Dodać policy dla secret resolution.
- [ ] 7. Dodać test, że sekret nie trafia do logów.
- [ ] 8. Udokumentować rotację i scope tokenów.

## Referencje do PHP

### SecretProvider vs `.env`

`.env` jest wygodne w dev, ale nie jest pełną strategią sekretów.

```text
PHP:
$_ENV / Symfony secrets / Vault client

Python:
SecretProvider port + adaptery env/Bitwarden
```

```php
// PHP — proste pobranie sekretu z env
$apiKey = $_ENV['OPENAI_API_KEY'];
```

```python
# Python — use case zależy od portu, nie od env/Bitwarden
class SecretProvider(Protocol):
    def resolve(self, name: str) -> SecretValue:
        ...
```

**Implikacje dla Python:**

- Testy używają fake provider.
- Adapter Bitwarden jest wymienny.
- Audit zapisuje fakt użycia sekretu, nie jego wartość.
- Secret access może wymagać approval.

## Oczekiwany rezultat fazy

Projekt ma dojrzały wzorzec secret management, bez ryzyka wrzucania sekretów do repo, promptów albo logów.
